from __future__ import annotations

import copy
import io
import logging
import os
import tempfile
import zipfile
from io import StringIO
from typing import IO

from PIL import Image, ImageTk
from lxml.etree import XMLSyntaxError

from src import settings_class as settings_class
from src.Common.errors import CorruptedComicInfo, BadZipFile
from src.Common.utils import IS_IMAGE_PATTERN
from src.Common.utils import obtain_cover_filename, getNewWebpFormatName, convertToWebp
from src.MetadataManager.comicinfo import ComicInfo, parseString

logger = logging.getLogger("LoadedCInfo")

COMICINFO_FILE = 'ComicInfo.xml'

_LOG_TAG_WEBP = "Convert Webp"
_LOG_TAG_WRITE_META = 'Write Meta'
settings = settings_class.get_setting("main")


class LoadedComicInfo:
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
    _cinfo_object: ComicInfo
    original_cinfo_object: ComicInfo
    # Used to keep original state after being loaded for the first time. Useful to undo sesion changes
    original_cinfo_object_before_session: ComicInfo = None

    has_metadata: bool = False
    is_cinfo_at_root: bool = False

    cover_filename: str | None = None
    cover_filename_last: str | None = None
    cached_image: ImageTk.PhotoImage = None
    cached_image_last: ImageTk.PhotoImage = None
    has_changes = False
    changed_tags = []

    @property
    def cinfo_object(self):
        return self._cinfo_object

    @cinfo_object.setter
    def cinfo_object(self, value: ComicInfo):
        self._cinfo_object = value

    @property
    def volume(self):
        if self.cinfo_object:
            return self.cinfo_object.get_Volume()

    @property
    def chapter(self):
        if self.cinfo_object:
            return self.cinfo_object.get_Number()

    def __init__(self, path, comicinfo: ComicInfo = None):
        """

        :param path:
        :param comicinfo: The data class to be applied
        :raises BadZipFile: The file can't be read or is not a valid zip file
        """

        self.file_path = path
        self.file_name = os.path.basename(path)
        logger.info(f"[{'Opening File':13s}] '{os.path.basename(self.file_path)}'")
        self.cinfo_object = comicinfo
        self.load_metadata()

    @volume.setter
    def volume(self, value):
        self.cinfo_object.set_Volume(value)

    @chapter.setter
    def chapter(self, value):
        self.cinfo_object.set_Number(value)

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
        self._process(convert_to_webp=True)

    def _export_metadata(self) -> str:
        exported_metadata = StringIO()
        self.cinfo_object.export(exported_metadata, 0)
        return exported_metadata.getvalue()

    def _process(self, write_metadata=False, convert_to_webp=False):
        """
        Renames the ComicInfo.xml file to OLD_Comicinfo.xml.bak
        :return:
        :raises PermissionError: If the file can't be written because of permissions or other program has file opened

        """
        logger.debug(f"[{'Processing':13s}] Starting")

        # Check to just append metadata if no cinfo in already in file or no webp conversion ordered
        if write_metadata and not convert_to_webp and not self.has_metadata:
            with zipfile.ZipFile(self.file_path, mode='a', compression=zipfile.ZIP_STORED) as zf:
                self.cinfo_object.set_PageCount(
                    len([file_ for file_ in zf.namelist() if IS_IMAGE_PATTERN.match(file_)]))

                zf.writestr(COMICINFO_FILE, self._export_metadata())
                logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] New ComicInfo.xml appended to the file")
            return

        # Creates a tempfile in the directory the original file is at
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self.file_path))
        os.close(tmpfd)

        is_metadata_backed = False

        # Dev notes
        # Due to how the zip library works, we can't just edit the file.
        # Need to create a copy of it with modified content and delete old one
        # After that rename temp file to match old file
        with zipfile.ZipFile(self.file_path, "r") as zin:

            with zipfile.ZipFile(tmpname, "w") as zout:  # The temp file where changes will be saved to
                # Write the new metadata once
                if write_metadata:
                    self.cinfo_object.set_PageCount(
                        len([file_ for file_ in zin.namelist() if IS_IMAGE_PATTERN.match(file_)]))
                    zout.writestr(COMICINFO_FILE, self._export_metadata())
                    logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] New ComicInfo.xml appended to the file")
                    # Directly backup the metadata if it's at root.
                    if self.is_cinfo_at_root:
                        zout.writestr(f"Old_{COMICINFO_FILE}.bak", zin.read(COMICINFO_FILE))
                        logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Backup for comicinfo.xml created")
                        is_metadata_backed = True

                # Start iterating files.
                for item in zin.infolist():

                    if write_metadata:
                        # Discard old backup
                        if item.filename == "Old_ComicInfo.xml.bak":  # Skip file, efectively deleting old backup
                            logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Skipped old backup file")
                            continue
                        if item.filename.endswith(COMICINFO_FILE):
                            # A root-level comicinfo was backed up already. This one is likely not where it should
                            if is_metadata_backed:
                                logger.info(f"[{_LOG_TAG_WRITE_META:13s}] Skipped non compliant ComicInfo.xml")
                                continue

                            # Metadata is not at root. Keep looking for a comicinfo.xml file in the archive.
                            # Keep the first one found and stop looking for more

                            # If filename is comicinfo save as old_comicinfo.xml
                            if item.filename.endswith(COMICINFO_FILE):
                                zout.writestr(f"Old_{item.filename}.bak", zin.read(item.filename))
                                logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Backup for comicinfo.xml created")
                            # Stop accepting more comicinfo files.
                            is_metadata_backed = True
                            continue

                    # Convert to webp if option enabled and file is image
                    if convert_to_webp and IS_IMAGE_PATTERN.match(item.filename):
                        with zin.open(item) as opened_image:
                            new_filename = getNewWebpFormatName(item.filename)
                            zout.writestr(new_filename, convertToWebp(opened_image))
                            logger.trace(f"[{_LOG_TAG_WEBP:13s}] Adding converted file '{new_filename}'"
                                         f" back to the new tempfile")
                    # Keep the rest of the files.
                    else:
                        zout.writestr(item.filename, zin.read(item.filename))
                        logger.trace(f"[{_LOG_TAG_WEBP:13s}] Adding '{item.filename}' back to the new tempfile")

        logger.debug(f"[{'Processing':13s}] Data from old file copied to new file")
        # Delete old file and rename new file to old name
        try:
            os.remove(self.file_path)
            os.rename(tmpname, self.file_path)
            logger.debug(f"[{'Processing':13s}] Successfully deleted old file and named tempfile as the old file")
        # If we fail to delete original file we delete temp file effecively aborting the metadata update
        except PermissionError:
            logger.exception(f"[{'Processing':13s}] Permission error. Aborting and clearing temp files")
            os.remove(tmpname)  # Could be moved to a 'finally'? Don't want to risk it not clearing temp files properly
            raise
        except Exception:
            logger.exception(f"[{'Processing':13s}] Unhandled exception. Create an issue so this gets investigated."
                             f" Aborting and clearing temp files")
            os.remove(tmpname)
            raise
        self.original_cinfo_object = copy.copy(self.cinfo_object)
        self.has_changes = False

    def load_all(self):
        try:
            # Fixme: skip folders
            with zipfile.ZipFile(self.file_path, 'r') as self.archive:
                self._load_cover_info()
                if not self.cinfo_object:
                    self._load_metadata()

        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        return self

    def load_cover_info(self, cache_cover_bytes):
        try:
            with zipfile.ZipFile(self.file_path, 'r') as self.archive:
                self._load_cover_info(cache_cover_bytes)
        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        return self

    def _load_cover_info(self, cache_cover_bytes=True):
        cover_info = obtain_cover_filename(self.archive.namelist())
        if not cover_info:
            return
        self.cover_filename, self.cover_filename_last = cover_info

        if not self.cover_filename:
            logger.warning(f"[{'CoverParsing':13s}] Couldn't parse any cover")
        else:
            logger.info(f"[{'CoverParsing':13s}] Cover parsed as '{self.cover_filename}'")
            if cache_cover_bytes:
                self.get_cover_image_bytes()

        if not self.cover_filename_last:
            logger.warning(f"[{'CoverParsing':13s}] Couldn't parse any back cover")
        else:
            logger.info(f"[{'CoverParsing':13s}] Back Cover parsed as '{self.cover_filename_last}'")
            if cache_cover_bytes:
                self.get_cover_image_bytes(back_cover=True)

    def get_cover_image_bytes(self, resized=False, back_cover=False) -> IO[bytes] | None:
        """
        Opens the cbz and returns the bytes for the parsed cover image
        :return:
        """
        if not self.file_path or not self.cover_filename:
            return None
        if back_cover and not self.cover_filename_last:
            return None

        with zipfile.ZipFile(self.file_path, 'r') as zin:
            img_bytes = zin.open(self.cover_filename if not back_cover else self.cover_filename_last)
            image = Image.open(img_bytes)
            image = image.resize((190, 260), Image.LANCZOS)
            try:
                if not back_cover:
                    self.cached_image = ImageTk.PhotoImage(image)
                else:
                    self.cached_image_last = ImageTk.PhotoImage(image)
            except RuntimeError:  # Random patch for some error when running tests
                ...
            if resized:
                return io.BytesIO(image.tobytes())
        return img_bytes

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
                self.cinfo_object = parseString(xml_string, silence=True)
            except XMLSyntaxError as e:
                logger.warning(LOG_TAG + f"Failed to parse XML:\n{e}\nAttempting recovery...")
                try:
                    self.cinfo_object = parseString(xml_string, doRecover=True, silence=True)
                except XMLSyntaxError:
                    logger.error(f"[{'Reading Meta':13s}] Failed to parse XML: {e} - Recovery attempt failed")
                    raise CorruptedComicInfo(self.file_path)
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
