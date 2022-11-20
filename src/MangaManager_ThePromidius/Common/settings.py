import abc
import dataclasses
import logging
from configparser import ConfigParser

config = ConfigParser()


logger = logging.getLogger("Settings")

# @dataclasses.dataclass
class SettingsSection(abc.ABC):
    def __init__(self):
        self.initialize()

    @abc.abstractmethod
    def initialize(self):
        ...

    def get_value(self, value):
        return getattr(self, value)

    def set_value(self,name, value):
        setattr(self, name, value)

_CONFIG_PATH = "config.ini"
@dataclasses.dataclass
class _DummySetting(SettingsSection):
    def initialize(self):
        ...
    def fill(self, values:dict):
        self.__dict__.update(values)
        # setattr(self,'__dict__', values)
        return self


class Settings:
    # def __init__(self):
    # if not os.path.exists(_CONFIG_FILE):
    def __init__(self, config_path = ""):
        _CONFIG_PATH = config_path

    def read(self):
        if not self.__dict__:
            raise RuntimeError("Modules must be imported prior to read their configs")
        config.read(_CONFIG_PATH)
        for section in config.sections():
            if section not in self.__dict__:
                section_class = _DummySetting
                section_class.name = section
                section_class = section_class()
                section_class.fill(config[section])
                # self.main = section_class

            else:
                section_class = getattr(self, section)
            for key in config[section]:
                setattr(section_class, key, config.get(section, key))
            # self.__dict__.update(config[section])
            setattr(self, section, section_class)
        self.write()

    def write(self):
        for section in self.__dict__:
            if not self.__dict__.get(section):
                logger.warning(f"Aborting loading extension settings. Section: '{section}'")
                continue
            config[section] = getattr(self,section).__dict__ # FIXME: weird error here
        with open(_CONFIG_PATH, 'w') as f:
            config.write(f)

    def import_(self, value):
        """
        Modules must be imported prior to read the config
        :param value:
        :return:
        """
        # section_class = SettingsSection()
        setattr(self, value.name, value)

    def get_setion(self, value) -> SettingsSection:
        return getattr(self, value)
# if __name__ == '__main__':
#     a = Settings()
#     a.read()
#     a.write()
#     print("sda")
