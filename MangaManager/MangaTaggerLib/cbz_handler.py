import zipfile
import os
import tempfile
import logging
import io
from lxml.etree import XMLSyntaxError

import errors
from .models import *
from .errors import NoMetadataFileFound
from . import ComicInfo

logger = logging.getLogger(__name__)
def is_folder(name: str, folders_list):
    if name.split("/")[0] + "/" in folders_list:
        return True
    else:
        return False


class ReadComicInfo:
    def __init__(self, cbz_path: str, comicinfo_xml: str = None):
        self.cbz_path = cbz_path
        self.xmlString = ""
        self.total_files = 0
        comicinfo_xml_exists = False
        if not comicinfo_xml:
            with zipfile.ZipFile(self.cbz_path, 'r') as zin:
                self.total_files = len(zin.infolist())
                for file in zin.infolist():
                    if file.filename == "ComicInfo.xml":
                        comicinfo_xml_exists = True
                        with zin.open(file) as infile:
                            self.xmlString = infile.read()
                if not comicinfo_xml_exists:
                    raise NoMetadataFileFound(self.cbz_path)
        else:
            self.xmlString = comicinfo_xml
        logger.debug("ReadComicInfo: Reading XML done")

    def to_ComicInfo(self, print_xml: bool=False) -> ComicInfo:
        """
        Reads a cbz o zip file and returns the a ComicInfo class from the ComicInfo.xml file.
        If ComicInfo not present returns none
        """
        print_xml = False if print_xml else True
        try:
            comicinfo = ComicInfo.parseString(self.xmlString, silence=print_xml)
        except XMLSyntaxError as e:
            try:
                logger.error(f"Failed to parse XML:\n{e}\nAttempting recovery...", exc_info=False)
                comicinfo = ComicInfo.parseString(self.xmlString, silence=print_xml,doRecover=True)
            except Exception as e:
                logger.error(f"Failed to parse XML:\n{e}\nRecovery attempt failed", exc_info=False)
                raise errors.CorruptedComicInfo(self.cbz_path)

        logger.debug("returning comicinfo")
        return comicinfo



    def to_String(self) -> str:
        return self.xmlString.decode('utf-8')


class WriteComicInfo:
    def __init__(self, loadedComicInfo: LoadedComicInfo):
        self._zipFilePath = loadedComicInfo.path
        _oldZipFilePath = self._zipFilePath

        # new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", _zipFilePath)[0])
        logger.debug(f"[Write file] -  {self._zipFilePath}")
        # os.rename(_zipFilePath, new_zipFilePath)
        export_io = io.StringIO()
        try:
            loadedComicInfo.comicInfoObj.export(export_io, 0)
            self._export_io = export_io.getvalue()
        except AttributeError as e:
            logger.info(f"Attribute error :{str(e)}")

    def _backup(self):
        """
                Processing order
                1. Create temp file to write in it
                2. Reads file provided in path in LoadedComicInfo
                3. Backup any file named ComicInfo.xml -> writes in temp file
                4. Write to the file new ComicInfo.xml -> writes in temp file
                5. Write to the file all files -> writes in temp file
                6. Deletes file provided
                7. Renames tempfile to the same name that was deleted previously
                """
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self._zipFilePath))
        os.close(tmpfd)
        backup_isdone = False
        with zipfile.ZipFile(self._zipFilePath, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:
                for item in zin.infolist():
                    logger.debug(f"[Backup] Iterating: {item.filename}")
                    if item.filename == "ComicInfo.xml":
                        # Backup ComicInfo.xml
                        zout.writestr(f"Old_{item.filename}.bak", zin.read(item.filename))
                        logger.debug("[Backup] Backup for ComicInfo.xml created")
                    elif item.filename == "Old_ComicInfo.xml.bak":
                        # Delete old backup
                        # zout.writestr(f"Old_{item.filename}.bak", zin.read(item.filename))
                        continue
                    else:
                        # Write the rest of the files as they are
                        zout.writestr(item.filename, zin.read(item.filename))
                        logger.debug(f"[Backup] Adding {item.filename} back to the new tempfile")
        logger.debug("[Backup] Backup successful")
        try:
            os.remove(self._zipFilePath)
            os.rename(tmpname, self._zipFilePath)
        except PermissionError as e:
            logger.error("[Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(tmpname)
            raise e

    def to_file(self):
        self._backup()
        with zipfile.ZipFile(self._zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            # We finally append our new ComicInfo file
            zf.writestr("ComicInfo.xml", self._export_io)
            logger.debug("[Write] New ComicInfo.xml added to the file")

    def to_str(self) -> str:
        return self._export_io

    def delete(self):
        logger.debug("File backed up with diferent name hence removed")

    def restore(self):
        """
                Processing order
                1. Create temp file to write in it
                2. Reads file provided in path in LoadedComicInfo
                3. Deletes any file named ComicInfo.xml
                4. Rename OldComicInfo.xml.bj to ComicInfo.xml -> writes in temp file
                5. Writes the rest of files -> writes in temp file
                6. Deletes file provided
                7. Renames tempfile to the same name that was deleted previously
                """
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self._zipFilePath))
        os.close(tmpfd)
        backup_isdone = False
        with zipfile.ZipFile(self._zipFilePath, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:
                for item in zin.infolist():
                    logger.debug(f"[Restore Backup] Iterating: {item.filename}")
                    if item.filename == "ComicInfo.xml":
                        # Skip this file we want to overwrite it to restore the backup
                        continue
                    elif item.filename == "Old_ComicInfo.xml.bak":
                        zout.writestr(item.filename.replace("Old_", "").replace(".bak", ""), zin.read(item.filename))
                        continue
                    else:
                        # Write the rest of the files as they are
                        zout.writestr(item.filename, zin.read(item.filename))
                        logger.debug(f"[Restore Backup] Adding {item.filename} back to the new tempfile")
        logger.debug("[Restore Backup] Backup successful")
        try:
            os.remove(self._zipFilePath)
            os.rename(tmpname, self._zipFilePath)
        except PermissionError as e:
            logger.error("[Restore Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(tmpname)
            raise e
