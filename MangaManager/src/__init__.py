from pathlib import Path
_CONFIG_PATH = "config.ini"
MM_PATH = Path(Path.home(), "MangaManager")

from src.Common.settings import Settings


MM_PATH.mkdir(exist_ok=True,parents=True)
CONFIG_PATH = Path(MM_PATH, _CONFIG_PATH)

settings_class = Settings(CONFIG_PATH)
settings_class.load_settings()

