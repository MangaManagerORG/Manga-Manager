import abc
from typing import final
from io import StringIO
from html.parser import HTMLParser

from common.models import ComicInfo
from .ExtensionsInterface import IMMExtension
from src.Settings import Settings


class IMetadataSource(IMMExtension):
    name = ''
    """
        A set of settings which will be found in the main settings dialog of Manga Manager and used for the source
    """
    settings = []

    @classmethod
    @abc.abstractmethod
    def get_cinfo(cls, series_name) -> ComicInfo:
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
                            comicinfo.append_by_tag_name(fields.strip(), self.merge(old_name, name))
                        else:
                            comicinfo.append_by_tag_name(fields.strip(), name.strip())

            print(f"No mapping found for: {name} as {role}")

    def strip_description_html_tags(summary):
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

        s = MLStripper()
        s.feed(summary.strip())
        summary = s.get_data()
        source_index = summary.find("Source")
        if source_index != -1:
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

        # Save any default settings to ini
        for section in self.settings:
            for control in section.values:
                Settings().set_default(section.key, control.key, control.value)
        Settings().save()

        # Load any saved settings into memory to overwrite defaults
        self.save_settings()
