import argparse
import enum
import glob
import logging
import pathlib
import sys
from logging.handlers import RotatingFileHandler

from src.MangaManager_ThePromidius.Common.errors import NoFilesSelected
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerCLI import App as CLIMetadataApp
# from Common.settings import Settings
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerGUI import App as MetadataApp

# if __name__ == '__main__':
# MetadataManager()
# import test_file


# exit()
PROJECT_PATH = pathlib.Path(__file__).parent
SETTING_PATH = pathlib.Path(PROJECT_PATH, "settings.json")
LOGS_PATH = pathlib.Path(f"{PROJECT_PATH}/logs/")
LOGS_PATH.mkdir(parents=True, exist_ok=True)
LOGFILE_PATH = pathlib.Path(LOGS_PATH, "MangaManager.log")

# Setup Logger
logger = logging.getLogger()
logging.getLogger('PIL').setLevel(logging.WARNING)

rotating_file_handler = RotatingFileHandler(LOGFILE_PATH, maxBytes=5725760,
                                            backupCount=2)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)20s - %(levelname)8s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]  # , rotating_file_handler]
                    # filename='/tmp/myapp.log'
                    )

logger.debug('DEBUG LEVEL - MAIN MODULE')
logger.info('INFO LEVEL - MAIN MODULE')


# <Arguments parser>
class ToolS(enum.Enum):
    NONE = 0
    METADATA = 1
    WEBP = 5

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))

def get_selected_files(glob_path)-> list[str]:
    file_paths = glob.glob(glob_path)
    if not file_paths:
        raise NoFilesSelected()
    return file_paths
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--cli', help="Metadata Editor in CLI mode", action="store", dest="selected_files_cli",
                        metavar="--cli <glob-like-path>", required=False, default=False)
    parser.add_argument('--webp', help="Webp converter in CLI mode", action="store", dest="selected_files_webp",
                        metavar="--webp <glob-like-path>", required=False, default=False)
    args = parser.parse_args()
    if args.selected_files_cli:
        logger.info(f"Starting: CLI Metadata app")
        selected_files = get_selected_files(args.selected_files_cli)
        app = CLIMetadataApp(selected_files)
    elif args.selected_files_webp:
        logger.info(f"Starting: CLI Webp converter app")
        # app = glob.glob(args.selected_files))
        selected_files = get_selected_files(args.selected_files_cli)

    else:
        logger.info(f"Starting: GUI Manga Manager")
        app = MetadataApp()
        app.mainloop()
