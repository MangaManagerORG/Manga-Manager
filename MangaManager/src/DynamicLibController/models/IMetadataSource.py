import abc
from typing import final

from common.models import ComicInfo
from src.Settings import Settings


class IMetadataSource(abc.ABC):
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

    def update_people_from_mapping(people: list[object], mapping, comicinfo: ComicInfo, name_selector, role_selector):
        if comicinfo is None:
            return

        for person in people:
            name = name_selector(person)
            role = role_selector(person)

            for map_role in mapping:
                if map_role == role:
                    for fields in mapping[map_role]:
                        comicinfo.set_by_tag_name(fields, name.strip())

            print(f"No mapping found for: {name} as {role}")

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