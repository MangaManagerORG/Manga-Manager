import configparser
import os
import logging

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

