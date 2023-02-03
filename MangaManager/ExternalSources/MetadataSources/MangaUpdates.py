from __future__ import annotations

import logging

import requests

from src.Common.errors import MangaNotFoundError
from src.Common.utils import update_people_from_mapping
from src.DynamicLibController.models.MetadataSourcesInterface import IMetadataSource
from src.MetadataManager.comicinfo import ComicInfo
from src.Settings.SettingControlType import SettingControlType


class MangaUpdates(IMetadataSource):
    name = "MangaUpdates"
    _log = logging.getLogger()
    person_mapper = {
            "Author": [
                "Writer"
            ],
            "Artist": [
                "Penciller",
                "Inker",
                "CoverArtist"
            ]
    }

    settings = [
        {
            "pretty_name": "MangaUpdates: Person Mappings",
            "values": [
                {
                    "key": "Author",
                    "type_": SettingControlType.Text,
                    "name": "Author",
                    "tooltip": "Author from source will map to ComicInfo fields",
                    "value": "Writer"
                },
                {
                    "key": "Artist",
                    "type_": SettingControlType.Text,
                    "name": "Artist",
                    "tooltip": "Artist from source will map to ComicInfo fields",
                    "value": "Penciller, Inker, CoverArtist"
                }
            ]
        }
    ]

    def __init__(self):
        pass

    @classmethod
    def get_cinfo(cls, series_name) -> ComicInfo | None:
        comicinfo = ComicInfo()
        
        data = cls._get_series_details(series_name, {})

        # Basic Info
        comicinfo.set_Series(data["title"].strip())
        comicinfo.set_Summary(data["description"].strip())
        comicinfo.set_Genre(", ".join([ i["genre"] for i in data["genres"] ]))
        comicinfo.set_Tags(", ".join([ i["category"] for i in data["categories"] ]))
        comicinfo.set_Web(data["url"].strip())
        comicinfo.set_Manga("Yes" if data["type"] == "Manga" else "No")
        comicinfo.set_Year(data["year"])

        # People Info
        update_people_from_mapping(data["authors"], cls.person_mapper, comicinfo,
                                   lambda item: item["name"],
                                   lambda item: item["type"])

        comicinfo.set_Publisher(", ".join([ i["publisher_name"] for i in data["publishers"] ]))

        # Extended
        comicinfo.set_CommunityRating(round(data["bayesian_rating"]/2, 1))

        return comicinfo

    @classmethod
    def initialize(cls):
        cls._log = logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    @classmethod
    def _get_series_id(cls, search_params, logging_info):
        try:
            response = requests.post('https://api.mangaupdates.com/v1/series/search', json=search_params)
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Manager is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None

        cls._log.debug(f'Search Params: {search_params}')
        # cls._log.debug(f'Response JSON: {response.json()}')

        if len(response.json()['results']) == 0:
            raise MangaNotFoundError("MangaUpdates",search_params['search'])
        try:
            return response.json()['results'][0]['record']['series_id']
        except TypeError:
            return None

    @classmethod
    def _get_series_details(cls, manga_title, logging_info):
        search_params = {
            "search": manga_title,
            "page": 1,
            "per_page": 1
        }

        try:
            series_details = requests.get('https://api.mangaupdates.com/v1/series/' + str(cls._get_series_id(search_params, {})))
        except Exception as e:
            cls._log.exception(e, extra=logging_info)
            cls._log.warning('Manga Manager is unfamiliar with this error. Please log an issue for investigation.',
                             extra=logging_info)
            return None
            
        return series_details.json()
