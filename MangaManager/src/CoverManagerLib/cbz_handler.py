import logging
import os
import re
import tempfile
import zipfile

from src.CommonLib.WebpConverter import convertToWebp, getNewWebpFormatName, supportedFormats
from . import errors
from .models import cover_process_item_info

logger = logging.getLogger(__name__)


def is_folder(name: str, folders_list):
    if name.split("/")[0] + "/" in folders_list:
        return True
    else:
        return False


class _SingleCoverBackup:

    def __init__(self, zin, zout, doConvertWebp=False):
        self.zin = zin
        self.zout = zout
        self.doConvertWebp = doConvertWebp

    def single_cover(self, filename):
        if self.doConvertWebp:
            newname = f"OldCover_{getNewWebpFormatName(filename)}.bak"
            with self.zin.open(filename) as open_zipped_file:
                self.zout.writestr(newname, convertToWebp(open_zipped_file))
                logger.debug(
                    f"[SetCover][Backup] Adding backup '{filename}' as '{newname}' to the new tempfile")
        else:
            newname = f"OldCover_{filename}.bak"
            self.zout.writestr(newname, self.zin.read(filename))
            logger.debug(
                f"[SetCover][Backup] Adding backup '{filename}' as '{newname}' to the new tempfile")

    def add_image(self,filename):

        if self.doConvertWebp and filename.endswith(supportedFormats):
            with self.zin.open(filename) as open_zipped_file:
                self.zout.writestr(getNewWebpFormatName(filename), convertToWebp(open_zipped_file))
            logger.debug(
                f"[SetCover][Backup] Adding '{filename}' as '{getNewWebpFormatName(filename)}' to the new tempfile")
        else:
            self.zout.writestr(filename, self.zin.read(filename))
            logger.debug(f"[SetCover][Backup] Adding '{filename}' back to the new tempfile")


class SetCover:
    def __init__(self, process_values: cover_process_item_info, convert_to_webp=False):
        self.values = process_values
        self.convert_to_webp = convert_to_webp
        if self.values.coverFileFormat.startswith("."):
            self.values.coverFileFormat = self.values.coverFileFormat.strip(".")
        v = process_values
        self.oldZipFilePath = v.zipFilePath
        # new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", v.zipFilePath)[0])

        self.temp_file = None
        if v.coverRecover:
            logger.info("[SetCover] Proceeding to recover cover")
            self._recover_cover()
            return

        logger.info("[SetCover] Proceeding to do backup")
        self._backup_cover()

        if v.coverDelete:
            logger.info("[SetCover] Proceeding to delete cover")
            self._delete()
            return
        if v.coverOverwrite:
            logger.info("[SetCover] Proceeding to overwrite cover")
            self._overwrite()
            return
        else:
            logger.info("[SetCover] Proceeding to append cover")
            self._append()
            return

    def _create_temp_file(self):
        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(self.values.zipFilePath))
        os.close(tmpfd)
        self.temp_file = tmpname

    def _backup_cover(self):
        """
        Backup will always back up all files in any situation.

        If overwrite is set to false:
            - If file name == 0*.ext it gets overwritten (0000.ext is a reserved name, can't go lower than 0)
                + File is backed up

        If overwrite is set to true:
            - First file detected as cover is backed up

        If delete is set to True:
            - First file detected as cover is backed up


        """
        with zipfile.ZipFile(self.values.zipFilePath, 'r') as zin:
            # If its append mode, we can just skip this part no files is backed up only added

            file_list = zin.namelist()
            forced_cover = [v for v in zin.namelist() if re.match(r"(?i).*cover.*", v)]

            cover_matches_000_pattern = [v for v in zin.namelist() if
                                         v.startswith("00000.") or re.match(r"(?i)^0*\.\.?[a-z]+$", v)]

            old_cover = [v for v in zin.namelist() if
                         v.startswith("OldCover_") or re.match(r"(?i)^0*\.\.?[a-z]+$", v)]
            folders_list = [v for v in zin.namelist() if v.endswith("/")]  # Notes all folders to not process them.

            if not any((self.values.coverOverwrite, self.values.coverDelete, cover_matches_000_pattern)):
                return

            self._create_temp_file()

            with zipfile.ZipFile(self.temp_file, 'w') as zout:
                backup = _SingleCoverBackup(zin, zout, self.convert_to_webp)

                is_cover_backed = False

                # Backup any filename that has "cover" in it. If multiple, it selects the first one provided
                if forced_cover and not is_cover_backed:
                    forced_cover_filename = forced_cover[0]
                    # Proceed to back up the cover as OldCover_{}.bak
                    backup.single_cover(forced_cover_filename)
                    file_list.remove(forced_cover_filename)
                    is_cover_backed = True

                # Backup any cover that follows the pattern 0000.ext
                elif cover_matches_000_pattern and not is_cover_backed:
                    forced_cover_filename = cover_matches_000_pattern[0]
                    # Proceed to back up the cover as OldCover_00000.ext.bak
                    backup.single_cover(forced_cover_filename)
                    file_list.remove(forced_cover_filename)
                    is_cover_backed = True

                # No ".*cover.*" and no 000.ext file so backup first image found if overwrite or delete is true
                elif not is_cover_backed and (self.values.coverDelete or self.values.coverOverwrite):
                    for file in file_list:
                        # Check that file is an image.
                        # Any additional file (comicinfo, other backups) should never be treated as cover
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')) is not None:
                            forced_cover_filename = file
                            break
                    # Proceed to back up the cover as OldCover_00000.ext.bak
                    backup.single_cover(forced_cover_filename)
                    file_list.remove(forced_cover_filename)
                    is_cover_backed = True

                # Proceed to add the files to the new file
                for filename in file_list:
                    # Do not save old backup
                    if not filename.startswith("OldCover_"):
                        backup.add_image(filename)

        try:
            os.remove(self.values.zipFilePath)
            os.rename(self.temp_file, self.values.zipFilePath)
        except PermissionError as e:
            logger.error("[SetCover][Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(self.temp_file)
            raise e

        logger.info("[SetCover][Backup] Finished backup")

    def _delete(self):
        # Dummy method to read code better.
        # Cover gets backed earlier up so file is not named the same. Hence, it's deleted
        logger.info("[SetCover][Delete] Finished deleting")

    def _append(self):
        values = self.values
        if not values.coverFilePath or not os.path.exists(values.coverFilePath):
            raise errors.NoCoverFile(values.coverFilePath)

        logger.debug(f"[SetCover][Append] Cover path:{values.coverFilePath} - File path:{values.zipFilePath}")

        new_coverFileName = f"00000.{values.coverFileFormat}"

        with zipfile.ZipFile(values.zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            if self.convert_to_webp:
                zf.writestr(getNewWebpFormatName(new_coverFileName), convertToWebp(values.coverFilePath))
                logger.info(f"[SetCover][append] Finished appending '{getNewWebpFormatName(new_coverFileName)}")
            else:
                zf.write(values.coverFilePath, new_coverFileName)
                logger.info("[SetCover][append] Finished appending")

    def _overwrite(self):
        values = self.values
        if not values.coverFilePath or not os.path.exists(values.coverFilePath):
            raise errors.NoCoverFile(values.coverFilePath)
        # Open saved zip to get the OldCover name. We are using the same name for the new file
        with zipfile.ZipFile(values.zipFilePath, 'r') as zin:
            filenames_list = zin.namelist()
        oldCover_name = [name for name in filenames_list if name.startswith("OldCover_")]

        # os.system("pause")
        if oldCover_name:
            new_coverFileName = oldCover_name[0].replace("OldCover_", "").replace(".bak", "")
        else:
            # print(filenames_list[0])
            new_coverFileName = "00000cover.txt"
        logger.debug(f"[SetCover][Overwrite] Cover path:{values.coverFilePath} - File path:{values.zipFilePath}")
        with zipfile.ZipFile(values.zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            # zf.writestr("debug.txt",f"{filenames_list}\n\n\n{oldCover_name}")
            zf.write(values.coverFilePath, new_coverFileName)
        logger.info("[SetCover][Overwrite] Finished overwriting")

    def _recover_cover(self):
        """
        This renames back OldCover_nameHere.ext.bak to nameHere.ext
        if a nameHere.ext exists, it gets overwritten
        """
        self._create_temp_file()
        tmpname = self.temp_file

        r = r"(?i)^0*\.[a-z]{3}$"
        with zipfile.ZipFile(self.values.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:
                oldCovers_matches = [v for v in zin.namelist() if
                                     re.match(r"OldCover_.*\.bak", v)]
                backedUp_filename = ""
                if oldCovers_matches:
                    logger.info("[SetCover][Backup]Found backed up image")
                    backedUp_filename = re.findall(r"OldCover_(.*)\.bak", oldCovers_matches[0])[0]

                for item in zin.infolist():
                    if not oldCovers_matches and re.match(r, item.filename):
                        continue
                    else:
                        if item.filename == backedUp_filename:
                            # Found the current cover that was replaced. We ignore it so will be deleted
                            logger.debug(f"[SetCover][Backup] Ignoring '{item.filename}'")
                            continue

                        if item.filename in oldCovers_matches:
                            # Found backup image. Adding to new file with original name
                            logger.info("Recovering cover")
                            zout.writestr(backedUp_filename, zin.read(item.filename))
                            logger.debug(
                                f"[SetCover][Backup] Added '{item.filename}' to the new tempfile as '{backedUp_filename}'")
                            continue

                    # Adding file to new file.
                    item_filename = item.filename
                    zout.writestr(item_filename, zin.read(item.filename))
                    logger.debug(f"[SetCover][Backup] Added '{item.filename}' back to the new tempfile")
                    continue

        try:
            os.remove(self.values.zipFilePath)
            os.rename(tmpname, self.values.zipFilePath)
        except PermissionError as e:
            logger.error("[SetCover][Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(tmpname)
            raise e
        logger.info("[SetCover][Backup] Recovery completed")
