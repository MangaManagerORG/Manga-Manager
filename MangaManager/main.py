import argparse
import enum
import glob
import logging
from pathlib import Path

from logging_setup import add_trace_level, setup_logging

add_trace_level()

parser = argparse.ArgumentParser()

############
# Logging arguments
###########
parser.add_argument(
    '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.INFO)
parser.add_argument(
    '--trace',
    help="Prints INSANE amount of debug statements",
    action="store_const", dest="loglevel", const=logging.TRACE,
)

parser.add_argument('-d', help="Debug Level", action="store", dest="selected_files_cli",
                    metavar="--cli <glob-like-path>", required=False, default=False)

parser.add_argument('--cli', help="Metadata Editor in CLI mode", action="store", dest="selected_files_cli",
                    metavar="--cli <glob-like-path>", required=False, default=False)

parser.add_argument('--webp', help="Webp converter in CLI mode", action="store", dest="selected_files_webp",
                    metavar="--webp <glob-like-path>", required=False, default=False)
args = parser.parse_args()

# Setup logger
mm_path = Path(Path.home(), "MangaManager")
mm_path.mkdir(exist_ok=True, parents=True)
LOGS_PATH = Path(f"{mm_path}/logs/")
LOGS_PATH.mkdir(parents=True, exist_ok=True)
LOGFILE_PATH = Path(LOGS_PATH, "MangaManager.log")
setup_logging(LOGFILE_PATH, args.loglevel)
logger = logging.getLogger()

from src.Settings.Settings import Settings
# Create initial ini with defaults else load existing
Settings().load()
from src.Common.errors import NoFilesSelected
from src.MetadataManager.MetadataManagerCLI import App as CLIMetadataApp
from src.__version__ import __version__ as version



# <Arguments parser>


class ToolS(enum.Enum):
    NONE = 0
    METADATA = 1
    WEBP = 5

    @classmethod
    def list(cls):
        return list(map(lambda c: c.name, cls))


def get_selected_files(glob_path) -> list[str]:
    file_paths = glob.glob(glob_path)
    if not file_paths:
        raise NoFilesSelected()
    return file_paths




if __name__ == '__main__':
    if args.selected_files_cli:
        logger.info(f"Starting: CLI Metadata app")
        selected_files = get_selected_files(args.selected_files_cli)
        app = CLIMetadataApp(selected_files)
    elif args.selected_files_webp:
        logger.info(f"Starting: CLI Webp converter app")
        # app = glob.glob(args.selected_files))
        selected_files = get_selected_files(args.selected_files_cli)

    else:
        logger.info(f"Starting: GUI Manga Manager v{version}. Welcome")
        from src.MetadataManager import execute_gui
        execute_gui()
