import argparse
import enum
import glob
import logging
import pathlib
import sys

from MetadataManager.MetadataManagerCLI import App as CLIMetadataApp
# from Common.settings import Settings
from MetadataManager.MetadataManagerGUI import App as MetadataApp

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

# rotating_file_handler = RotatingFileHandler(LOGFILE_PATH, maxBytes=5725760,
#
#                                             backupCount=2)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)20s - %(levelname)8s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]  # , rotating_file_handler]
                    # filename='/tmp/myapp.log'
                    )

logger.debug('DEBUG LEVEL - MAIN MODULE')
logger.info('INFO LEVEL - MAIN MODULE')
# <Arguments parser>
class ToolS(enum.Enum):
    METADATA = CLIMetadataApp
    VOLUME = 3
    EPUB2CBZ = 4
    WEBP = 5
    SETTINGS = 6
# ToolS.METADATA.value
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "selected_files",metavar="<path>")
    parser.add_argument(
        '-c', '--cli',
        help="cli mode",
        action="store_const", dest="tool", const=ToolS.METADATA,
        default=logging.INFO)
    args = parser.parse_args()
    if args.tool:
        app = args.tool.value(glob.glob(args.selected_files))
    else:
        app = MetadataApp()
        app.mainloop()
