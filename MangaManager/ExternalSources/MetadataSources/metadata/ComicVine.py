import logging
from abc import ABC

from common.models import ComicInfo
from src.Common.errors import MangaNotFoundError
from src.DynamicLibController.models.IMetadataSource import IMetadataSource
from src.Settings import SettingSection, SettingControl, SettingControlType


class ComicVine(IMetadataSource, ABC):
    name = 'ComicVine'
    _log = logging.getLogger()

    def __init__(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl('API Key', "API Key", SettingControlType.Text, "",
                               "API Key to communicate with ComicVine. This is required for the source",
                               self.is_valid_api_key),

            ])
        ]

        super(ComicVine, self).__init__()
        self._log = logging.getLogger(f'{self.__module__}.{self.__name__}')

    def save_settings(self):
        pass

    def get_cinfo(self, partial_comic_info: ComicInfo) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = self._search_by_title(partial_comic_info.series, "MANGA", {})
        except MangaNotFoundError:
            content = self._search_by_issue(partial_comic_info.series, "MANGA", {})

        if content is None:
            return None
        content = content.get("id")
        data = self._search_details_by_series_id(content, "MANGA", {})

        startdate = data.get("startDate")
        comicinfo.summary = data.get("description").strip()
        comicinfo.day = startdate.get("day")
        comicinfo.month = startdate.get("month")
        comicinfo.year = startdate.get("year")
        comicinfo.series = data.get("title").get("romaji").strip()
        comicinfo.genre = ", ".join(data.get("genres")).strip()
        comicinfo.web = data.get("siteUrl").strip()

        # People
        self.update_people_from_mapping(data["staff"]["edges"], cls.person_mapper, comicinfo,
                                       lambda item: item["node"]["name"]["full"],
                                       lambda item: item["role"])

        return comicinfo

    def is_valid_api_key(self, value):
        return True
