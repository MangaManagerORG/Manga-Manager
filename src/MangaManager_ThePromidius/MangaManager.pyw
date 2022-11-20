import logging
import pathlib
import sys

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

if __name__ == '__main__':
    app = MetadataApp()
    app.mainloop()
