from __future__ import annotations

import logging
import re
import requests
from enum import StrEnum
from typing import Optional

from common import get_invalid_person_tag
from common.models import ComicInfo
from src.Common.errors import MangaNotFoundError
from src.DynamicLibController.models.IMetadataSource import IMetadataSource
from src.Settings.SettingControl import SettingControl
from src.Settings.SettingControlType import SettingControlType
from src.Settings.SettingSection import SettingSection
from src.Settings.Settings import Settings

pattern = r"anilist.com/manga/(\d+)"

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
    _HOW_METADATA_MAPS_TOOLTIP = "How metadata field will map to ComicInfo fields"
    romaji_as_series = Settings().get(name, AniListSetting.SeriesTitleLanguage)

    def init_settings(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl(key=AniListSetting.SeriesTitleLanguage, name="Prefer Romaji Series Title Language",
                               control_type=SettingControlType.Bool, value=True,
                               tooltip="How metadata field will map to Series and LocalizedSeries fields\n"
                                       "true: Romaji->Series, English->LocalizedSeries\n"
                                       "false: English->Series, Romaji->LocalizedSeries\n"
                                       "Always Romaji->Series when no English"),
                SettingControl(key=AniListPerson.OriginalStory, name="Original Story",
                               control_type=SettingControlType.Text, value="Writer",
                               tooltip=self._HOW_METADATA_MAPS_TOOLTIP,
                               validate=self.is_valid_person_tag, format_value=self.trim),
                SettingControl(key=AniListPerson.CharacterDesign, name="Character Design",
                               control_type=SettingControlType.Text, value="Penciller",
                               tooltip=self._HOW_METADATA_MAPS_TOOLTIP,
                               validate=self.is_valid_person_tag, format_value=self.trim),
                SettingControl(key=AniListPerson.Story, name="Story",
                               control_type=SettingControlType.Text, value="Writer",
                               tooltip=self._HOW_METADATA_MAPS_TOOLTIP,
                               validate=self.is_valid_person_tag, format_value=self.trim),
                SettingControl(key=AniListPerson.Art, name="Art",
                               control_type=SettingControlType.Text, value="Penciller, Inker, CoverArtist",
                               tooltip=self._HOW_METADATA_MAPS_TOOLTIP,
                               validate=self.is_valid_person_tag, format_value=self.trim),
                SettingControl(key=AniListPerson.Assistant, name="Assistant",
                               control_type=SettingControlType.Text, value="",
                               tooltip=self._HOW_METADATA_MAPS_TOOLTIP,
                               validate=self.is_valid_person_tag, format_value=self.trim),
            ])
        ]
        super().init_settings()

    @staticmethod
    def is_valid_person_tag(key, value):
        invalid_people = get_invalid_person_tag(value)

        if len(invalid_people) == 0:
            return ""
        return ", ".join(invalid_people) + " are not a valid tags"
    @staticmethod
    def get_manga_id_from_url(url):
        pattern = r"https:\/\/anilist\.co\/manga\/(\d+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return None
    @classmethod
    def save_settings(cls):
        cls.romaji_as_series = Settings().get(cls.name, AniListSetting.SeriesTitleLanguage)
        cls.person_mapper["Original Story"] = Settings().get(cls.name, AniListPerson.OriginalStory).split(',')
        cls.person_mapper["Original Creator"] = Settings().get(cls.name, AniListPerson.OriginalStory).split(',')
        cls.person_mapper["Character Design"] = Settings().get(cls.name, AniListPerson.CharacterDesign).split(',')
        cls.person_mapper["Story"] = Settings().get(cls.name, AniListPerson.Story).split(',')
        cls.person_mapper["Art"] = Settings().get(cls.name, AniListPerson.Art).split(',')
        cls.person_mapper["Story & Art"] = Settings().get(cls.name, AniListPerson.Story).split(',') + Settings().get(
            cls.name, AniListPerson.Art).split(',')
        cls.person_mapper["Assistant"] = Settings().get(cls.name, AniListPerson.Assistant).split(',')
    @classmethod
    def _get_id_from_series(cls, cinfo: ComicInfo) -> Optional[int]:

        manga_id = cls.get_manga_id_from_url(cinfo.web)
        if manga_id is not None:
            return manga_id

        try:
            content = cls._search_for_manga_title_by_manga_title(cinfo.series, "MANGA", {})
        except MangaNotFoundError:
            content = cls.search_for_manga_title_by_manga_title_with_adult(cinfo.series, "MANGA", {})

        if content is None:
            return None
        return content.get("id")

    @classmethod
    def get_cinfo(cls, comic_info_from_ui: ComicInfo) -> ComicInfo | None:
        comicinfo = ComicInfo()
        serie_id = cls._get_id_from_series(comic_info_from_ui)
        if serie_id is None:
            return None
        data = cls._search_details_by_series_id(serie_id, "MANGA", {})

        startdate = data.get("startDate")
        comicinfo.day = startdate.get("day")
        comicinfo.month = startdate.get("month")
        comicinfo.year = startdate.get("year")
        comicinfo.genre = ", ".join(data.get("genres")).strip()
        comicinfo.web = data.get("siteUrl").strip()
        if data.get("volumes"):
            comicinfo.count = data.get("volumes")

        # Title (Series & LocalizedSeries)
        title = data.get("title")
        cls._log.info("[AniList] Fetch Data found title " + str(title) + " for " + comic_info_from_ui.series)
        title_english = (data.get("title").get("english") or "").strip()
        title_romaji = (data.get("title").get("romaji") or "").strip()
        if cls.romaji_as_series:
            comicinfo.series = title_romaji
            if title_romaji != title_english:
                comicinfo.localized_series = title_english
        else:
            comicinfo.series = title_english if title_english != "" else title_romaji
            if title_romaji != title_english:
                comicinfo.localized_series = title_romaji

        # Summary
        comicinfo.summary = IMetadataSource.clean_description(data.get("description"), remove_source=True)

        # People
        cls.update_people_from_mapping(data["staff"]["edges"], cls.person_mapper, comicinfo,
                                       lambda item: item["node"]["name"]["full"],
                                       lambda item: item["role"])

        return comicinfo

    @classmethod
    def _post(cls, query, variables, logging_info):
        try:
            response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
            if response.status_code == 429:  # Anilist rate-limit code
                raise AniListRateLimit()
        except AniListRateLimit:
            cls._log.exception("Hitted anilist ratelimit")
            return None
        except Exception:
            cls._log.exception("Unhandled exception making the request to anilist")
            return None

        cls._log.debug(f'Query: {query}')
        cls._log.debug(f'Variables: {variables}')
        # self.logger.debug(f'Response JSON: {response.json()}')
        try:
            return response.json()['data']['Media']
        except TypeError:
            cls._log.exception("Wrong data format recieved when parsing response json")
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
