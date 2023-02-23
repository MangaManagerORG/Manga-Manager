from __future__ import annotations

import io
import logging
import zipfile
from typing import IO

from PIL import ImageTk, Image

from src.Common.errors import BadZipFile
from src.Common.utils import obtain_cover_filename
from .CoverActions import CoverActions
from .ArchiveFile import ArchiveFile
logger = logging.getLogger("LoadedCInfo")
COMICINFO_FILE = 'ComicInfo.xml'
COMICINFO_FILE_BACKUP = 'Old_ComicInfo.xml.bak'
COVER_NAME = "!0000_Cover"
BACKCOVER_NAME = "9999_Back"
_LOG_TAG_WEBP = "Convert Webp"
_LOG_TAG_WRITE_META = 'Write Meta'
_LOG_TAG_RECOMPRESSING = "Recompressing"
move_to_value = ""




class LoadedFileCoverData:
    cover_filename: str | None = None
    cover_cache: ImageTk.PhotoImage = None

    backcover_filename: str | None = None
    backcover_cache: ImageTk.PhotoImage = None

    _cover_action: CoverActions | None = None
    # Path to the new cover selected by the user
    _new_cover_path: str | None = None
    new_cover_cache: ImageTk.PhotoImage | None = None
    # Path to the new backcover selected by the user
    _backcover_action: CoverActions | None = None
    _new_backcover_path: str | None = None
    new_backcover_cache: ImageTk.PhotoImage | None = None

    def get_cover_cache(self, is_backcover=False) -> ImageTk.PhotoImage | None:
        if self._cover_action is None:
            return self.backcover_cache if is_backcover else self.cover_cache
        else:
            return self.new_backcover_cache if is_backcover else self.new_cover_cache

    @property
    def cover_action(self):
        return self._cover_action

    @cover_action.setter
    def cover_action(self, value: CoverActions):
        if value == CoverActions.RESET:
            self._new_cover_path = None
            self.new_cover_cache = None
            self._cover_action = None
        else:
            self._cover_action = value
            self.has_changes = True

    @property
    def backcover_action(self):
        return self._backcover_action

    @backcover_action.setter
    def backcover_action(self, value: CoverActions):
        if value == CoverActions.RESET:
            self._new_backcover_path = None
            self.new_backcover_cache = None
            self._backcover_action = None
        else:
            self._backcover_action = value
            self.has_changes = True

    @property
    def new_cover_path(self):
        return self._new_cover_path

    @new_cover_path.setter
    def new_cover_path(self, path):
        if path is None:
            self._new_cover_path = None
            self.new_cover_cache = None
            return
        image = Image.open(path)
        image = image.resize((190, 260), Image.NEAREST)
        try:
            self.new_cover_cache = ImageTk.PhotoImage(image)
        except RuntimeError:
            self.new_cover_cache = None
        self._new_cover_path = path

    @property
    def new_backcover_path(self):
        return self._new_backcover_path

    @new_backcover_path.setter
    def new_backcover_path(self, path):
        if path is None:
            self._new_backcover_path = None
            self.new_backcover_cache = None
            return
        image = Image.open(path)
        image = image.resize((190, 260), Image.NEAREST)
        try:
            self.new_backcover_cache = ImageTk.PhotoImage(image)
        except RuntimeError:
            self.new_cover_cache = None
        self._new_backcover_path = path

    def load_cover_info(self, load_images=True):
        try:
            with ArchiveFile(self.file_path,'r') as self.archive:
                cover_info = obtain_cover_filename(self.archive.namelist())
                if not cover_info:
                    return
                self.cover_filename, self.backcover_filename = cover_info

                if not self.cover_filename:
                    logger.warning(f"[{'CoverParsing':13s}] Couldn't parse any cover")
                else:
                    logger.info(f"[{'CoverParsing':13s}] Cover parsed as '{self.cover_filename}'")
                    if load_images:
                        self.get_cover_image_bytes()

                if not self.backcover_filename:
                    logger.warning(f"[{'CoverParsing':13s}] Couldn't parse any back cover")
                else:
                    logger.info(f"[{'CoverParsing':13s}] Back Cover parsed as '{self.backcover_filename}'")
                    if load_images:
                        self.get_cover_image_bytes(back_cover=True)
        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        except Exception:
            logger.exception(f"Unhandled error loading cover info for file: '{self.file_name}'")
        return self

    def get_cover_image_bytes(self, resized=False, back_cover=False) -> IO[bytes] | None:
        """
        Opens the cbz and returns the bytes for the parsed cover image
        :return:
        """
        if not self.file_path or not self.cover_filename:
            return None
        if back_cover and not self.backcover_filename:
            return None
        try:
            with ArchiveFile(self.file_path,'r') as zin:
                img_bytes = zin.open(self.cover_filename if not back_cover else self.backcover_filename)
                image = Image.open(img_bytes)
                image = image.resize((190, 260), Image.NEAREST)
                try:
                    if not back_cover:
                        self.cover_cache = ImageTk.PhotoImage(image)
                    else:
                        self.backcover_cache = ImageTk.PhotoImage(image)
                except RuntimeError as e:
                    print(e)  # Random patch for some error when running tests
                    ...
                if resized:
                    return io.BytesIO(image.tobytes())
            return img_bytes
        except Exception:
            logger.exception(f"Error getting cover bytes. BackCover = {'True' if back_cover else 'False'} File: {self.file_name}")