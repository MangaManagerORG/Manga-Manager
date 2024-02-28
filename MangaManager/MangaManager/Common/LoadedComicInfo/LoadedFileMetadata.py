import copy
import logging

import rarfile
from lxml.etree import XMLSyntaxError

from ComicInfo import ComicInfo
from MangaManager.Common.LoadedComicInfo.ILoadedComicInfo import ILoadedComicInfo
from MangaManager.Common.errors import MissingRarTool

logger = logging.getLogger("LoadedCInfo")
COMICINFO_FILE = 'ComicInfo.xml'
COVER_NAME = "!0000_Cover"
BACKCOVER_NAME = "9999_Back"
_LOG_TAG_WEBP = "Convert Webp"
_LOG_TAG_WRITE_META = 'Write Meta'
_LOG_TAG_RECOMPRESSING = "Recompressing"
move_to_value = ""


class LoadedFileMetadata(ILoadedComicInfo):

    _cinfo_object: ComicInfo
    original_cinfo_object: ComicInfo
    # Used to keep original state after being loaded for the first time. Useful to undo sesion changes
    original_cinfo_object_before_session: ComicInfo | None = None
    had_metadata_on_open = False

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
            if COMICINFO_FILE not in self.archive.namelist():
                cinfo_file = [filename.endswith(COMICINFO_FILE) for filename in self.archive.namelist()][
                                 0] or COMICINFO_FILE
            else:
                cinfo_file = COMICINFO_FILE
                self.is_cinfo_at_root = True
            xml_string = self.archive.read(cinfo_file).decode('utf-8')
            self.has_metadata = True
            self.had_metadata_on_open = True
        except KeyError:
            xml_string = ""
        except rarfile.RarCannotExec:
            xml_string = ""
            raise MissingRarTool
        except Exception:
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
            logger.info(LOG_TAG + "No metadata file was found. A new file will be created")
        self.original_cinfo_object = copy.copy(self.cinfo_object)
        self.original_cinfo_object_before_session = copy.copy(self.cinfo_object)

    def reset_metadata(self):
        """
        Returns the metadata to the first state of loaded cinfo
        """
        self.cinfo_object = self.original_cinfo_object