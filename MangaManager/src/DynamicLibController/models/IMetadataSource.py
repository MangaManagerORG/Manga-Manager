import abc
import string
from typing import final, TypeVar, TypeVarTuple

from src.MetadataManager.comicinfo import ComicInfo
from src.Settings.SettingControl import SettingControl


class IMetadataSource(abc.ABC):
    name = ''
    """
        A set of settings which will be found in the main settings dialog of Manga Manager and used for the source
    """
    settings = []

    def save_setting(self, section_key, key, value):
        for section in self.settings:
            if section_key in section:
                for control in section[section_key]:
                    if control.key == key:
                        control.value = value


    @classmethod
    @abc.abstractmethod
    def get_cinfo(cls, series_name) -> ComicInfo:
        ...

    def save_settings(cls, setting_control: tuple[TypeVar(SettingControl), *TypeVarTuple(string)]):
        pass

    @final
    def __init__(self, master, super_=None, **kwargs):
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(
                f"Error initializing the {self.__class__.__name__} Extension. The 'name' attribute must be set in the CoverSource class.")
        # if self.embedded_ui:
        super().__init__(master=master, **kwargs)
        if super_ is not None:
            self._super = super_