#!/usr/bin/env python3
import argparse
import enum
import json
import logging
import os
import pathlib
import platform
import sys
import tkinter as tk
from logging.handlers import RotatingFileHandler
from pathlib import Path

from CommonLib import WebpConverter
from CommonLib.HelperFunctions import create_settings
from ConvertersLib.epub2cbz import epub2cbz
from CoverManagerLib import CoverManager
from MetadataManagerLib import MetadataManager
from VolumeManager import VolumeManager


# <Arguments parser>
class ToolS(enum.Enum):
    COVER = 1
    METADATA = 2
    VOLUME = 3
    EPUB2CBZ = 4
    WEBP = 5
parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.INFO)

parser.add_argument(
    '--cover',
    help="Launches Cover Manager tool",
    action="store_const", dest="default_selected_tool", const=ToolS.COVER,
    default=0)

parser.add_argument(
    '--tagger',
    help="Launches Manga Tagger tool",
    action="store_const", dest="default_selected_tool", const=ToolS.METADATA
)

parser.add_argument(
    '--volume',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=ToolS.VOLUME
)
parser.add_argument(
    '--epub2cbz',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=ToolS.EPUB2CBZ
)
parser.add_argument(
    '--webpConverter',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=ToolS.WEBP
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
    type=is_dir_path, dest="active_dir_path")


# </Arguments parser>


# <Logger>
logger = logging.getLogger()
logging.getLogger('PIL').setLevel(logging.WARNING)
# formatter = logging.Formatter()

PROJECT_PATH = pathlib.Path(__file__).parent
SETTING_PATH = pathlib.Path(PROJECT_PATH, "settings.json")
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
images_path = pathlib.Path(PROJECT_PATH, "Icons")
tools = [CoverManager, MetadataManager, VolumeManager, epub2cbz, WebpConverter]



def load_settings():
    if Path(SETTING_PATH).exists():
        with open(SETTING_PATH, 'r') as settings_json:
            loaded_settings = json.load(settings_json)
    else:
        with open(SETTING_PATH, 'w+') as settings_json:
            loaded_settings = create_settings()
            json.dump(loaded_settings, settings_json, indent=4)

    settings = dict()
    # Library path
    if os.getenv("LIBRARY_FOLDER_PATH") is not None:
        settings["library_folder_path"] = os.getenv("LIBRARY_FOLDER_PATH")
    elif loaded_settings.get("library_folder_path"):
        settings["library_folder_path"] = loaded_settings.get("library_folder_path")
    elif os.path.exists("/manga"):
        settings["library_folder_path"] = "/manga"
    else:
        settings["library_folder_path"] = ""

    if os.getenv("COVER_FOLDER_PATH") is not None:
        settings["cover_folder_path"] = os.getenv("COVER_FOLDER_PATH")
    elif loaded_settings.get("cover_folder_path"):
        settings["cover_folder_path"] = loaded_settings.get("cover_folder_path")
    elif os.path.exists("/covers"):
        settings["cover_folder_path"] = "/covers"
    else:
        settings["cover_folder_path"] = ""

    return settings


class MangaManager:
    settings = None

    def __init__(self, master: tk.Tk):
        self.master = master
        self.settings = load_settings()

    def start_ui(self):
        # build ui
        self.frame_1 = tk.Frame(self.master)
        self.button_cover_editor = tk.Button(self.frame_1)
        self.img_COVER_EDITOR = tk.PhotoImage(file=Path(images_path, 'cover_editor_half_size.png'))
        self.button_cover_editor.configure(image=self.img_COVER_EDITOR, text='Cover Editor',
                                           command=lambda: self.execute(ToolS.COVER))
        self.button_cover_editor.grid(column='0', padx='5', pady='5', row='0')

        self.button_metadata_editor = tk.Button(self.frame_1)
        self.img_METADATA_EDITOR = tk.PhotoImage(file=Path(images_path, 'metadata_editor_half_size.png'))
        self.button_metadata_editor.configure(image=self.img_METADATA_EDITOR, text='Metadata Editor',
                                              command=lambda: self.execute(ToolS.METADATA))
        self.button_metadata_editor.grid(column='1', padx='5', pady='5', row='0')

        self.button_volume_editor = tk.Button(self.frame_1)
        self.img_VOLUME_EDITOR = tk.PhotoImage(file=Path(images_path, 'volume_editor_half_size.png'))
        self.button_volume_editor.configure(image=self.img_VOLUME_EDITOR, text='Volume Editor',
                                            command=lambda: self.execute(ToolS.VOLUME))
        self.button_volume_editor.grid(column='3', row='0')

        self.button_webp_converter = tk.Button(self.frame_1)
        self.img_WEBP_CONVERTER = tk.PhotoImage(file=Path(images_path, 'webp_converter_half_size.png'))
        self.button_webp_converter.configure(image=self.img_WEBP_CONVERTER, text='Webp Converter',
                                             command=lambda: self.execute(ToolS.WEBP))
        self.button_webp_converter.grid(column='0', padx='5', pady='5', row='1')

        self.button_epub2cbz = tk.Button(self.frame_1)
        self.img_EPUB2CBZ = tk.PhotoImage(file=Path(images_path, 'epub-2_cbz_half_size.png'))
        self.button_epub2cbz.configure(image=self.img_EPUB2CBZ, text='Epub 2 Cbz',
                                       command=lambda: self.execute(ToolS.EPUB2CBZ))
        self.button_epub2cbz.grid(column='1', row='1')

        self.frame_1.configure(height='200', padx='60', pady='60', width='200')
        self.frame_1.pack(anchor='center', expand='true', fill='both', side='top')
        self.frame_1.grid_anchor('center')

        # Main widget
        self.mainwindow = self.master

    def execute(self, tool: ToolS):
        root2 = tk.Toplevel(self.mainwindow)
        if platform.system() == "Linux":
            root2.attributes('-zoomed', True)
        elif platform.system() == "Windows":
            root2.state('zoomed')

        selApp = tools[tool.value - 1]
        subapp = selApp.App(root2, settings=self.settings)
        subapp.start_ui()
        subapp.run()

    def run(self):
        self.mainwindow.mainloop()


if __name__ == "__main__":
    args = parser.parse_args()

    if not args.default_selected_tool:
        master_root = tk.Tk()
        master_root.title("Manga Manager")

        app = MangaManager(master_root)
        app.start_ui()
        app.run()
    else:
        root = tk.Tk()
        if platform.system() == "Linux":
            root.attributes('-zoomed', True)
        elif platform.system() == "Windows":
            root.state('zoomed')

        selApp = tools[args.default_selected_tool.value - 1]
        subapp = selApp.App(root, settings=load_settings())
        subapp.start_ui()
        subapp.run()
