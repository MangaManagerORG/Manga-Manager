import abc
import configparser
import copy
from configparser import ConfigParser
from typing import MutableMapping, List

import src
from src.Settings.SettingControl import SettingControl
from src.Settings.SettingControlType import SettingControlType
from src.Settings.SettingSection import SettingSection

layout_factory = {}

CONFIG_PATH = ""
CPARSER = ConfigParser()


# class SettingItem(object):
#     def __init__(self, section, key, name, tooltip, value=None, type_=False, values=None):
#         if values is None:
#             values = list()
#         self.section = section
#         self.key = key
#         self.name = name
#         self.tooltip = tooltip
#         self.value = value
#         self.type_ = type_
#         self.values = values
#
#     def __repr__(self):
#         return self.value
#
#     def __bool__(self):
#         if self.type_ == "bool":
#             return True if self.value in ("True", True, "true") else False
#         else:
#             return bool(self.value)
#
#     def __str__(self):
#         return self.value


# class SettingsSection(object):
#     _section_name: str
#
#     def __init__(self, section_name, settings_dict: list[SettingControl]):
#         self.settings: list[SettingItem] = []
#         self._section_name = section_name
#         self.pname = settings_dict["pretty_name"]
#
#         a = {}
#         for value in settings_dict.get("values"):
#             b = copy.copy(SettingItem)
#             b.value = property(lambda self_: CPARSER.get(self_.section, self_.key),
#                                lambda self_, new_value: CPARSER[self_.section].update({self_.key: new_value or ""}))
#             try:
#                 value["value"] = CPARSER.get(self._section_name, value.get("key"))
#             except configparser.NoOptionError:
#                 CPARSER.set(self._section_name,value.get("key"), "")
#
#             c = b(section_name, **value)
#
#             c.__dict__.update(value)
#             a[value["key"]] = c
#             self.settings.append(c)
#
#         self.__dict__.update(a)
#
#     @property
#     def section_name(self) -> str:
#         return self._section_name
#
#     @classmethod
#     def get(cls, key, *_, **__):
#         return CPARSER.get(cls._section_name, key)
#
#     @classmethod
#     def set(cls, key, value, *_, **__):
#         CPARSER[cls._section_name][key] = value


# factory: dict[MutableMapping[str, SettingsSection]] = dict()
#
#
# def register_section(section_name, section: SettingsSection):
#     factory[section_name] = section


# class Settings:
#     CPARSER = CPARSER
#     factory = factory
#
#     def __init__(self, config_path):
#         self.factory: dict[str:SettingsSection] = factory
#         global CONFIG_PATH
#         CONFIG_PATH = config_path
#
#     def get_setting_path(self, section_name):
#         return CONFIG_PATH
#
#     @staticmethod
#     def get_setting(section_name) -> SettingsSection:
#         return factory.get(section_name)
#
#     @staticmethod
#     def list_settings() -> list[MutableMapping[str, SettingsSection]]:
#         return [setting_key for setting_key in factory]
#
#     @staticmethod
#     def save_settings() -> None:
#         with open(CONFIG_PATH, 'w') as f:
#             CPARSER.write(f)
#
#     def load_settings(self) -> None:
#         CPARSER.read(CONFIG_PATH)
#         for section in registered_settings_sections:
#             if section not in CPARSER.sections():
#                 CPARSER.add_section(section)
#                 for value in registered_settings_sections.get(section).get("values"):
#                     CPARSER.set(section, value.get("key"), "")
#
#             section_class = SettingsSection(section, registered_settings_sections.get(section))
#             register_section(section, section_class)
#             setattr(self, section_class.section_name, section_class)


###
#
#   Default settings_class for base modules
#
default_settings = {
    "main": SettingSection("Main Settings", [
        SettingControl("library_path", "Library Path", SettingControlType.Text, "", "The path to your library. This location will be opened by default when choosing files"),
        SettingControl("covers_folder_path", "Covers folder path", SettingControlType.Text, "", "The path to your covers. This location will be opened by default when choosing covers"),
        SettingControl("cache_cover_images", "Cache cover images", SettingControlType.Bool, False, "If enabled, the covers of the file will be cached and shown in the ui"),
        SettingControl("selected_layout", "* Active layout", SettingControlType.Options, [], "Selects the layout to be displayed"),
    ]),
    "WebpConverter": SettingSection("Webp Converter Settings", [
        SettingControl("default_base_path", "Default base path", SettingControlType.Text, "", "The starting point where the glob will begin looking for files that match the pattern"),
    ]),
    "ExternalSources": SettingSection("External Sources Settings", [
        SettingControl("default_metadata_source", "Default metadata source", SettingControlType.Options, [], "The source that will be hit when looking for metadata"),
        SettingControl("default_cover_source", "Default cover source", SettingControlType.Options, [], "The source that will be hit when looking for cover images"),
    ])
}
# registered_settings_sections = {
#     "main": {
#         "pretty_name": "Main Settings",
#         "values": [
#             {
#                 "key": "library_path",
#                 "name": "Library path",
#                 "type_": SettingControlType.Text,
#                 "tooltip": "The path to your library. This location will be opened by default when choosing files",
#             },
#             {
#                 "key": "covers_folder_path",
#                 "name": "Covers folder path",
#                 "type_": SettingControlType.Text,
#                 "tooltip": "The path to your covers. This location will be opened by default when choosing covers"
#             },
#             {
#                 "key": "cache_cover_images",
#                 "name": "Cache cover images",
#                 "tooltip": "If enabled, the covers of the file will be cached and shown in the ui",
#                 "type_": SettingControlType.Bool,
#             },
#             {
#                 "key": "selected_layout",
#                 "name": "* Active layout",
#                 "tooltip": "Selects the layout to be displayed",
#                 "type_": SettingControlType.Options,
#                 "values": []
#             },
#         ]
#     },
#     "WebpConverter": {
#         "pretty_name": "Webp Converter Settings",
#         "values": [
#             {
#                 "key": "default_base_path",
#                 "name": "Default base path",
#                 "type_": SettingControlType.Text,
#                 "tooltip": "The starting point where the glob will begin looking for files that match the pattern"
#             }
#         ]
#     },
#     "ExternalSources": {
#         "pretty_name": "External Sources Settings",
#         "values": [
#             {
#                 "key": "default_metadata_source",
#                 "name": "Default metadata source",
#                 "tooltip": "The source that will be hit when looking for metadata.",
#                 "type_": SettingControlType.Options,
#                 "values": []
#             },
#             {
#                 "key": "default_cover_source",
#                 "name": "Default cover source",
#                 "tooltip": "The source that will be hit when looking for cover images.",
#                 "type_": SettingControlType.Options,
#                 "values": []
#             }
#         ]
#     }
#
# }

#settings_class = Settings(src.MM_PATH)