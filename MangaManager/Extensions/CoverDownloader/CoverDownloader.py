# import tkinter
# from idlelib.tooltip import Hovertip
# from idlelib.tooltip import Hovertip
import asyncio
import logging
import urllib.request
import os
import platform
import subprocess
from enum import StrEnum
from pathlib import Path
from tkinter import Frame, Label, StringVar
from tkinter.ttk import Entry, Button, Frame
import slugify
import requests

from Extensions.CoverDownloader.CoverData import CoverData
from Extensions.CoverDownloader.MangaDex import parse_mangadex_id
from Extensions.CoverDownloader.exceptions import UrlNotFound
from Extensions.IExtensionApp import IExtensionApp
from MangaManager.MetadataManager.GUI.widgets import ProgressBarWidget
# from src.MetadataManager.GUI.tooltip import ToolTip
from MangaManager.Settings import Settings, SettingHeading, SettingSection, SettingControl, SettingControlType

logger = logging.getLogger()
def get_cover_from_source_dummy() -> list:
    ...


class CoverDownloaderSetting(StrEnum):
    ForceOverwrite = "force_overwrite" #  If existing covers should be re-downloaded and overwritten
class CoverDownloader(IExtensionApp):
    name = "Cover Downloader"
    embedded_ui = True

    def init_settings(self):

        self.settings = [
            SettingSection(self.name,self.name,[
                SettingControl(
                    key=CoverDownloaderSetting.ForceOverwrite,
                    name="Force Overwrite",
                    control_type=SettingControlType.Bool,
                    value=False,
                    tooltip="Enable if existing covers should be re-downloaded and overwritten"
                )
            ])
        ]
        super().init_settings()

    @property
    def output_folder(self):
        return Settings().get(SettingHeading.Main, 'covers_folder_path')

    def serve_gui(self):
        self.url_var = StringVar(name="mdex_cover_url")
        self.url_var.trace("w",self.get_series_data)

        self.dest_path_var = StringVar(name="dest_path",value=str(Path((self.output_folder or Path(Path.home(),"Pictures","Manga Covers")),
                                                     '<Manga Name Folder>')))
        Label(self.master,text="MangaManager will download all availabe images from").pack()
        # self.frame_3 = Frame(frame1)
        Label(self.master, text='MANGADEX MANGA ID / URL').pack(side='top')
        Entry(master=self.master,textvariable=self.url_var).pack(side='top')

        Label(self.master, text="to the folder:").pack()
        label_path = Label(self.master,textvariable=self.dest_path_var)
        label_path.pack(pady="10 30", side='top')

        self.button_1 = Button(self.master, text='Correct! Start!', state="disabled", command=self.process_download)
        self.button_1.pack(side='top')
        self.button_explorer = Button(self.master, text='Open explorer', command=self.open_explorer)
        self.pb = ProgressBarWidget(self.master)

    def process_download(self):
        try:
            self.download()
        except Exception as e:
            logger.exception("Error downloading")
        finally:
            self.button_1.configure(text="DONE", state="disabled")
            self.show_open_explorer_btn()

    def show_open_explorer_btn(self):
        self.button_explorer.pack(side='top')
    def hide_open_explorer_btn(self):
        self.button_explorer.pack_forget()

    def open_explorer(self):

        path = self.dest_path_var.get()
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        ...





    def get_series_data(self,*_):
        mdex_id = parse_mangadex_id(self.url_var.get())
        if mdex_id is None:
            return
        self.hide_open_explorer_btn()
        self.button_1.configure(text="Correct! Start", state="normal")
        # self.show_open_explorer_btn()

        logger.debug(f"Parsed mdex id: '{mdex_id}'")
        data = {"manga[]": [mdex_id], "includes[]": ["manga"], "limit": 50}
        # Request the list of covers in the prrovided manga
        r = requests.get(f"https://api.mangadex.org/cover", params=data)

        if r.status_code != 200:
            logger.warning(f"Page responded with {r.status_code}",extra={"url":r.url})
            return
            # raise UrlNotFound(r.url)
        data = r.json().get("data")
        cover_attributes = data[0].get("relationships")[0].get("attributes")

        # Get title
        ja_title = list(filter(lambda p: p.get("ja-ro"),
                               cover_attributes.get("altTitles")))
        if ja_title:
            ja_title = ja_title[0].get("ja-ro")
        full_name = (ja_title or cover_attributes.get("title").get("en"))
        normalized_manga_name = slugify.slugify(full_name[:50])

        # Get final path where images will be saved
        self.destination_dirpath = Path((self.output_folder or Path(Path.home(), "Pictures", "Manga Covers")),normalized_manga_name)

        # Update ui path
        self.dest_path_var.set(str(self.destination_dirpath))
        self.update()
        self.cur_id = mdex_id
        self.cur_data = data
    def download(self):
        self.pb.start(len(self.cur_data))
        self.destination_dirpath.mkdir(parents=True, exist_ok=True)
        for i,cover_data in enumerate(self.cur_data):
            cover = CoverData().from_cover_data(cover_data)
            image_path = Path(self.destination_dirpath, cover.dest_filename)
            if not image_path.exists() or Settings().get(self.name,CoverDownloaderSetting.ForceOverwrite):
                image_url = f"https://mangadex.org/covers/{self.cur_id}/{cover.source_filename}"

                urllib.request.urlretrieve(image_url, image_path)
                logger.debug(f"Downloaded '{image_path}'")
            else:
                logger.info(f"Skipped https://mangadex.org/covers/{self.cur_id}/{cover.source_filename} -> Already exists")
                self.pb.increase_failed()
            self.pb.increase_processed()
        self.pb.stop()
        self.update()
