import configparser
import os
import logging

logger = logging.getLogger("MangaManager")

class Settings():
    """ This is a singleton that holds settings.ini key/values """
    __instance = None
    config_parser = configparser.ConfigParser(interpolation=None)

    def __new__(cls, config_file='settings.ini', thumbs_file='r18-thumbs.csv'):
        if Settings.__instance is None:
            Settings.__instance = object.__new__(cls)
        Settings.__instance.config_file = os.path.abspath(config_file)

        if len(Settings.__instance.config_parser.sections()) == 0:
            logger.info('Loading Config from: {}'.format(Settings.__instance.config_file))
            Settings.__instance.load()

        return Settings.__instance

    def __init__(self, config_file='settings.ini'):
        self.config_file = config_file

    def create_if_missing(self):
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                f.write('')
            self.save()
        return self

    def save(self):
        pass

    def load(self):
        self.config_parser.read(self.config_file)

    def get(self, section, key):
        return self.config_parser[section][key].strip()