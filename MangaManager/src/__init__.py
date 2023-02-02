import logging
from os import environ
from os.path import abspath
from pathlib import Path

import requests  # Needed for sources to work

requests.s3423 = ""  # Random patch so import does not get cleaned up

from pkg_resources import resource_filename

logger = logging.getLogger()
_CONFIG_PATH = "config.ini"
MM_PATH = Path(Path.home(), "MangaManager")
MM_PATH.mkdir(exist_ok=True, parents=True)
DEV_BUILD = f'{environ.get("$$_ENV_DEVELOPMENT_MM_$$")}'
DEV_BUILD = DEV_BUILD.lower() == "true"

sub_mm_path = abspath(resource_filename(__name__, '../'))
logger.error(f"sub_mm_path:{sub_mm_path}")
EXTENSIONS_DIR = Path(sub_mm_path, "Extensions")
EXTENSIONS_DIR.mkdir(exist_ok=True)

SOURCES_DIR = Path(sub_mm_path, "ExternalSources")
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
