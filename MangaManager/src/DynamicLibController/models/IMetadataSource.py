import abc
import logging
from typing import final
from io import StringIO
from html.parser import HTMLParser

from common.models import ComicInfo
from .ExtensionsInterface import IMMExtension
from src.Settings import Settings

# MLStripper: https://stackoverflow.com/a/925630
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


class IMetadataSource(IMMExtension):
    name = ''
    """
        A set of settings which will be found in the main settings dialog of Manga Manager and used for the source
    """
    settings = []
    logger = None

    @classmethod
    @abc.abstractmethod
    def get_cinfo(cls, comic_info_from_ui: ComicInfo) -> ComicInfo:
        ...

    def save_settings(self):
        """
        When a setting update occurs, this is invoked and internal state should be updated from Settings()
        """
        pass

    def merge(self, value1, value2):
        return self.trim(value1 + "," + value2)

    def update_people_from_mapping(self, people: list[object], mapping, comicinfo: ComicInfo, name_selector,
                                   role_selector):
        if comicinfo is None:
            return

        for person in people:
            name = name_selector(person)
            role = role_selector(person)

            for map_role in mapping:
                if map_role == role:
                    for fields in mapping[map_role]:
                        old_name = comicinfo.get_by_tag_name(fields.strip())
                        if old_name and old_name.strip() != "":
                            comicinfo.set_by_tag_name(fields.strip(), self.merge(self, old_name, name))
                        else:
                            comicinfo.set_by_tag_name(fields.strip(), name.strip())

            print(f"No mapping found for: {name} as {role}")

    @staticmethod
    def clean_description(summary, removeSource):
        """
        summary: String
        removeSource: Boolean

        Removes HTML text like <br> from String
        Removes "(Source ...)" from String when flag is set to True
        """
        # Remove HTML
        s = MLStripper()
        s.feed(summary.strip())
        summary = s.get_data()

        # Remove "(Source ...)"
        source_index = summary.find("Source")
        if removeSource and source_index != -1:
            start_index = summary.find("(", 0, source_index)
            end_index = summary.find(")", source_index)
            if start_index != -1 and end_index != -1:
                if summary[start_index - 1] == '\n':
                    start_index -= 1
                summary = summary[:start_index] + summary[end_index + 1:]

        return summary.strip()

    @final
    def __init__(self):
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(
                f"Error initializing the {self.__class__.__name__} Extension. The 'name' attribute must be set in the CoverSource class.")

        self.logger = logging.getLogger(f'{self.__module__}.{self.__class__.__name__}')
        # Save any default settings to ini
        for section in self.settings:
            for control in section.values:
                Settings().set_default(section.key, control.key, control.value)
        Settings().save()

        # Load any saved settings into memory to overwrite defaults
        self.save_settings()
