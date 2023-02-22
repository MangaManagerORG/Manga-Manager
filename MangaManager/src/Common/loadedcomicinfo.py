from __future__ import annotations

import copy
import enum
import io
import logging
import os
import tempfile
import zipfile
from typing import IO

from PIL import Image, ImageTk
from lxml.etree import XMLSyntaxError

from common.models import ComicInfo
from src.Common.errors import BadZipFile
from src.Common.utils import IS_IMAGE_PATTERN, convert_to_webp
from src.Common.utils import obtain_cover_filename, get_new_webp_name

logger = logging.getLogger("LoadedCInfo")

COMICINFO_FILE = 'ComicInfo.xml'
COMICINFO_FILE_BACKUP = 'Old_ComicInfo.xml.bak'

COVER_NAME = "!0000_Cover"
BACKCOVER_NAME = "9999_Back"

_LOG_TAG_WEBP = "Convert Webp"
_LOG_TAG_WRITE_META = 'Write Meta'
_LOG_TAG_RECOMPRESSING = "Recompressing"


class CoverActions(enum.Enum):
    RESET = 0  # Cancel current selected action
    REPLACE = 1
    DELETE = 2
    APPEND = 3


class LoadedFileMetadata:

    _cinfo_object: ComicInfo
    original_cinfo_object: ComicInfo
    # Used to keep original state after being loaded for the first time. Useful to undo sesion changes
    original_cinfo_object_before_session: ComicInfo | None = None

    @property
    def cinfo_object(self):
        return self._cinfo_object

    @cinfo_object.setter
    def cinfo_object(self, value: ComicInfo):
        self._cinfo_object = value

    @property
    def volume(self):
        if self.cinfo_object:
            return self.cinfo_object.volume

    @property
    def chapter(self):
        if self.cinfo_object:
            return self.cinfo_object.number

    @volume.setter
    def volume(self, value):
        self.cinfo_object.volume = value

    @chapter.setter
    def chapter(self, value):
        self.cinfo_object.number = value

    def _load_metadata(self):

        """
        Reads the metadata from the ComicInfo.xml at root level
        :raises CorruptedComicInfo If the metadata file exists but can't be parsed
        :return:
        """
        LOG_TAG = f"[{'Reading Meta':13s}] "
        try:
            # If Comicinfo is not at root try to grab any ComicInfo.xml in the file
            if "ComicInfo.xml" not in self.archive.namelist():
                cinfo_file = [filename.endswith(COMICINFO_FILE) for filename in self.archive.namelist()][
                                 0] or COMICINFO_FILE
            else:
                cinfo_file = COMICINFO_FILE
                self.is_cinfo_at_root = True
            xml_string = self.archive.read(cinfo_file).decode('utf-8')
            self.has_metadata = True
        except KeyError:
            xml_string = ""

        if xml_string:
            try:
                self.cinfo_object = ComicInfo.from_xml(xml_string)
            except XMLSyntaxError as e:
                logger.warning(LOG_TAG + f"Failed to parse XML due to a syntax error:\n{e}")
            except Exception:
                logger.exception(f"[{'Reading Meta':13s}] Unhandled error reading metadata."
                                 f" Please create an issue for further investigation")
                raise
            logger.debug(LOG_TAG + "Successful")
            self.original_cinfo_object_before_session = copy.copy(self.cinfo_object)
        else:
            self.cinfo_object = ComicInfo()
            logger.info(LOG_TAG + "No metadata file was found.A new file will be created")
        self.original_cinfo_object = copy.copy(self.cinfo_object)
        self.original_cinfo_object_before_session = copy.copy(self.cinfo_object)

    def reset_metadata(self):
        """
        Returns the metadata to the first state of loaded cinfo
        """
        self.cinfo_object = self.original_cinfo_object


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
            with zipfile.ZipFile(self.file_path, 'r') as self.archive:
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
            with zipfile.ZipFile(self.file_path, 'r') as zin:
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


class LoadedComicInfo(LoadedFileMetadata, LoadedFileCoverData):
    """
        Helper class that loads the info that is required by the tools

        file_path : str
            Path of the file
        cinfo_object : ComicInfo
            The class where the metadata is stored
        cover_filename : str
            The filename of the image that gets parsed as series cover
        has_metadata : bool
            If false, we only need to append metadata.
            No need to back up ComicInfo.xml because it doesn't exist
        volume : int
            The volume from the metadata. If not set then it tries to parse from filename
        chapter : str
            The volume from the metadata. If not set then it tries to parse from filename
        """

    file_path: str

    has_metadata: bool = False
    is_cinfo_at_root: bool = False

    has_changes = False
    changed_tags = []

    def __init__(self, path, comicinfo: ComicInfo = None, load_default_metadata=True):
        """

        :param path:
        :param comicinfo: The data class to be applied
        :raises BadZipFile: The file can't be read or is not a valid zip file
        """

        self.file_path = path or None
        self.file_name = None if path is None else os.path.basename(path)
        logger.info(f"[{'Opening File':13s}] '{self.file_name}'")
        self.cinfo_object = comicinfo
        if load_default_metadata:
            self.load_metadata()

    ###############################
    # LOADING METHODS
    ###############################

    def load_all(self):
        try:
            # Fixme: skip folders
            # Update: 05-01-23 At this point i don't remember why the fix me. I'm leaving it there.
            with zipfile.ZipFile(self.file_path, 'r') as self.archive:
                self.load_cover_info()
                if not self.cinfo_object:
                    self._load_metadata()

        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        return self

    def load_metadata(self):
        try:
            with zipfile.ZipFile(self.file_path, 'r') as self.archive:
                if not self.cinfo_object:
                    self._load_metadata()
        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        return self

    ###############################
    # PROCESSING METHODS
    ###############################

    # INTERFACE METHODS
    def write_metadata(self, auto_unmark_changes=False):
        # print(self.cinfo_object.__dict__)
        logger.debug(f"[{'BEGIN WRITE':13s}] Writing metadata to file '{self.file_path}'")
        # logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] ComicInfo file found in old file")
        try:
            self._process(write_metadata=True)
        finally:
            if auto_unmark_changes:
                self.has_changes = False

    def convert_to_webp(self):
        logger.debug(f"[{'BEGIN CONVERT':13s}] Converting to webp: '{self.file_path}'")
        self._process(do_convert_to_webp=True)

    def _export_metadata(self) -> str:
        return str(self.cinfo_object.to_xml())

    # ACTUAL LOGIC
    def _process(self, write_metadata=False, do_convert_to_webp=False, **_):

        if write_metadata and not do_convert_to_webp and not self.has_metadata:
            with zipfile.ZipFile(self.file_path, mode='a', compression=zipfile.ZIP_STORED) as zf:
                # We finally append our new ComicInfo file
                zf.writestr(COMICINFO_FILE, self._export_metadata())
                logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] New ComicInfo.xml appended to the file")
            self.has_metadata = True

        # Creates a tempfile in the directory the original file is at
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self.file_path))
        os.close(tmpfd)

        with zipfile.ZipFile(self.file_path, "r") as zin:
            initial_file_count = len(zin.namelist())

            with zipfile.ZipFile(tmpname, "w") as zout:  # The temp file where changes will be saved to
                self._recompress(zin, zout, write_metadata=write_metadata, do_convert_webp=do_convert_to_webp)

        has_cover_action = self.cover_action not in (CoverActions.RESET, None) or self.backcover_action not in (
            CoverActions.RESET, None)
        # Reset cover flags
        self.cover_action = CoverActions.RESET
        self.backcover_action = CoverActions.RESET

        logger.debug(f"[{'Processing':13s}] Data from old file copied to new file")
        # Delete old file and rename new file to old name
        try:
            with zipfile.ZipFile(self.file_path, "r") as zin:
                assert initial_file_count == len(zin.namelist())
            os.remove(self.file_path)
            os.rename(tmpname, self.file_path)
            logger.debug(f"[{'Processing':13s}] Successfully deleted old file and named tempfile as the old file")
        # If we fail to delete original file we delete temp file effecively aborting the metadata update
        except PermissionError:
            logger.exception(f"[{'Processing':13s}] Permission error. Aborting and clearing temp files")
            os.remove(
                tmpname)  # Could be moved to a 'finally'? Don't want to risk it not clearing temp files properly
            raise
        except Exception:
            logger.exception(f"[{'Processing':13s}] Unhandled exception. Create an issue so this gets investigated."
                             f" Aborting and clearing temp files")
            os.remove(tmpname)
            raise

        self.original_cinfo_object = copy.copy(self.cinfo_object)
        logger.info(f"Succesfully recompressed '{self.file_name}'")

        if (self.cover_cache or self.backcover_cache) and has_cover_action:
            logger.info(f"Updating covers")
            self.load_cover_info()

    def _recompress(self, zin, zout, write_metadata, do_convert_webp):
        """
        Given 2 input and output zipfiles copy content of one zipfile to the new one.
        Files that matches certain criteria gets skipped and not copied over, hence deleted.

        :param zin: The zipfile object of the zip that's going to be read
        :param zout: The ZipFile object of the new zip to copy stuff to
        :param write_metadata: Should update metadata
        :param do_convert_webp: Should convert images before adding to new zipfile
        :return:
        """
        is_metadata_backed = False
        # Write the new metadata once
        if write_metadata:
            zout.writestr(COMICINFO_FILE, self._export_metadata())
            logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] New ComicInfo.xml appended to the file")
            # Directly backup the metadata if it's at root.
            if self.is_cinfo_at_root:
                zout.writestr(f"Old_{COMICINFO_FILE}.bak", zin.read(COMICINFO_FILE))
                logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Backup for comicinfo.xml created")
                is_metadata_backed = True
            self.has_metadata = True

        # Append the cover if the action is append
        if self.cover_action == CoverActions.APPEND:
            self._append_image(zout, self.new_cover_path, False, do_convert_webp,
                               current_backcover_filename=self.backcover_filename)

        if self.backcover_action == CoverActions.APPEND:
            self._append_image(zout, self.new_backcover_path, True, do_convert_webp,
                               current_backcover_filename=self.backcover_filename)

        # Start iterating files.
        for item in zin.infolist():
            if write_metadata:
                # Discard old backup
                if item.filename.endswith(
                        COMICINFO_FILE_BACKUP):  # Skip file, efectively deleting old backup
                    logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Skipped old backup file")
                    continue

                if item.filename.endswith(COMICINFO_FILE):
                    # A root-level comicinfo was backed up already. This one is likely not where it should
                    if is_metadata_backed:
                        logger.info(f"[{_LOG_TAG_WRITE_META:13s}] Skiping non compliant ComicInfo.xml")
                        continue

                    # If filename is comicinfo save as old_comicinfo.xml
                    zout.writestr(f"Old_{item.filename}.bak", zin.read(item.filename))
                    logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Backup for comicinfo.xml created")
                    # Stop accepting more comicinfo files.
                    is_metadata_backed = True
                    continue

            # Handle Cover Changes:
            if item.filename == self.cover_filename:
                match self.cover_action:
                    case None:
                        self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp)
                    case CoverActions.DELETE:
                        logger.trace(
                            f"[{_LOG_TAG_RECOMPRESSING:13}] Skipping cover to efectively delete it. File: '{item.filename}'")
                    case CoverActions.REPLACE:
                        with open(self.new_cover_path, "rb") as opened_image:
                            opened_image_io = io.BytesIO(opened_image.read())
                            self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp,
                                             image=opened_image_io)
                    case _:
                        self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp)
                continue
            # Handle BackCover Change
            elif item.filename == self.backcover_filename:
                match self.backcover_action:
                    case None:
                        self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp)
                    case CoverActions.DELETE:
                        logger.trace(
                            f"[{_LOG_TAG_RECOMPRESSING:13}] Skipping back cover to efectively delete it. File: '{item.filename}'")
                    case CoverActions.REPLACE:
                        with open(self.new_backcover_path, "rb") as opened_image:
                            opened_image_io = io.BytesIO(opened_image.read())
                            self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp,
                                             image=opened_image_io)
                    case _:
                        self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp)
                continue
            # Copy the rest of the images as they are
            self._move_image(zin, zout=zout, item_=item, do_convert_to_webp=do_convert_webp)

    # Recompressing methods
    @staticmethod
    def _move_image(zin: zipfile.ZipFile, zout: zipfile.ZipFile, item_: zipfile.ZipInfo,
                    do_convert_to_webp: bool,
                    new_filename=None, image: IO[bytes] = None):
        """
        Given an input and output ZipFile copy the passed item to the new zipfile. Also converts image to webp if set to true
        :param zin: The input zipfile object
        :param zout: The output zipfile where the bytes will be copied over
        :param item_: The zipfile 'item' object
        :param do_convert_to_webp: Should the bytes be converted to webp formate
        :param new_filename: If a new filename is desired this should be set. Else it will use original filename
        :param image: Bytes of the image if the data wants to be overwritten
        :return:
        """
        # Convert to webp if option enabled and file is image
        if do_convert_to_webp and IS_IMAGE_PATTERN.match(item_.filename):
            with zin.open(item_) as opened_image:
                new_filename = get_new_webp_name(new_filename if new_filename is not None else item_.filename)
                zout.writestr(new_filename, convert_to_webp(opened_image if image is None else image))
                logger.trace(f"[{_LOG_TAG_RECOMPRESSING:13s}] Adding converted file '{new_filename}' to new tempfile"
                             f" back to the new tempfile")
        # Keep the rest of the files.
        else:
            zout.writestr(item_.filename if new_filename is None else new_filename,
                          zin.read(item_.filename) if image is None else image.read())
            logger.trace(f"[{_LOG_TAG_RECOMPRESSING:13s}] Adding '{item_.filename}' back to the new tempfile")

    @staticmethod
    def _append_image(zout, cover_path, is_backcover=False, do_convert_to_webp=False, current_backcover_filename=''):
        """
            Given a zipfile object, append (Add image and make it be the first one when natural sorting. Make it last if is_backcover is true) the image in the provided path

            :param zout: The zipfile object where the image is going to be added to
            :param cover_path: The path to the image file
            :param is_backcover: Whether we are "appending" a cover or backcover
            :param do_convert_to_webp: Whether the provided image should be converted to webp
            :return:
            """
        file_name, ext = os.path.splitext(os.path.basename(cover_path))
        new_filename = f"{os.path.join(os.path.dirname(current_backcover_filename), '~') if is_backcover else ''}{BACKCOVER_NAME if is_backcover else COVER_NAME}{ext}"
        logger.trace(
            f"[{_LOG_TAG_RECOMPRESSING:13}] Apending cover to efectively delete it. Loading '{cover_path}'")

        if do_convert_to_webp:
            with open(cover_path, "rb") as opened_image:
                opened_image_io = io.BytesIO(opened_image.read())
                new_filename = get_new_webp_name(new_filename)
                zout.writestr(new_filename, convert_to_webp(opened_image_io))
                logger.trace(
                    f"[{_LOG_TAG_RECOMPRESSING:13s}] Adding converted file '{new_filename}' to new tempfile")
        else:
            zout.write(cover_path, new_filename)
            logger.trace(
                f"[{_LOG_TAG_RECOMPRESSING:13s}] Adding file '{new_filename}' to new tempfile")
