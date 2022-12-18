import logging
from pathlib import Path

# from Extensions.Interface import IExtensionApp

logger = logging.getLogger()
_CONFIG_PATH = "config.ini"
MM_PATH = Path(Path.home(), "MangaManager")
EXTENSIONS_DIR = Path("/Extensions")

# EXTENSIONS_DIR = Path(Path(__file__).parent.parent,"Extensions")


from src.Common.settings import Settings


MM_PATH.mkdir(exist_ok=True,parents=True)
CONFIG_PATH = Path(MM_PATH, _CONFIG_PATH)

settings_class = Settings(CONFIG_PATH)
settings_class.load_settings()


# from .extension_manager import load_extensions
loaded_extensions = []
# try:
#     loaded_extensions = load_extensions(EXTENSIONS_DIR)
# except Exception:
#     logger.exception("Exception loading the extensions")


print("asdsa")