from __future__ import annotations

import logging

import requests

from src.Common.errors import MangaNotFoundError
from src.Common.utils import update_people_from_mapping
from src.DynamicLibController.models.IMetadataSource import IMetadataSource
from src.MetadataManager.comicinfo import ComicInfo
from src.Settings.SettingControl import SettingControl
from src.Settings.SettingControlType import SettingControlType
from src.Settings.SettingSection import SettingSection
from src.Settings.Settings import Settings


class AniList(IMetadataSource):
    name = "AniList"
    _log = logging.getLogger()
    person_mapper = {
        "Original Story": [
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

    settings = [
        SettingSection(name, name, [
            SettingControl("Original Story", "Original Story", SettingControlType.Text, "Writer",
                           "How metadata field will map to ComicInfo fields"),
            SettingControl("Character Design", "Character Design", SettingControlType.Text, "Penciller",
                           "How metadata field will map to ComicInfo fields"),
            SettingControl("Story & Art", "Story & Art", SettingControlType.Text, "Writer, Penciller, Inker, CoverArtist",
                           "How metadata field will map to ComicInfo fields"),
        ])
    ]

    def __init__(self):
        pass

    def save_settings(self):
        self.person_mapper["Original Story"] = Settings().get(self.name, 'Original Story').split(',')
        self.person_mapper["Character Design"] = Settings().get(self.name, 'Character Design').split(',')
        self.person_mapper["Story & Art"] = Settings().get(self.name, 'Story & Art').split(',')

    @classmethod
    def get_cinfo(cls, series_name) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = cls._search_for_manga_title_by_manga_title(series_name, "MANGA", {})
        except MangaNotFoundError:
            content = cls.search_for_manga_title_by_manga_title_with_adult(series_name, "MANGA", {})

        if content is None:
            return None
        content = content.get("id")
        data = cls._search_details_by_series_id(content, "MANGA", {})

        startdate = data.get("startDate")
        comicinfo.set_Summary(data.get("description").strip())
        comicinfo.set_Day(startdate.get("day"))
        comicinfo.set_Month(startdate.get("month"))
        comicinfo.set_Year(startdate.get("year"))
        comicinfo.set_Series(data.get("title").get("romaji").strip())
        comicinfo.set_Genre(", ".join(data.get("genres")))
        comicinfo.set_Web(data.get("siteUrl").strip())

        # People
        update_people_from_mapping(data["staff"]["edges"], cls.person_mapper, comicinfo,
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
