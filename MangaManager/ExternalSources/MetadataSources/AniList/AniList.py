import logging

import requests

from io import StringIO
from html.parser import HTMLParser
from src.Common.errors import MangaNotFoundError
from src.DynamicLibController.models.MetadataSourcesInterface import IMetadataSource
from src.MetadataManager.comicinfo import ComicInfo

# https://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class AniList(IMetadataSource):
    name = "AniList"
    _log = logging.getLogger()

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
        print("sdsadas")
        desc = strip_tags(data.get("description").strip())
        source_index = desc.find("Source")
        if source_index != -1:
            start_index = desc.find("(", 0, source_index)
            end_index = desc.find(")", source_index)
            if start_index != -1 and end_index != -1:
                if desc[start_index - 1] == '\n':
                    start_index -= 1
                desc = desc[:start_index] + desc[end_index + 1:]
        comicinfo.set_Summary(desc.strip())

        startdate = data.get("startDate")
        comicinfo.set_Day(startdate.get("day"))
        comicinfo.set_Month(startdate.get("month"))
        comicinfo.set_Year(startdate.get("year"))

        # TODO setting prefer english romaji
        set_english = "english"
        set_romaji = "romaji"
        title_english = data.get("title").get(set_english)
        if title_english:
            comicinfo.set_Series(title_english.strip())
            comicinfo.set_LocalizedSeries(data.get("title").get(set_romaji).strip())
        else:
            comicinfo.set_Series(data.get("title").get(set_romaji).strip())

        if data.get("volumes"):
            comicinfo.set_Count(data.get("volumes"))

        comicinfo.set_Genre(", ".join(data.get("genres")))
        comicinfo.set_Web(data.get("siteUrl").strip())
        # People
        mapping = {
            "Original Story": ["Writer"],
            "Story & Art": ["Inker", "Writer"],
            "Story": ["Writer"],
            "Art": ["Inker"],
            # "Character Design": "Penciller",
            "Assistant": ["Editor"],
            "Assistant (former)": ["Editor"],
            "Assistant (mob)": ["Editor"],
            "Assistant (beta)": ["Editor"]
        }
        staff_list = data["staff"]["edges"]

        for staff in staff_list:
            node = staff["node"]
            name = node["name"]["full"]
            role = staff["role"]
            mapped_role_list = mapping.get(role, "")
            if mapped_role_list:
                for mapped_role in mapped_role_list:
                    old_mapped_role = comicinfo.get_attr_by_name(mapped_role).strip()
                    if old_mapped_role != "":
                        name = old_mapped_role + ", " + name
                    comicinfo.set_attr_by_name(mapped_role, name.strip())
            else:
                print(f"No mapping found for role: {role}")

        print("asdsadsa")
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
            raise MangaNotFoundError("AniList",manga_title)
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
