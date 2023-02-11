from __future__ import annotations

import logging
from enum import StrEnum
import requests

from common import get_invalid_person_tag
from src.Common.errors import MangaNotFoundError
from src.DynamicLibController.models.IMetadataSource import IMetadataSource
from common.models import ComicInfo
from src.Settings.SettingControl import SettingControl
from src.Settings.SettingControlType import SettingControlType
from src.Settings.SettingSection import SettingSection
from src.Settings.Settings import Settings


class AniListPerson(StrEnum):
    OriginalStory = "original_story",
    CharacterDesign = "character_design",
    StoryAndArt = "story_and_art",


class AniList(IMetadataSource):
    name = "AniList"
    _log = logging.getLogger()
    # Map the Role from API to the ComicInfo tags to write
    person_mapper = {
        "Writer": [
            "Writer"
        ],
        "Character Design": [
            "Penciller"
        ],
        "Story & Art": [
            "Writer",
            "Penciller",
            "Inker",
            "CoverArtist"
        ]
    }

    def __init__(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl(AniListPerson.OriginalStory, "Original Story", SettingControlType.Text, "Writer",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.CharacterDesign, "Character Design", SettingControlType.Text, "Penciller",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.StoryAndArt, "Story & Art", SettingControlType.Text,
                               "Writer, Penciller, Inker, CoverArtist",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
            ])
        ]

        super(AniList, self).__init__()

    def save_settings(self):
        self.person_mapper[AniListPerson.OriginalStory] = Settings().get(self.name, AniListPerson.OriginalStory).split(
            ',')
        self.person_mapper[AniListPerson.CharacterDesign] = Settings().get(self.name,
                                                                           AniListPerson.CharacterDesign).split(',')
        self.person_mapper[AniListPerson.StoryAndArt] = Settings().get(self.name, AniListPerson.StoryAndArt).split(',')

    @staticmethod
    def is_valid_person_tag(key, value):
        invalid_people = get_invalid_person_tag(value)

        if len(invalid_people) == 0:
            return ""
        return ", ".join(invalid_people) + " are not a valid tags"

    @staticmethod
    def trim(value):
        ret = value.strip()
        if ret.endswith(','):
            return ret[0:-1]
        return ret

    @classmethod
    def get_cinfo(cls, partial_comic_info) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = cls._search_for_manga_title_by_manga_title(partial_comic_info.series, "MANGA", {})
        except MangaNotFoundError:
            content = cls.search_for_manga_title_by_manga_title_with_adult(partial_comic_info.series, "MANGA", {})

        if content is None:
            return None
        content = content.get("id")
        data = cls._search_details_by_series_id(content, "MANGA", {})

        startdate = data.get("startDate")
        comicinfo.summary = data.get("description").strip()
        comicinfo.day = startdate.get("day")
        comicinfo.month = startdate.get("month")
        comicinfo.year = startdate.get("year")
        comicinfo.series = data.get("title").get("romaji").strip()
        comicinfo.genre = ", ".join(data.get("genres")).strip()
        comicinfo.web = data.get("siteUrl").strip()

        # People
        cls.update_people_from_mapping(data["staff"]["edges"], cls.person_mapper, comicinfo,
                                       lambda item: item["node"]["name"]["full"],
                                       lambda item: item["role"])

        return comicinfo

    # TODO: Remove this method and make logger creation in __init__
    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _post(cls, query, variables, logging_info):
        try:
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
            if response.status_code == 429:  # Anilist rate-limit code
                raise AniListRateLimit()
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Manager is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None

        cls._log.debug(f'Query: {query}')
        cls._log.debug(f'Variables: {variables}')
        # cls._log.debug(f'Response JSON: {response.json()}')
        try:
            return response.json()['data']['Media']
        except TypeError:
            return None

    @classmethod
    def _search_for_manga_title_by_id(cls, manga_id, logging_info):
        query = '''
            query search_for_manga_title_by_id ($manga_id: Int) {
              Media (id: $manga_id, type: MANGA) {
                id
                title {
                  romaji
                  english
                  native
                }
                synonyms
              }
            }
            '''

        variables = {
            'manga_id': manga_id,
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def _search_for_manga_title_by_manga_title(cls, manga_title, format_, logging_info):
        query = '''
            query search_manga_by_manga_title ($manga_title: String, $format: MediaFormat) {
              Media (search: $manga_title, type: MANGA, format: $format, isAdult: false) {
                id
                title {
                  romaji
                  english
                  native
                }
                synonyms
              }
            }
            '''

        variables = {
            'manga_title': manga_title,
            'format': format_
        }

        ret = cls._post(query, variables, logging_info)
        if ret is None:
            raise MangaNotFoundError("AniList", manga_title)
        return ret

    @classmethod
    def search_for_manga_title_by_manga_title_with_adult(cls, manga_title, format_, logging_info):
        query = '''
            query search_manga_by_manga_title ($manga_title: String, $format: MediaFormat) {
              Media (search: $manga_title, type: MANGA, format: $format) {
                id
                title {
                  romaji
                  english
                  native
                }
                synonyms
              }
            }
            '''

        variables = {
            'manga_title': manga_title,
            'format': format_
        }

        return cls._post(query, variables, logging_info)

    @classmethod
    def _search_details_by_series_id(cls, series_id, format_, logging_info):
        query = '''
            query search_details_by_series_id ($series_id: Int, $format: MediaFormat) {
              Media (id: $series_id, type: MANGA, format: $format) {
                id
                status
                volumes
                siteUrl
                title {
                  romaji
                  english
                  native
                }
                type
                genres
                synonyms
                startDate {
                  day
                  month
                  year
                }
                coverImage {
                  extraLarge
                }
                staff {
                  edges {
                    node{
                      name {
                        first
                        last
                        full
                        alternative
                      }
                      siteUrl
                    }
                    role
                  }
                }
                description
              }
            }
            '''

        variables = {
            'series_id': series_id,
            'format': format_
        }

        return cls._post(query, variables, logging_info)


class AniListRateLimit(Exception):
    """
    Exception raised when AniList rate-limit is breached.
    """
