from os.path import abspath, dirname, join

from MangaManager_ThePromidius.Common.settings import Settings

_CONFIG_PATH = "config.ini"
CONFIG_PATH = abspath(join(dirname(__file__), _CONFIG_PATH))

settings = Settings(CONFIG_PATH)
settings.load_settings()

a = settings.get_setting("main")
a.library_path
a.library_path.value = "new_path"
print("adsadsa")
