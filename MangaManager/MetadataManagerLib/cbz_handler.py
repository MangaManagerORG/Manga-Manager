import io
import os
import tempfile
import zipfile

from lxml.etree import XMLSyntaxError

if __name__.startswith("MetadataManagerLib") or __name__ == 'MangaManager.MetadataManagerLib.cbz_handler':
    from .errors import NoMetadataFileFound, CorruptedComicInfo
    from .models import *
    # from . import ComicInfo
else:
    name = __name__
    from errors import NoMetadataFileFound, CorruptedComicInfo
    from models import *
    # import ComicInfo

logger = logging.getLogger(__name__)


def is_folder(name: str, folders_list):
    if name.split("/")[0] + "/" in folders_list:
        return True
    else:
        return False


class ReadComicInfo:
    def __init__(self, cbz_path: str, comicinfo_xml: str = None, ignore_empty_metadata=False):
        self.cbz_path = cbz_path
        self.xmlString = ""
        self.ignore_empty_metadata = ignore_empty_metadata
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
                if not comicinfo_xml_exists and not ignore_empty_metadata:
                    raise NoMetadataFileFound(self.cbz_path)
        else:
            self.xmlString = comicinfo_xml
        logger.debug("ReadComicInfo: Reading XML done")

    def to_ComicInfo(self, print_xml: bool=False) -> ComicInfo:
        """
        Reads a cbz o zip file and returns the a ComicInfo class from the ComicInfo.xml file.
        If ComicInfo not present returns none
        """
        if self.ignore_empty_metadata and not self.xmlString:
            logger.debug("returning comicinfo")
            return ComicInfo.ComicInfo()
        print_xml = False if print_xml else True
        try:
            comicinfo = ComicInfo.parseString(self.xmlString, silence=print_xml)
        except XMLSyntaxError as e:
            try:
                logger.error(f"Failed to parse XML:\n{e}\nAttempting recovery...", exc_info=False)
                comicinfo = ComicInfo.parseString(self.xmlString, silence=print_xml, doRecover=True)
            except Exception as e:
                logger.error(f"Failed to parse XML:\n{e}\nRecovery attempt failed", exc_info=False)
                raise CorruptedComicInfo(self.cbz_path)

        logger.debug("returning comicinfo")
        return comicinfo



    def to_String(self) -> str:
        return self.xmlString.decode('utf-8')


class WriteComicInfo:
    def __init__(self, loadedComicInfo: LoadedComicInfo):
        self._zipFilePath = loadedComicInfo.path
        _oldZipFilePath = self._zipFilePath

        # new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", _zipFilePath)[0])
        logger.debug(f"[Write] -  {self._zipFilePath}")
        # os.rename(_zipFilePath, new_zipFilePath)
        export_io = io.StringIO()
        try:
            loadedComicInfo.comicInfoObj.export(export_io, 0)
            self._export_io = export_io.getvalue()
        except AttributeError as e:
            logger.info(f"Attribute error :{str(e)}")
            # raise e

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
        backup_isdone = False
        with zipfile.ZipFile(self._zipFilePath, 'r') as zin:
            if not "ComicInfo.xml" in zin.namelist():
                logger.debug(f"[Backup] Skipping backup. No ComicInfo.xml present")
                return
            tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self._zipFilePath))
            os.close(tmpfd)
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

    def to_file(self, skip_backup=False, skip_if_comicinfo_is_present=False):
        comicinfo_is_present = False
        with zipfile.ZipFile(self._zipFilePath, 'r') as zin:
            if "ComicInfo.xml" in zin.namelist():
                comicinfo_is_present = True
                logger.debug("[Write] Skipped appending ComicInfo.xml to the file")
        if comicinfo_is_present:
            if not skip_backup:
                self._backup()
        if comicinfo_is_present and skip_if_comicinfo_is_present:
            return
        with zipfile.ZipFile(self._zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            # We finally append our new ComicInfo file
            zf.writestr("ComicInfo.xml", self._export_io)
            logger.debug("[Write] New ComicInfo.xml added to the file")

    def to_str(self) -> str:
        return self._export_io

    def delete(self):
        self._backup()
        logger.debug("[Delete] File backed up with a different name, hence removed")

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

        backup_isdone = False
        with zipfile.ZipFile(self._zipFilePath, 'r') as zin:
            if not "Old_ComicInfo.xml.bak" in zin.namelist():
                logger.debug(f"[Restore] Skipping restore for '{self._zipFilePath}'. No ComicInfo.xml present")
                return
            tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self._zipFilePath))
            os.close(tmpfd)
            with zipfile.ZipFile(tmpname, 'w') as zout:
                for item in zin.infolist():
                    logger.debug(f"[Restore Backup] Iterating: {item.filename}")
                    if item.filename == "ComicInfo.xml":
                        # Skip this file. We want to overwrite it to restore the backup
                        continue
                    elif item.filename == "Old_ComicInfo.xml.bak":
                        # Rename this file back to ComicInfo.xml hence restoring the metadata
                        zout.writestr(item.filename.replace("Old_", "").replace(".bak", ""), zin.read(item.filename))
                        # Keep a copy of the backup just in case. High chance it's unnecessary
                        zout.writestr(item.filename, zin.read(item.filename))
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


class MergeChapter:

    def __init__(self, ordered_loadedComicInfo: list[LoadedComicInfo], output_filename,
                 output_metadata: ComicInfo.ComicInfo = None):
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(ordered_loadedComicInfo[0].path))
        os.close(tmpfd)
        counter = 1
        with zipfile.ZipFile(tmpname, 'w') as zout:
            for loadedComicInfo in ordered_loadedComicInfo:
                with zipfile.ZipFile(loadedComicInfo.path, 'r') as zin:
                    # if not "ComicInfo.xml" in zin.namelist():
                    for item in zin.infolist():
                        new_filename = f"Ch.{str(loadedComicInfo.chapter).zfill(3)}/{item.filename}"

                        # Write the rest of the files as they are
                        zout.writestr(new_filename, zin.read(item.filename))
                        logger.debug(f"[Merge] Adding '{item.filename}' as {new_filename} to the new tempfile")
                        counter += 1
                export_io = io.StringIO()
                try:
                    loadedComicInfo.comicInfoObj.export(export_io, 0)
                    export_io = export_io.getvalue()
                    # Append old ComicInfo file
                    new_filename = f"Ch.{str(loadedComicInfo.chapter).zfill(3)}/OLD_MERGED_ComicInfo.xml"
                    zout.writestr(new_filename, export_io)
                    logger.debug("[Merge] OLD_MERGED_ComicInfo added to the new file")
                except AttributeError as e:
                    logger.info(f"Attribute error :{str(e)}")
                    # raise e
            export_io = io.StringIO()
            try:
                loadedComicInfo.comicInfoObj.export(export_io, 0)
                export_io = export_io.getvalue()
                # We finally append our new ComicInfo file
                zout.writestr("ComicInfo.xml", export_io)
                logger.debug("[Merge] ComicInfo added to the new file")
            except AttributeError as e:
                logger.info(f"Attribute error :{str(e)}")
                # raise e

        os.rename(tmpname, output_filename)
