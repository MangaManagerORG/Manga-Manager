from dataclasses import dataclass
from tkinter import PhotoImage


@dataclass
class cover_process_item_info:
    zipFilePath: str
    coverFilePath: str
    coverFileName: str
    coverFileFormat: str
    coverOverwrite: bool
    coverDelete: bool
    imageObject: PhotoImage

    def __init__(self, cbz_file, cover_path=None, cover_name=None, cover_format=None, coverOverwrite=False, coverDelete=False):
        # self.function = function
        self.zipFilePath = cbz_file
        self.coverFilePath = cover_path
        self.coverFileName = cover_name
        self.coverFileFormat = cover_format
        self.coverOverwrite = coverOverwrite
        self.coverDelete = coverDelete