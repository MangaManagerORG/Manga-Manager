import configparser
import logging
import os

from src.Settings.SettingsDefault import default_settings

logger = logging.getLogger()


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
        self.load()

    def save(self):
        """Save the current settings from memory to disk"""
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    def load(self):
        """Load the data from file and populate DefaultSettings"""
        self.config_parser.read(self.config_file)

        # Ensure all default settings exists, else add them
        for section in default_settings:
            if section not in self.config_parser.sections():
                self.config_parser.add_section(section)
            for item in default_settings[section]:
                for (key, value) in item.items():
                    if key not in self.config_parser[section] or self.config_parser.get(section, key) == "":
                        self.config_parser.set(section, key, str(value))

        self.save()

    def get(self, section, key):
        """Get a key's value, None if not present"""
        if not self.config_parser.has_section(section) or not self.config_parser.has_option(section, key):
            logger.error('Section or Key did not exist in settings: {}.{}'.format(section, key))
            return None
        return self.config_parser.get(section, key).strip()

    def set_default(self, section, key, value):
        """Sets a key's value only if it doesn't exist"""
        self._create_section(section)
        if key not in self.config_parser[section]:
            self.config_parser.set(section, key, str(value))

    def get_default(self, section, key, default_value):
        """
        Returns default value and creates the key if it doesn't exist
        """
        self.set_default(section, key, default_value)
        return self.get(section, key)

    def set(self, section, key, value):
        """Sets a key's value. Will Save to disk and reload Settings"""
        self._create_section(section)
        self.config_parser.set(section, key, str(value))
        self.save()
        self.load()

    def _create_section(self, section):
        if section not in self.config_parser:
            self.config_parser.add_section(section)
