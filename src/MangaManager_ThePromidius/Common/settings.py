import copy
from configparser import ConfigParser

# from src.MangaManager_ThePromidius import CONFIG_PATH
from typing import MutableMapping

CONFIG_PATH = ""
CPARSER = ConfigParser()


class SettingItem(object):
    def __init__(self, section, key, name, tooltip, value=None, type_=False):
        self.section = section
        self.key = key
        self.name = name
        self.tooltip = tooltip
        self.value = value
        self.type_ = type_

    def __repr__(self):
        return self.value

    def __bool__(self):
        if self.type_ == "bool":
            return True if self.value in ("True", True, "true") else False
        else:
            return bool(self.value)

    def __str__(self):
        return self.value


class SettingsSection(object):
    _section_name: str

    # @classmethod

    def __init__(self, section_name, settings_dict: dict):
        self.settings: list[SettingItem] = []
        self._section_name = section_name
        self.pname = settings_dict["pretty_name"]

        a = {}
        for value in settings_dict.get("values"):
            b = copy.copy(SettingItem)
            b.value = property(lambda self_: CPARSER.get(self_.section, self_.key),
                               lambda self_, new_value: CPARSER[self_.section].update({self_.key: new_value}))
            # b.__repr__ = lambda self_: CPARSER.get(self._section_name, value["key"])
            value["value"] = CPARSER.get(self._section_name, value.get("key"))
            c = b(section_name, **value)

            c.__dict__.update(value)
            a[value["key"]] = c
            self.settings.append(c)

        self.__dict__.update(a)
        # for value_dict in settings_dict["values"]:
        #     self._register_key(value_dict.get("key"))

    @property
    def section_name(self) -> str:
        return self._section_name

    # @classmethod
    # def _register_key(cls, name):
    #     setattr(cls, name,
    #             property(
    #                 lambda self_: self_.get(name),
    #                 lambda self_, value: self_.set(name, value))
    #             )

    @classmethod
    def get(cls, key, *args, **kargs):
        return CPARSER.get(cls._section_name, key)

    @classmethod
    def set(cls, key, value, *args, **kargs):
        CPARSER[cls._section_name][key] = value


factory: dict[MutableMapping[str, SettingsSection]] = dict()


def register_section(section_name, section: SettingsSection):
    factory[section_name] = section


class Settings:
    CPARSER = CPARSER
    factory = factory


    def __init__(self, config_path):
        self.factory: dict[str:SettingsSection] = factory
        global CONFIG_PATH
        CONFIG_PATH = config_path

    @staticmethod
    def get_setting(section_name) -> SettingsSection:
        return factory.get(section_name)

    @staticmethod
    def list_settings() -> list[str]:
        return [setting_key for setting_key in factory]

    @staticmethod
    def save_settings() -> None:

        with open(CONFIG_PATH, 'w') as f:
            CPARSER.write(f)

    def load_settings(self) -> None:
        CPARSER.read(CONFIG_PATH)
        for section in registered_settings_sections:
            if section not in CPARSER.sections():
                CPARSER.add_section(section)
                for value in registered_settings_sections.get(section).get("values"):
                    CPARSER.set(section, value.get("key"), "")

            section_class = SettingsSection(section, registered_settings_sections.get(section))
            register_section(section, section_class)
            setattr(self, section_class.section_name, section_class)


###
#
#   Default settings for base modules
#


registered_settings_sections = {
    "main": {
        "pretty_name": "Main settings",
        "values": [
            {
                "key": "library_path",
                "name": "Library path",
                "tooltip": "The path to your library. This location will be opened by default when choosing files",
            },
            {
                "key": "covers_folder_path",
                "name": "Covers folder path",
                "tooltip": "The path to your covers. This location will be opened by default when choosing covers"
            },
            {
                "key": "cache_cover_images",
                "name": "Cache cover images",
                "tooltip": "If enabled, the covers of the file will be cached and shown in the ui",
                "type_": "bool"
            },
        ]
    },
    "WebpConverter": {
        "pretty_name": "Webp Converter Settings",
        "values": [
            {
                "key": "default_base_path",
                "name": "Default base path",
                "tooltip": "The starting point where the glob will begin looking for files that match the pattern"
            }
        ]
    }
}
