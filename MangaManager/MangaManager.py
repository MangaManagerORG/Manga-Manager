#!/usr/bin/env python3
import argparse
import enum
import logging
import os
import pathlib
import platform
import sys
import tkinter
import tkinter as tk
from logging.handlers import RotatingFileHandler
from pathlib import Path

from CommonLib import WebpConverter
from ConvertersLib.epub2cbz import epub2cbz
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
    '--epub2cbz',
    help="Launches volume Manager tool",
    action="store_const", dest="default_selected_tool", const=4
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
images_path = pathlib.Path(PROJECT_PATH, "Icons")
tools = [CoverManager, MetadataManager, VolumeManager, epub2cbz, WebpConverter]


class ToolS(enum.Enum):
    COVER = 1
    METADATA = 2
    VOLUME = 3
    EPUB2CBZ = 4
    WEBP = 5


class MangaManager():
    def __init__(self):
        ...

    def start_ui(self, master: tkinter.Tk = None):
        # build ui
        self.frame_1 = tk.Frame(master)
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
        self.mainwindow = master

    def execute(self, tool: ToolS):
        root2 = tk.Toplevel(self.mainwindow)
        if platform.system() == "Linux":
            root2.attributes('-zoomed', True)
        elif platform.system() == "Windows":
            root2.state('zoomed')

        selApp = tools[tool.value - 1]
        # logger = selApp.loggerCall()
        app = selApp.App(root2)
        app.start_ui()
        app.run()

    def run(self):
        self.mainwindow.mainloop()


# def main():
# selected_tool = False
# #
# # self.frame_1 = tk.Frame(master)
# # self.button_2 = tk.Button(self.frame_1)
# # self.img_COVER_EDITOR = tk.PhotoImage(file='COVER_EDITOR.png')
# # self.button_2.configure(image=self.img_COVER_EDITOR, text='button_2')
# # #
# # print("Select Tool")
# # print("1 - Cover Setter")
# # print("2 - Manga Tagger")
# # print("3 - Volume Setter")
# # print("4 - Epub to CBZ converter")
# # print("5 - Webp Converter")
# # args = parser.parse_args()
# # if not args.default_selected_tool:
# #     while not selected_tool:
# #         selection = input("Select Number >")
# #         try:
# #             selection = int(selection)
# #         except:
# #             print("Wrong input. Select the number of the tool")
# #         selected_tool = True
# # else:
# #     selection = args.default_selected_tool
# # print(selection)
#
# root = tk.Toplevel(self.root())
# if platform.system() == "Linux":
#     root.attributes('-zoomed', True)
# elif platform.system() == "Windows":
#     root.state('zoomed')
#
# # root.geometry("%dx%d" % (root.winfo_width(), root.winfo_height()))
# # root.geometry("")
# # if selection == 3:
# #     print("Not implemented yet")
#
# selApp = tools[selection - 1]
# # logger = selApp.loggerCall()
# app = selApp.App(root)
# app.start_ui()
# app.run()


if __name__ == "__main__":
    master_root = tk.Tk()
    app = MangaManager()
    app.start_ui(master_root)
    app.run()
