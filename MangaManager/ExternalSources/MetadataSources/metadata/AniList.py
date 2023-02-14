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
    OriginalStory = "original_story",  # Original Story
    CharacterDesign = "character_design",  # Character Design
    Story = "story",  # Story
    Art = "art",  # Art
    Assistant = "assistant",  # Assistant


class AniListSetting(StrEnum):
    SeriesTitleLanguage = "series_title_language",


class AniList(IMetadataSource):
    name = "AniList"
    _log = logging.getLogger()
    # Map the Role from API to the ComicInfo tags to write
    person_mapper = {}
    romaji_as_series = True

    def __init__(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl(AniListSetting.SeriesTitleLanguage, "Prefer Romaji Series Title Language",
                               SettingControlType.Bool, True,
                               ("How metadata field will map to Series and LocalizedSeries fields\n"
                                "true: Romaji->Series, English->LocalizedSeries\n"
                                "false: English->Series, Romaji->LocalizedSeries\n"
                                "Always Romaji->Series when no English")),
                SettingControl(AniListPerson.OriginalStory, "Original Story", SettingControlType.Text, "Writer",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.CharacterDesign, "Character Design", SettingControlType.Text, "Penciller",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Story, "Story", SettingControlType.Text, "Writer",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Art, "Art", SettingControlType.Text, "Penciller, Inker, CoverArtist",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Assistant, "Assistant", SettingControlType.Text, "",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
            ])
        ]

        super(AniList, self).__init__()

    def save_settings(self):
        self.romaji_as_series = Settings().get(self.name, AniListSetting.SeriesTitleLanguage)
        self.person_mapper["Original Story"] = Settings().get(self.name, AniListPerson.OriginalStory).split(',')
        self.person_mapper["Character Design"] = Settings().get(self.name, AniListPerson.CharacterDesign).split(',')
        self.person_mapper["Story"] = Settings().get(self.name, AniListPerson.Story).split(',')
        self.person_mapper["Art"] = Settings().get(self.name, AniListPerson.Art).split(',')
        self.person_mapper["Story & Art"] = Settings().get(self.name, AniListPerson.Story).split(',') + Settings().get(
            self.name, AniListPerson.Art).split(',')
        self.person_mapper["Assistant"] = Settings().get(self.name, AniListPerson.Assistant).split(',')

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
    def get_cinfo(cls, comic_info_from_ui: ComicInfo) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = cls._search_for_manga_title_by_manga_title(comic_info_from_ui.series, "MANGA", {})
        except MangaNotFoundError:
            content = cls.search_for_manga_title_by_manga_title_with_adult(comic_info_from_ui.series, "MANGA", {})

        if content is None:
            return None
        content = content.get("id")
        data = cls._search_details_by_series_id(content, "MANGA", {})

        startdate = data.get("startDate")
        comicinfo.day = startdate.get("day")
        comicinfo.month = startdate.get("month")
        comicinfo.year = startdate.get("year")
        comicinfo.genre = ", ".join(data.get("genres")).strip()
        comicinfo.web = data.get("siteUrl").strip()
        if data.get("volumes"):
            comicinfo.count = data.get("volumes")

        # Title (Series & LocalizedSeries)
        title_english = data.get("title").get("english").strip() or ""
        title_romaji = data.get("title").get("romaji").strip() or ""
        if cls.romaji_as_series:
            comicinfo.series = title_romaji
            comicinfo.localized_series = title_english
        else:
            comicinfo.series = title_english
            comicinfo.localized_series = title_romaji

        # Summary
        comicinfo.summary = IMetadataSource.clean_description(data.get("description"), removeSource=True)

        # People
        cls.update_people_from_mapping(cls, data["staff"]["edges"], cls.person_mapper, comicinfo,
                                       lambda item: item["node"]["name"]["full"],
                                       lambda item: item["role"])

        return comicinfo

    @classmethod
    def _post(cls, query, variables, logging_info):
        try:
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
            if response.status_code == 429:  # Anilist rate-limit code
                raise AniListRateLimit()
        except Exception as e:
            cls.logger.exception(e, extra=logging_info)
            cls.logger.warning('Manga Manager is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None

        cls.logger.debug(f'Query: {query}')
        cls.logger.debug(f'Variables: {variables}')
        # self.logger.debug(f'Response JSON: {response.json()}')
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
