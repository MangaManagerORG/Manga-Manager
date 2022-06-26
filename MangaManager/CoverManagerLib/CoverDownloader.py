import logging
import os
import pathlib
import urllib.request

import requests

from CommonLib.ProgressBarWidget import ProgressBar
from CommonLib.HelperFunctions import create_settings
from CoverManagerLib.errors import UrlNotFound

logger = logging.getLogger(__name__)
ScriptDir = os.path.dirname(__file__)

url = "https://api.mangadex.org"

if __name__ == '__main__':
    directory = input("Folder Name Here: ")  # The folder of the cover
    parent_dir = os.getcwd()  # Returs the folder where manga-manager folder is as base path change this to set base path

    path = os.path.join(parent_dir, directory)

    os.mkdir(path)
    manga_id = input("Mangadex Manga ID Here: ")

    data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit": 50}
    r = requests.get(f"{url}/cover", params=data)

    r_json = r.json()

    for cover_data in r_json.get("data"):
        data = {"includes[]": ["cover_art"],
                "order": {
                    "createdAt": "asc",
                    "updatedAt": "asc",
                    "volume": "asc"
                }
                }
        cover_id = cover_data.get('id')
        cover_titles = list(filter(lambda p: p.get("type") == "manga", cover_data.get("relationships")))[0]. \
            get("attributes").get("title")

        normalized_manga_name = (cover_titles.get("jp") or cover_titles.get("en"))
        cover_filename = cover_data.get("attributes").get("fileName")
        cover_volume = cover_data.get("attributes").get("volume")
        cover_loc = cover_data.get("attributes").get("locale")
        filename, file_extension = os.path.splitext(cover_filename)
        image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
        print(image_url)
        urllib.request.urlretrieve(image_url,
                                   pathlib.Path(directory,
                                                f"Cover_Vol.{str(cover_volume).zfill(2)}_{cover_loc}{file_extension}"))

else:  # Called from cover manager

    import tkinter as tk


    class App:
        def __init__(self, master: tk.Toplevel, settings=None):
            self.master = master
            self.settings = settings

        def start_ui(self):
            # build ui
            self.frame_1 = tk.Frame(self.master)
            self.frame_3 = tk.Frame(self.frame_1)
            self.label_1 = tk.Label(self.frame_3)
            self.label_1.configure(text='INSERT MANGADEX MANGA ID / URL')
            self.label_1.pack(side='top')
            self.entry_1 = tk.Entry(self.frame_3)
            self.entry_1.configure(width='80')
            self.entry_1.pack(side='top')
            self.button_1 = tk.Button(self.frame_3)
            self.button_1.configure(text='Download Covers to:')
            self.button_1.pack(side='top')
            self.label_2 = tk.Label(self.frame_3)
            self.label_2.configure(text=str(pathlib.Path(self.settings.get('cover_folder_path'), '<Manga Name>')))
            self.label_2.pack(side='top')
            self.frame_3.configure(height='400', width='400')
            self.frame_3.pack(padx='50', pady='50', side='top')
            self.frame_1.configure(height='600', width='600')
            self.frame_1.pack(anchor='center', expand='true', fill='both', side='top')

            # Main widget
            self.mainwindow = self.frame_1

        def run(self):
            self.master.mainloop()
