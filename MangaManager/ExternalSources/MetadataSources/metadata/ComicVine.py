import logging
from abc import ABC

import requests

from common.models import ComicInfo
from src.Common.errors import MangaNotFoundError
from src.DynamicLibController.models.IMetadataSource import IMetadataSource
from src.Settings import SettingSection, SettingControl, SettingControlType, Settings


class ComicVine(IMetadataSource, ABC):
    name = 'ComicVine'
    _log = logging.getLogger()

    def __init__(self):
        self.settings = [
            SettingSection(self.name, self.name, [
                SettingControl('api_key', "API Key", SettingControlType.Text, "",
                               "API Key to communicate with ComicVine. This is required for the source"),

            ])
        ]

        super(ComicVine, self).__init__()
        self._log = logging.getLogger(f'{self.__module__}.{self.name}')

    def save_settings(self):
        pass

    def get_cinfo(self, partial_comic_info: ComicInfo) -> ComicInfo | None:
        comicinfo = ComicInfo()
        try:
            content = self._search_by_title(partial_comic_info.series)
        except MangaNotFoundError:
            content = self._search_by_issue(partial_comic_info.series)

        if content is None:
            return None
        # content = content.get("id")
        # data = self._search_details_by_series_id(content, "MANGA", {})
        #
        # startdate = data.get("startDate")
        # comicinfo.summary = data.get("description").strip()
        # comicinfo.day = startdate.get("day")
        # comicinfo.month = startdate.get("month")
        # comicinfo.year = startdate.get("year")
        # comicinfo.series = data.get("title").get("romaji").strip()
        # comicinfo.genre = ", ".join(data.get("genres")).strip()
        # comicinfo.web = data.get("siteUrl").strip()

        # People
        # self.update_people_from_mapping(data["staff"]["edges"], self.person_mapper, comicinfo,
        #                                lambda item: item["node"]["name"]["full"],
        #                                lambda item: item["role"])

        return comicinfo

    def _search_by_title(self, series_name, publish_year=""):
        url = f"{self._build_url_base('series')}&name={series_name}"
        try:
            response = requests.get(url)
            # if response.status_code == 429:  # Anilist rate-limit code
            #     raise AniListRateLimit()
        except Exception as e:
            #self._log.exception(e, extra=logging_info)
            self._log.warning('Manga Manager is unfamiliar with this error. Please log an issue for investigation.', e)
            return None

        self._log.debug(f'Query: {url}')
        #self._log.debug(f'Response JSON: {response.json()}')
        try:
            return response.json()['results']
        except TypeError:
            return None
        pass

    def _search_by_issue(self, series_name, issue_number):
        pass

    def _build_url_base(self, entity):
        return f"http://api.comicvine.com/{entity}/?api_key={Settings().get(self.name, 'API Key')}&format=json"
