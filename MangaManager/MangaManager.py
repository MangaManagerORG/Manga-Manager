#!/usr/bin/env python3
import argparse
import logging
import os
import pathlib
import sys
import tkinter as tk
from logging.handlers import RotatingFileHandler

from CommonLib import WebpConverter
from CoverManagerLib import CoverManager
from MetadataManagerLib import MetadataManager
from VolumeManager import VolumeManager

# <Arguments parser>

parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.INFO)

parser.add_argument(
    '--cover',
    help="Launches Cover Manager tool",
    action="store_const", dest="default_selected_tool", const=1,
    default=0)

parser.add_argument(
    '--tagger',
    help="Launches Manga Tagger tool",
    action="store_const", dest="default_selected_tool", const=2
    )

parser.add_argument(
    '--volume',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=3
)
parser.add_argument(
    '--webpConverter',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=5
)

def is_dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


# This one is to be used together with my Windows configuration.
# I have an entry in my contextual menu to run python scripts


parser.add_argument(
    '-p', '--path',
    type=is_dir_path,dest="active_dir_path")

args = parser.parse_args()
# </Arguments parser>


# <Logger>
logger = logging.getLogger()
logging.getLogger('PIL').setLevel(logging.WARNING)
# formatter = logging.Formatter()

PROJECT_PATH = pathlib.Path(__file__).parent
rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/logs/MangaManager.log", maxBytes=5725760,
                                            backupCount=2)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout), rotating_file_handler]
                    # filename='/tmp/myapp.log'
                    )
logger.debug('DEBUG LEVEL - MAIN MODULE')
logger.info('INFO LEVEL - MAIN MODULE')
# </Logger>

tools = [CoverManager, MetadataManager, VolumeManager, "Placeholder", WebpConverter]

def main():
    selected_tool = False
    print("Select Tool")
    print("1 - Cover Setter")
    print("2 - Manga Tagger")
    print("3 - Volume Setter")
    print("5 - Webp Coverter")
    if not args.default_selected_tool:
        while not selected_tool:
            selection = input("Select Number >")
            try:
                selection = int(selection)
            except:
                print("Wrong input. Select the number of the tool")
            selected_tool = True
    else:
        selection = args.default_selected_tool
    print(selection)

    root = tk.Tk()
    # if selection == 3:
    #     print("Not implemented yet")

    selApp = tools[selection-1]
    # logger = selApp.loggerCall()
    app = selApp.App(root)
    app.start_ui()
    app.run()


if __name__ == "__main__":
    main()
