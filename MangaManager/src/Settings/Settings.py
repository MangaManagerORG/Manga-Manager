import configparser
import json
import os
import logging

from src.Settings import default_settings

logger = logging.getLogger("MangaManager")

class Settings():
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

    def save(self):
        pass

    def load(self):
        self.config_parser.read(self.config_file)

        # Update DefaultSettings with values in config
        for section in self.config_parser.sections():
            for control in default_settings[section].values:
                control.value = self.get(section, control.key)

    def get(self, section, key):
        return self.config_parser[section][key].strip()

    def set(self, section, key, value):
        self.config_parser[section][key] = value
        self.load()