from pathlib import Path

from src.MangaManager_ThePromidius.Common.settings import Settings

####

_CONFIG_PATH = "config.ini"
MM_PATH = Path(Path.home(), "MangaManager")
MM_PATH.mkdir(exist_ok=True,parents=True)

CONFIG_PATH = Path(MM_PATH,_CONFIG_PATH)

settings = Settings(CONFIG_PATH)
settings.load_settings()

# IMPORTANT: BREAK LINES IN IMPORTS BREAKS THE BUILDED EXECUTABLES
