import logging
from os import environ
from pathlib import Path

logger = logging.getLogger()
_CONFIG_PATH = "config.ini"
MM_PATH = Path(Path.home(), "MangaManager")
MM_PATH.mkdir(exist_ok=True, parents=True)
DEV_BUILD = f'{environ.get("$$_ENV_DEVELOPMENT_MM_$$")}'
DEV_BUILD = DEV_BUILD.lower() == "true"
EXTENSIONS_DIR = Path(MM_PATH, "Extensions")
EXTENSIONS_DIR.mkdir(exist_ok=True)

SOURCES_DIR = Path(MM_PATH, "Sources")
SOURCES_DIR.mkdir(exist_ok=True)

from src.settings import Settings

CONFIG_PATH = Path(MM_PATH, _CONFIG_PATH)

settings_class = Settings(CONFIG_PATH)
settings_class.load_settings()

sources_factory = {
    "MetadataSources": [],
    "CoverSources": []
}


from src.DynamicLibController.extension_manager import load_extensions
try:
    loaded_extensions = load_extensions(EXTENSIONS_DIR)
except Exception:
    logger.exception("Exception loading the extensions")

# Load sources
from src.DynamicLibController import sources_manager
