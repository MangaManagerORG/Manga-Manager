import copy
import logging
import os
import re
import tempfile
import zipfile
from io import StringIO
from typing import IO

from lxml.etree import XMLSyntaxError

from .comicinfo import ComicInfo, parseString
from .errors import CorruptedComicInfo, FailedBackup
from src.MangaManager_ThePromidius.Common.naturalsorter import natsort_key_with_path_support

logger = logging.getLogger("LoadedCInfo")


# Patterns for picking cover
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp')
cover_r1 = '^!*0+\\.[a-z]+$'
cover_r2 = '.*cover.*\\.[a-z]+$'
covers_patterns = [cover_r1, cover_r2]
COVER_PATTERN = re.compile(f"(?i)({'|'.join(covers_patterns)})")
cover_r3_alt = '^!*0+1\\.[a-z]+$'
ALT_COVER_PATTERN = re.compile(f"(?i)({'|'.join([cover_r3_alt])})")
IS_IMAGE_PATTERN = re.compile(rf"(?i).*.(?:{'|'.join(IMAGE_EXTENSIONS)})$")


def obtain_cover_filename(file_list) -> str:
    """
    Helper function to find a cover file based on a list of filenames
    :param file_list:
    :return:
    """
    cover = None
    # Cover stuff
    possible_covers = [filename for filename in file_list
                       if IS_IMAGE_PATTERN.findall(filename) and COVER_PATTERN.findall(filename)]

    # Try to get 0001
    if not possible_covers:
        possible_covers = [filename for filename in file_list if ALT_COVER_PATTERN.findall(filename)]
    # Resource back to first filename available that is a cover

    if not possible_covers:
        list_image_files = (filename for filename in file_list if IS_IMAGE_PATTERN.findall(filename))
        cover = sorted(list_image_files, key=natsort_key_with_path_support, reverse=False)

    if isinstance(cover, list):
        cover = cover[0]
    if not cover:
        if len(possible_covers) > 1:
            cover = possible_covers[0]
        else:
            cover = possible_covers
    return cover


def matchany(image_filename):
    ...


# @dataclass()


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
    cover_filename: str = None
    has_metadata: bool = False

    @property
    def cinfo_object(self):
        return self._cinfo_object

    @cinfo_object.setter
    def cinfo_object(self, value: ComicInfo):
        self._cinfo_object = value
        self.original_cinfo_object = copy.copy(value)

    @property
    def volume(self):
        if self.cinfo_object:
            return self.cinfo_object.get_Volume()

    @property
    def chapter(self):
        if self.cinfo_object:
            return self.cinfo_object.get_Number()

    def __init__(self, path, comicInfo: ComicInfo = None):
        """

        :param path:
        :param comicInfo: The data class to be applied
        """

        self.file_path = path
        logger.info(f"[{'OpeningFile':13s}] '{os.path.basename(self.file_path)}'")
        with zipfile.ZipFile(self.file_path, 'r') as self.archive:
            self._load_cover_info()
            if not comicInfo:
                self._load_metadata()
            else:
                self.cinfo_object = comicInfo

    def get_cover_image_bytes(self) -> IO[bytes]:
        """
        Opens the cbz and returns the bytes for the parsed cover image
        :return:
        """
        with zipfile.ZipFile(self.file_path, 'r') as zin:
            return zin.open(self.cover_filename)

    def _load_cover_info(self):
        self.cover_filename = obtain_cover_filename(self.archive.namelist())
        logger.info(f"[{'CoverParsing':13s}] Cover parsed as '{self.cover_filename}'")

    def _load_metadata(self):
        logger.info(f"[{'Reading Meta':13s}]")
        try:
            xml_string = self.archive.read('ComicInfo.xml').decode('utf-8')
            self.has_metadata = True
        except KeyError:
            xml_string = ""

        if xml_string:
            try:
                self.cinfo_object = parseString(xml_string, silence=True)
            except XMLSyntaxError as e:
                logger.warning(f"[{'Reading Meta':13s}] Failed to parse XML:\n{e}\nAttempting recovery...")
                try:
                    self.cinfo_objectcomicinfo = parseString(xml_string, doRecover=True, silence=True)
                except XMLSyntaxError:
                    logger.error(f"[{'Reading Meta':13s}] Failed to parse XML: {e} - Recovery attempt failed",
                                 exc_info=False)
                    raise CorruptedComicInfo(self.file_path)
                except Exception:
                    logger.exception(f"[{'Reading Meta':13s}] Unhandled error reading metadata."
                                     f" Please create an issue for further investigation")
                    raise
            logger.debug(f"[{'Reading Meta':13s}] Successful")
        else:
            self.cinfo_object = ComicInfo()
            logger.info(f"[{'Reading Meta':13s}] No metadata file was found so a new one will be created")

    @volume.setter
    def volume(self, value):
        self.cinfo_object.set_Volume(value)

    @chapter.setter
    def chapter(self, value):
        self.cinfo_object.set_Number(value)

    def write_metadata(self):
        # print(self.cinfo_object.__dict__)
        logger.debug(f"[{'Write Meta':13s}] Writing metadata to file '{self.file_path}'")
        export = StringIO()

        self.cinfo_object.export(export, 0)
        if self.has_metadata:
            logger.debug(f"[{'Write Meta':13s}] ComicInfo file found in old file")
            ...
            self._backup_cinfo()

        with zipfile.ZipFile(self.file_path, "a", compression=zipfile.ZIP_STORED) as zout:
            # We finally append our new ComicInfo file
            zout.writestr("ComicInfo.xml", export.getvalue())
            logger.debug(f"[{'WriteMetadata':13s}] New ComicInfo.xml appended to the file")

    def _backup_cinfo(self):
        """
        Renames the ComicInfo.xml file to OLD_Comicinfo.xml.bak
        :return:
        :raises FailedBackup: If it fails to backup because of any error

        """
        logger.debug(f"[{'Backup':13s}] Starting backup")
        with zipfile.ZipFile(self.file_path, "r") as zin:
            if "ComicInfo.xml" not in zin.namelist():  # Redundant check. TODO: Make sure this check is safe to remove
                logger.debug(f"[{'Backup':13s}] Skipping backup. No ComicInfo.xml present")
                return

            # Dev notes
            # Due to how the zip library works, we can't just edit the file.
            # Need to create a copy of it with modified content and delete old one
            # After that rename temp file to match old file

            # Creates a tempfile in the directory the original file is at
            tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self.file_path))
            os.close(tmpfd)

            with zipfile.ZipFile(tmpname, "w") as zout:  # The temp file where changes will be saved to
                for item in zin.infolist():  # We use infolist since we want to get file data not just a list of names

                    if item.filename == "ComicInfo.xml":  # If filename is comicinfo save as old_comicinfo.xml
                        zout.writestr(f"Old_{item.filename}.bak", zin.read(item.filename))
                        logger.debug(f"[{'Backup':13s}] Backup for comicinfo.xml created")

                    elif item.filename == "Old_ComicInfo.xml.bak":  # Skip file, efectively deleting old backup
                        logger.debug(f"[{'Backup':13s}] Skipped old backup file")
                        continue

                    else:  # Any other file gets saved as is
                        zout.writestr(item.filename, zin.read(item.filename))
                        logger.debug(f"[{'Backup':13s}] Adding {item.filename} back to the new tempfile")
        logger.debug(f"[{'Backup':13s}] Data from old file copied to new file")
        # Delete old file and rename new file to old name
        try:
            os.remove(self.file_path)
            os.rename(tmpname, self.file_path)
            logger.debug(f"[{'Backup':13s}] Successfully deleted old file and named tempfile as the old file")
        # If we fail to delete original file we delete temp file effecively aborting the metadata update
        except PermissionError:
            logger.exception(f"[{'Backup':13s}] Permission error. Aborting and clearing temp files")
            os.remove(tmpname)  # Could be moved to a 'finally'? Don't want to risk it not clearing temp files properly
            raise FailedBackup()
        except Exception:
            logger.exception(f"[{'Backup':13s}] Unhandled exception. Create an issue so this gets investigated."
                             f" Aborting and clearing temp files")
            os.remove(tmpname)
            raise
