from __future__ import annotations

import copy
import io
import logging
import os
import tempfile
import zipfile
from typing import IO

from common.models import ComicInfo
from src.Common.errors import BadZipFile
from src.Common.utils import IS_IMAGE_PATTERN, get_new_webp_name, convert_to_webp
from .ArchiveFile import ArchiveFile
from .CoverActions import CoverActions
from .ILoadedComicInfo import ILoadedComicInfo
from .LoadedFileCoverData import LoadedFileCoverData
from .LoadedFileMetadata import LoadedFileMetadata
from ...Settings import Settings, SettingHeading

logger = logging.getLogger("LoadedCInfo")
COMICINFO_FILE = 'ComicInfo.xml'
COMICINFO_FILE_BACKUP = 'Old_ComicInfo.xml.bak'
COVER_NAME = "!0000_Cover"
BACKCOVER_NAME = "9999_Back"
_LOG_TAG_WEBP = "Convert Webp"
_LOG_TAG_WRITE_META = 'Write Meta'
_LOG_TAG_RECOMPRESSING = "Recompressing"
move_to_value = ""


class LoadedComicInfo(LoadedFileMetadata, LoadedFileCoverData, ILoadedComicInfo):


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

    def get_template_values(self) -> dict:
        """
        Returns a dict with predefined values to fill in string templates
        :return:
        """
        return {
            "filename": self.file_name,
            "series": self.cinfo_object.series or "",
            "series_sort": self.cinfo_object.series_sort or "",
            "title": self.cinfo_object.title or "",
            "chapter": self.cinfo_object.number or "",
            "volume": self.cinfo_object.volume or "",
            "publisher": self.cinfo_object.publisher or ""
        }

    def get_template_filename(self, input_template: str) -> str|None:
        """
        Fills the provided template with the available values in the comicinfo
        :param input_template: A string representing the input template ("{series} - {chapter}")
        :return: None if there's a missing key in the template
        """
        try:
            return input_template.format_map(self.get_template_values()).replace("  ", " ")
        except KeyError as e:
            logger.error(f"Could not get {list(e.args)} keys when filling template values")
            return None
    ###############################
    # LOADING METHODS
    ###############################

    def load_all(self):
        try:
            # Fixme: skip folders
            # Update: 05-01-23 At this point i don't remember why the fix me. I'm leaving it there.
            self.load_cover_info()
            with ArchiveFile(self.file_path,'r') as self.archive:
                if not self.cinfo_object:
                    self._load_metadata()

        except zipfile.BadZipFile:
            logger.error(f"[{'OpeningFile':13s}] Failed to read file. File is not a zip file or is broken.",
                         exc_info=False)
            raise BadZipFile()
        return self

    def load_metadata(self):
        try:
            with ArchiveFile(self.file_path,'r') as self.archive:
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

        with ArchiveFile(self.file_path, 'r') as zin:
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
            with ArchiveFile(self.file_path, 'r') as zin:
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
        logger.info(f"Successfully recompressed '{self.file_name}'")

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
                if Settings().get(SettingHeading.Main, "create_backup_comicinfo") == 'True' and self.had_metadata_on_open:
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
                        COMICINFO_FILE_BACKUP):  # Skip file, effectively deleting old backup
                    logger.debug(f"[{_LOG_TAG_WRITE_META:13s}] Skipped old backup file")
                    continue

                if item.filename.endswith(COMICINFO_FILE):
                    # A root-level comicinfo was backed up already. This one is likely not where it should
                    if is_metadata_backed:
                        logger.info(f"[{_LOG_TAG_WRITE_META:13s}] Skipping non compliant ComicInfo.xml")
                        continue

                    # If filename is comicinfo save as old_comicinfo.xml
                    if Settings().get(SettingHeading.Main, "create_backup_comicinfo") == 'True' and self.had_metadata_on_open:
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
                            f"[{_LOG_TAG_RECOMPRESSING:13}] Skipping cover to effectively delete it. File: '{item.filename}'")
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
