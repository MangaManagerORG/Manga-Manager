#!/usr/bin/env python3
import tkinter as tk
import argparse
import logging
import sys
import os
from MangaTaggerLib import MangaTagger
from CoverManagerLib import CoverManager
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
logger = logging.getLogger(__name__)
logging.getLogger('PIL').setLevel(logging.WARNING)
formatter = logging.Formatter()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]
                    # filename='/tmp/myapp.log'
                    )
logger.debug('DEBUG LEVEL - MAIN MODULE')
logger.info('INFO LEVEL - MAIN MODULE')
# </Logger>

tools = [CoverManager, MangaTagger, VolumeManager]

def main():
    selected_tool = False
    print("Select Tool")
    print("1 - Cover Setter")
    print("2 - Manga Tagger")
    print("3 - Volume Setter")
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
    selApp.loggerCall()
    app = selApp.App(root)
    app.start_ui()
    app.run()


if __name__ == "__main__":
    main()
