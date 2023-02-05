import configparser
import os
import logging

from src.Settings import SettingHeading

logger = logging.getLogger()
default_settings = {
    SettingHeading.Main: [
        {"library_path": ""},
        {"covers_folder_path": ""},
        {"cache_cover_images": ""},
        {"selected_layout": "False"},
    ],
    SettingHeading.WebpConverter: [
        {"default_base_path": ""},
    ],
    SettingHeading.ExternalSources: [
        {"default_metadata_source": ""},
        {"default_cover_source": ""},
    ],
}


class Settings:
    """ This is a singleton that holds settings.ini key/values """
    __instance = None
    config_parser = configparser.ConfigParser(interpolation=None)

    def __new__(cls, config_file='settings.ini'):
        if Settings.__instance is None:
            Settings.__instance = object.__new__(cls)
        Settings.__instance.config_file = os.path.abspath(config_file)

        if len(Settings.__instance.config_parser.sections()) == 0:
            logger.info('Loading Config from: {}'.format(Settings.__instance.config_file))
            Settings.__instance.load()

        return Settings.__instance

    def __init__(self, config_file='settings.ini'):
        self.config_file = config_file
        if not os.path.exists(self.config_file):
            self.save()

    def save(self):
        """Save the current settings from memory to disk"""
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def load(self):
        """Load the data from file and populate DefaultSettings"""
        self.config_parser.read(self.config_file)

        if len(self.config_parser.sections()) == 0:
            # Init default settings and refresh
            for section in default_settings:
                self.config_parser.add_section(section)
                for (key, value) in section.items():
                    self.config_parser[section][key] = value
            self.save()

    def get(self, section, key):
        """Get a key's value, None if not present"""
        if section not in self.config_parser or key not in self.config_parser[section]:
            logger.error('Section or Key did not exist in settings: {}.{}'.format(section, key))
            return None
        return self.config_parser[section][key].strip()

    def set(self, section, key, value):
        """Sets a key's value. Will Save to disk and reload Settings"""
        self.config_parser[section][key] = value
        self.save()
        self.load()
