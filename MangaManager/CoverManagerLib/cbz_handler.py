import logging
import os
import re
import tempfile
import zipfile

from CommonLib.WebpConverter import convertToWebp, getNewWebpFormatName, supportedFormats
from . import errors
from .models import cover_process_item_info

logger = logging.getLogger(__name__)


class SetCover:
    def __init__(self, process_values: cover_process_item_info, conver_to_webp=False):
        self.values = process_values
        self.conver_to_webp = conver_to_webp

        v = process_values
        self.oldZipFilePath = v.zipFilePath
        # new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", v.zipFilePath)[0])

        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(v.zipFilePath))
        os.close(tmpfd)
        self.temp_file = tmpname
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

        tmpname = self.temp_file
        # backup_isdone = False

        def is_folder(name: str, folders_list):
            if name.split("/")[0] + "/" in folders_list:
                return True
            else:
                return False
        cover_is_000 = False
        r = r"(?i)^0*\.[a-z]{3}$"

        with zipfile.ZipFile(self.values.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:
                processed_files = []
                # old_cover_filename = [v for v in zin.namelist() if v.startswith("OldCover_")]  # Find "OldCover_ file
                folders_list = [v for v in zin.namelist() if v.endswith("/")]  # Notes all folders to not process them.
                # for item in zin.infolist():
                cover_matches = [v for v in zin.namelist() if
                                 v.startswith("00000.") or re.match(r, v) or re.match(r"(?i).*cover.*", v)]
                if cover_matches:
                    logger.info("[SetCover][Backup] Found 0000 file")
                    cover_is_000 = True
                backup_isdone = False
                for item in zin.infolist():

                    # Delete existing "OldCover_00.ext.bak file
                    if item.filename.startswith("OldCover_"):
                        continue
                    # If it's folder we copy as it is
                    if is_folder(item.filename, folders_list):  # We write any inner folders as is
                        if self.conver_to_webp:
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(getNewWebpFormatName(item.filename), convertToWebp(open_zipped_file))
                        else:
                            zout.writestr(item.filename, zin.read(item.filename))
                        continue

                    # If it's a file with a format not supported by converter we save it as it is
                    file_format = re.findall(r"(?i)\.[a-z]+$", item.filename)
                    if file_format:
                        if not file_format[0] in supportedFormats:
                            zout.writestr(item.filename, zin.read(item.filename))
                            logger.debug(f"Added '{item.filename}' to new tempfile. File was not processed")
                            continue

                    if item.filename in cover_matches:  # This file is a potential cover

                        # If cover is backed up this is not cover
                        if backup_isdone:
                            if item.filename in processed_files:
                                continue
                            # File is marked as possible cover but cover is backed up. This is not cover, adding to file
                            if self.conver_to_webp:
                                with zin.open(item.filename) as open_zipped_file:
                                    zout.writestr(getNewWebpFormatName(item.filename), convertToWebp(open_zipped_file))
                                    logger.debug(
                                        f"[SetCover][Backup] Adding '{getNewWebpFormatName(item.filename)}' to the new tempfile")
                            else:
                                zout.writestr(item.filename, zin.read(item.filename))
                                logger.debug(f"[SetCover][Backup] Adding '{item.filename}' to the new tempfile")
                            continue

                        # If there exists 0*.ext.
                        if re.match(r, item.filename):
                            # This file name matches r"0*.ext"

                            if self.conver_to_webp:
                                newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                                with zin.open(item.filename) as open_zipped_file:
                                    zout.writestr(newname, convertToWebp(open_zipped_file))
                                    logger.debug(
                                        f"[SetCover][Backup] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                            else:
                                newname = f"OldCover_{item.filename}.bak"
                                zout.writestr(newname, zin.read(item.filename))
                                logger.debug(
                                    f"[SetCover][Backup] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                            backup_isdone = True
                            processed_files.append(item.filename)
                            continue

                    # Find 001.ext
                    if re.match(r"(?i)^0*1\.[a-z]{3}$", item.filename) and (
                            self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:

                        if self.conver_to_webp:
                            newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(newname, convertToWebp(open_zipped_file))
                        else:
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                        logger.info(
                            f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Find 002.ext
                    elif re.match(r"(?i)^0*2\.[a-z]{3}$", item.filename) and (
                            self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        if self.conver_to_webp:
                            newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(newname, convertToWebp(open_zipped_file))
                        else:
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                        logger.info(
                            f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Find 003.ext
                    elif re.match(r"(?i)^0*3\.[a-z]{3}$", item.filename) and (
                            self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        if self.conver_to_webp:
                            newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(newname, convertToWebp(open_zipped_file))
                        else:
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                        logger.info(
                            f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Find 004.ext
                    elif re.match(r"(?i)^0*4\.[a-z]{3}$", item.filename) and (
                            self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        if self.conver_to_webp:
                            newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(newname, convertToWebp(open_zipped_file))
                        else:
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                        logger.info(
                            f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Find 00.ext
                    elif re.match(r"(?i)^0*\.[a-z]{3}$", item.filename) and (
                            self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        if self.conver_to_webp:
                            newname = f"OldCover_{getNewWebpFormatName(item.filename)}.bak"
                            with zin.open(item.filename) as open_zipped_file:
                                zout.writestr(newname, convertToWebp(open_zipped_file))
                        else:
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                        logger.info(
                            f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile as '{newname}'")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Adding file to new file.
                    # File is not flagged as potential cover
                    item_filename = item.filename
                    if self.conver_to_webp:
                        with zin.open(item.filename) as open_zipped_file:
                            zout.writestr(getNewWebpFormatName(item.filename), convertToWebp(open_zipped_file))
                        logger.debug(
                            f"[SetCover][Backup] Adding '{getNewWebpFormatName(item.filename)}' back to the new tempfile")
                    else:
                        zout.writestr(item_filename, zin.read(item.filename))
                        logger.debug(f"[SetCover][Backup] Adding '{item.filename}' back to the new tempfile")
                    continue

        try:
            os.remove(self.values.zipFilePath)
            os.rename(tmpname, self.values.zipFilePath)
        except PermissionError as e:
            logger.error("[SetCover][Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(tmpname)
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
            if self.conver_to_webp:
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
