import configparser
import os
import logging

from main import providers
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

    """
        Save the current settings from memory to disk
    """

    def save(self):
        with open(self.config_file, 'w') as configfile:
            self.config_parser.write(configfile)

    """
        Load the data from file and populate DefaultSettings
    """

    def load(self):
        self.config_parser.read(self.config_file)

        # Update DefaultSettings with values in config
        for section in self.config_parser.sections():
            if not section in default_settings:
                # This is an external provider setting, update them
                for provider in providers:
                    for setting in list(self.config_parser.items(section)):
                        provider.save_setting(section, setting)
            else:
                for control in default_settings[section].values:
                    control.value = self.get(section, control.key)



    """
        Get a key's value
    """

    def get(self, section, key):
        return self.config_parser[section][key].strip()

    """
        Sets a key's value. Will Save to disk and reload DefaultSettings
    """

    def set(self, section, key, value):
        self.config_parser[section][key] = value
        self.save()
        self.load()

    # def add(self, section, setting_section):
    #     for control in setting_section.values:
    #         if not section in self.config_parser.sections():
    #             self.config_parser.add_section(section)
    #             default_settings[section] = setting_section
    #         else:
    #             # I need to override default_settings
    #             default_settings[section]
    #         self.config_parser[section][control.key] = control.value
    #         if not section in default_settings:
    #             default_settings[section] = setting_section
    #     self.save()
    #     self.load()
