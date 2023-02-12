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
    OriginalStory = "Original Story",
    CharacterDesign = "Character Design",
    StoryAndArt = "Story & Art",
    Story = "Story",
    Art = "Art",
    Assistant = "Assistant",
    Assistant_former = "Assistant (former)",
    Assistant_mob = "Assistant (mob)",
    Assistant_beta = "Assistant (beta)",


class AniListSetting(StrEnum):
    SeriesTitleLanguage = "series_title_language",


class AniList(IMetadataSource):
    name = "AniList"
    _log = logging.getLogger()
    # Map the Role from API to the ComicInfo tags to write
    person_mapper = {}
    aniList_setting = {}

    def __init__(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl(AniListSetting.SeriesTitleLanguage, "Prefer Romaji Series Title Language",
                               SettingControlType.Bool, True,
                               "How metadata field will map to Series and LocalizedSeries fields"),
                SettingControl(AniListPerson.OriginalStory, AniListPerson.OriginalStory, SettingControlType.Text,
                               "Writer",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.CharacterDesign, AniListPerson.CharacterDesign, SettingControlType.Text,
                               "Penciller",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.StoryAndArt, AniListPerson.StoryAndArt, SettingControlType.Text,
                               "Writer, Penciller, Inker, CoverArtist",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Story, AniListPerson.Story, SettingControlType.Text, "Writer",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Art, AniListPerson.Art, SettingControlType.Text,
                               "Penciller, Inker, CoverArtist",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Assistant, AniListPerson.Assistant, SettingControlType.Text, "",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Assistant_former, AniListPerson.Assistant_former, SettingControlType.Text,
                               "",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Assistant_mob, AniListPerson.Assistant_mob, SettingControlType.Text, "",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
                SettingControl(AniListPerson.Assistant_beta, AniListPerson.Assistant_beta, SettingControlType.Text, "",
                               "How metadata field will map to ComicInfo fields", self.is_valid_person_tag, self.trim),
            ])
        ]

        super(AniList, self).__init__()

    def save_settings(self):
        self.aniList_setting[AniListSetting.SeriesTitleLanguage] = [Settings().get(self.name,
                                                                                   AniListSetting.SeriesTitleLanguage)]
        self.person_mapper[AniListPerson.OriginalStory] = Settings().get(self.name, AniListPerson.OriginalStory).split(
            ',')
        self.person_mapper[AniListPerson.CharacterDesign] = Settings().get(self.name,
                                                                           AniListPerson.CharacterDesign).split(',')
        self.person_mapper[AniListPerson.StoryAndArt] = Settings().get(self.name, AniListPerson.StoryAndArt).split(',')
        self.person_mapper[AniListPerson.Story] = Settings().get(self.name, AniListPerson.Story).split(',')
        self.person_mapper[AniListPerson.Art] = Settings().get(self.name, AniListPerson.Art).split(',')
        self.person_mapper[AniListPerson.Assistant] = Settings().get(self.name, AniListPerson.Assistant).split(',')
        self.person_mapper[AniListPerson.Assistant_former] = Settings().get(self.name,
                                                                            AniListPerson.Assistant_former).split(',')
        self.person_mapper[AniListPerson.Assistant_mob] = Settings().get(self.name, AniListPerson.Assistant_mob).split(
            ',')
        self.person_mapper[AniListPerson.Assistant_beta] = Settings().get(self.name,
                                                                          AniListPerson.Assistant_beta).split(',')

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
    def get_cinfo(cls, series_name) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = cls._search_for_manga_title_by_manga_title(series_name.strip(), "MANGA", {})
        except MangaNotFoundError:
            content = cls.search_for_manga_title_by_manga_title_with_adult(series_name.strip(), "MANGA", {})

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
        title_english = data.get("title").get("english")
        if cls.aniList_setting.get(AniListSetting.SeriesTitleLanguage) == 'True':
            comicinfo.series = data.get("title").get("romaji").strip()
            if title_english:
                comicinfo.localized_series = title_english.strip()
        else:
            if title_english:
                comicinfo.series = title_english.strip()
                comicinfo.localized_series = data.get("title").get("romaji").strip()
            else:
                comicinfo.series = data.get("title").get("romaji").strip()

        # Summary
        comicinfo.summary = cls.strip_description_html_tags(data.get("description"))

        # People
        cls.update_people_from_mapping(data["staff"]["edges"], cls.person_mapper, comicinfo,
                                       lambda item: item["node"]["name"]["full"],
                                       lambda item: item["role"])

        return comicinfo

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
