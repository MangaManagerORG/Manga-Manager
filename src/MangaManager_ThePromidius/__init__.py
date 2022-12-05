from src.MangaManager_ThePromidius.Common.settings import Settings

# Create our own implementation to have trace logging

_CONFIG_PATH = "config.ini"
# CONFIG_PATH = abspath(join(dirname(__file__), _CONFIG_PATH))
from pathlib import Path

MM_PATH = Path(Path.home(),"MangaManager")
MM_PATH.mkdir(exist_ok=True,parents=True)

CONFIG_PATH = Path(MM_PATH,_CONFIG_PATH)

settings = Settings(CONFIG_PATH)
settings.load_settings()
