import logging
import os
import pathlib
import urllib.request

import requests

from CommonLib.HelperFunctions import create_settings, cleanFilename, check_url_isImage
from CommonLib.ProgressBarWidget import ProgressBar
from CoverManagerLib.errors import UrlNotFound

logger = logging.getLogger(__name__)
ScriptDir = os.path.dirname(__file__)

if __name__ != '__main__':  # Called from cover manager
    import tkinter as tk
    from tkinter.filedialog import askdirectory


class App:
    def __init__(self, master: 'tk.Toplevel' = None, settings=None):
        self.master = master
        self.settings = settings
        if settings is None:
            self.settings = create_settings()
        self._progressbar_frame = None
        self._initialized_UI = False

    def start_ui(self):
        """
        Build the gui
        :return:
        """
        # build ui
        if not self.master:
            return Exception("Tried to initialize ui with no master window")
        self.frame_1 = tk.Frame(self.master)
        self.frame_3 = tk.Frame(self.frame_1)
        self.label_1 = tk.Label(self.frame_3)
        self.label_1.configure(text='INSERT MANGADEX MANGA ID / URL')
        self.label_1.pack(side='top')
        self.entry_1 = tk.Entry(self.frame_3)
        self.entry_1.configure(width='80')
        self.entry_1.pack(side='top')
        self.button_1 = tk.Button(self.frame_3)
        self.button_1.configure(text='Download Covers to:', command=self._process)
        self.button_1.pack(side='top')
        self.label_2 = tk.Label(self.frame_3)
        self.label_2.configure(text=str(pathlib.Path((self.settings.get('cover_folder_path') or os.getcwd()),
                                                     '<Manga Name Folder>')))
        self.label_2.pack(pady="10 30", side='top')

        self.button_2 = tk.Button(self.frame_3)
        self.button_2.configure(text="Change output folder", command=self.set_output_folder)
        self.button_2.pack(side='top')

        # self.button_3 = tk.Button(self.frame_3)
        # self.button_3.configure(text="Open output folder", command=self.open_output_folder)
        # self.button_3.pack(side="top")

        self._progressbar_frame = tk.Frame(self.frame_3)
        self._progressbar_frame.configure(height='160', width='390')

        self._progressbar_frame.pack(anchor='e', expand='true', fill='both', padx='30', pady='15', side='right')

        self.frame_3.configure(height='400', width='400')
        self.frame_3.pack(padx='50', pady='50', side='top')
        self.frame_1.configure(height='600', width='600')
        self.frame_1.pack(anchor='center', expand='true', fill='both', side='top')

        # Main widget
        self.mainwindow = self.frame_1
        self._initialized_UI = True

    def run(self):
        """
        Only call this method once the ui is initialized else not needed
        :return:
        """
        self.master.mainloop()

    def set_output_folder(self, output_folder=None):
        if output_folder:
            self.settings["cover_folder_path"] = output_folder

        elif self._initialized_UI:
            if not output_folder:
                self.settings["cover_folder_path"] = askdirectory(parent=self.master,
                                                                  initialdir=self.settings.get("cover_folder_path"))
            self.label_2.configure(text=str(pathlib.Path(self.settings.get('cover_folder_path'), '<Manga Name>')))
        else:
            self.settings["cover_folder_path"] = ""
    #
    # def open_output_folder(self):
    #     print(f"'{(self.settings.get('cover_folder_path') or os.getcwd())}'")
    #     os.system(f"start '{(self.settings.get('cover_folder_path') or os.getcwd())}'")
    #

    def _process(self):
        if self._initialized_UI:
            manga_id = self.parse_mangadex_id(self.entry_1.get())
        self.download_covers(manga_id, self.settings.get('cover_folder_path'))

    def parse_mangadex_id(self, value) -> str:
        """
        Accepts a mangadex id or URL
        :param value:
        :return: mangadex managa id
        """

        if "https://mangadex.org/title/" in value:
            value = value.replace("https://mangadex.org/title/", "").split("/")[0]
        return value

    def download_covers(self, manga_id, forceOverwrite=False, test_run=False):
        """
        Downloads the covers from manga_id from mangadex.
        If the cover is already downloaded it won't re-download

        :param manga_id: The manga id only.
        :param cover_folder: The folder where the series folder will be created.
        :param forceOverwrite: If existing covers should be re-downloaded and overwritten
        :param test_run: Value to make a dry run where it asserts that each cover url is valid
        :return:
        """

        data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit": 50}
        # Request the list of covers in the provided manga
        r = requests.get(f"https://api.mangadex.org/cover", params=data)

        if r.status_code == 400:
            raise UrlNotFound(r.url)

        r_json = r.json()
        cover_attributes = r_json.get("data")[0].get("relationships")[0].get("attributes")

        ja_title = list(filter(lambda p: p.get("ja-ro"),
                               cover_attributes.get("altTitles")))
        if ja_title:
            ja_title = ja_title[0].get("ja-ro")

        normalized_manga_name = (ja_title or cover_attributes.get("title").get("en"))

        destination_dirpath = pathlib.Path(self.settings.get('cover_folder_path'), cleanFilename(
            normalized_manga_name))  # The covers get stored in their own series folder inside the covers directory
        if not test_run:
            destination_dirpath.mkdir(parents=True, exist_ok=True)
        total = len(r_json.get("data"))
        self.progressbar = ProgressBar(self._initialized_UI, self._progressbar_frame, total)

        for i, cover_data in enumerate(r_json.get("data")):
            try:

                cover_filename = cover_data.get("attributes").get("fileName")
                filename, file_extension = os.path.splitext(cover_filename)

                cover_volume = cover_data.get("attributes").get("volume")
                cover_loc = cover_data.get("attributes").get("locale")

                destination_filename = f"Cover_Vol.{str(cover_volume).zfill(2)}_{cover_loc}{file_extension}"
                destination_filepath = pathlib.Path(destination_dirpath, destination_filename)
                if (not destination_filepath.exists() or forceOverwrite) and not test_run:
                    image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
                    urllib.request.urlretrieve(image_url, destination_filepath)
                    logger.debug(f"Downloaded {destination_filename}")
                elif test_run:
                    image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
                    print(f"Asserting if valid url: '{image_url}' ")
                    return check_url_isImage(image_url)
                else:
                    logger.info(f"Skipped 'https://mangadex.org/covers/{manga_id}/{cover_filename}' -> Already exists")
                self.progressbar.increaseCount()
            except Exception as e:
                logger.error(e)
                self.progressbar.increaseError()
        logger.info(f"Files saved to: '{destination_dirpath}'")
        print(f"Files saved to: '{destination_dirpath}'")


if __name__ == '__main__':
    # TODO: process arguments with argparse as other tools
    covers_path = pathlib.Path(input("Cover Directory Path: "))  # The folder where the covers are stored
    app = App()
    app.set_output_folder(covers_path)
    mangadex_url = input("Mangadex serie url/id: ")
    mangadex_id = app.parse_mangadex_id(mangadex_url)

    app.download_covers(mangadex_id)
