import zipfile
import os
import re
import logging
import tempfile

from MangaManager.CoverManagerLib.models import cover_process_item_info
from MangaManager.CoverManagerLib import errors


class SetCover:
    def __init__(self, process_values: cover_process_item_info):
        self.values = process_values
        v = process_values
        self.oldZipFilePath = v.zipFilePath
        # new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", v.zipFilePath)[0])

        tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(v.zipFilePath))
        os.close(tmpfd)
        self.temp_file = tmpname
        logging.info("[SetCover] Proceeding to backup")
        self._backup_cover()

        if v.coverDelete:
            logging.info("[SetCover] Proceeding to delete cover")
            self._delete()
            return
        if v.coverOverwrite:
            logging.info("[SetCover] Proceeding to overwrite cover")
            self._overwrite()
            return
        else:
            logging.info("[SetCover] Proceeding to append cover")
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
                cover_matches = [v for v in zin.namelist() if v.startswith("00000.") or re.match(r, v) or re.match(r"(?i)cover",v)]
                if cover_matches:
                    logging.info("[SetCover][Backup]Found 0000 file")
                    cover_is_000 = True
                backup_isdone = False
                for item in zin.infolist():
                    # Delete existing "OldCover_00.ext.bak file
                    if item.filename.startswith("OldCover_"):
                        continue
                    # If it's folder we copy as it is
                    if is_folder(item.filename, folders_list):  # We write any inner folders as is
                        zout.writestr(item.filename, zin.read(item.filename))
                        continue

                    if item.filename in cover_matches:  # This file is a potential cover

                        # If cover is backed up this is not cover
                        if backup_isdone:
                            if item.filename in processed_files:
                                continue
                            # File is marked as possible cover but cover is backed up. This is not cover, adding to file
                            zout.writestr(item.filename, zin.read(item.filename))
                            logging.debug(f"[SetCover][Backup] Adding {item.filename} to the new tempfile")
                            continue

                        # If there exists 0*.ext.
                        if re.match(r, item.filename):
                            # This file name matches r"0*.ext"
                            newname = f"OldCover_{item.filename}.bak"
                            zout.writestr(newname, zin.read(item.filename))
                            logging.debug(f"[SetCover][Backup] Adding backup '{item.filename}' to the new tempfile")
                            backup_isdone = True
                            processed_files.append(item.filename)
                            continue

                    # Find 001.ext
                    if re.match(r"(?i)^0*1\.[a-z]{3}$", item.filename) and (self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        newname = f"OldCover_{item.filename}.bak"
                        zout.writestr(newname, zin.read(item.filename))
                        logging.info(f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue
                    # Find 002.ext
                    elif re.match(r"(?i)^0*2\.[a-z]{3}$", item.filename) and (self.values.coverOverwrite or self.values.coverDelete) and not backup_isdone:
                        newname = f"OldCover_{item.filename}.bak"
                        zout.writestr(newname, zin.read(item.filename))
                        logging.info(f"[SetCover][Backup][Overwrite/Delete] Adding backup '{item.filename}' to the new tempfile")
                        backup_isdone = True
                        processed_files.append(item.filename)
                        continue

                    # Adding file to new file.
                    # File is not flagged as potential cover
                    item_filename = item.filename
                    zout.writestr(item_filename, zin.read(item.filename))
                    logging.debug(f"[SetCover][Backup] Adding {item.filename} back to the new tempfile")
                    continue


                    # # delete existing "OldCover_00.ext.bak file
                    # if item.filename.startswith("OldCover_"):
                    #     continue
                    #
                    # if item.filename.startswith("00000.") or re.match(r, item.filename):
                    #     if backup_isdone:
                    #         continue
                    #     newname = f"OldCover_{item.filename}.bak"
                    #     zout.writestr(newname, zin.read(item.filename))
                    #     backup_isdone = True
                    #
                    # if is_folder(item.filename, folders_list):  # We write any inner folders as is
                    #     zout.writestr(item_filename, zin.read(item.filename))
                    #     continue
                    # # If there's no 00000.ext file and overwrite or delete is True, making a backup of first image
                    # if (not cover_is_000 or backup_isdone) and (self.values.coverOverwrite or self.values.coverDelete):
                    #     newname = f"OldCover_{item.filename}.bak"
                    #     zout.writestr(newname, zin.read(item.filename))
                    #     backup_isdone = True
                    #     logging.info(f"[Backup] Backed up first image as cover: {item.filename}")
                    #     continue
                    # else:
                    #     item_filename = item.filename
                    #     zout.writestr(item_filename, zin.read(item.filename))
                    #     logging.info(f"[Backup] Adding {item.filename} back to the new tempfile")
                    #     continue
        try:
            os.remove(self.values.zipFilePath)
            os.rename(tmpname, self.values.zipFilePath)
        except PermissionError as e:
            logging.error("[SetCover][Backup] Permission error. Clearing temp files...", exc_info=e)
            os.remove(tmpname)
            raise e

        logging.info("[SetCover][Backup] Finished backup")

    def _delete(self):
        # Dummy method to read code better.
        # Cover gets backed earlier up so file is not named the same. Hence, it's deleted
        logging.info("[SetCover][Delete] Finished deleting")


    def _append(self):
        values = self.values
        if not values.coverFilePath or not os.path.exists(values.coverFilePath):
            raise errors.NoCoverFile(values.coverFilePath)

        logging.debug(f"[SetCover][Append] Cover path:{values.coverFilePath} - File path:{values.zipFilePath}")
        new_coverFileName = f"00000.{values.coverFileFormat}"
        with zipfile.ZipFile(values.zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            zf.write(values.coverFilePath, new_coverFileName)
        logging.info("[SetCover][append] Finished appending")
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
        logging.debug(f"[SetCover][Overwrite] Cover path:{values.coverFilePath} - File path:{values.zipFilePath}")
        with zipfile.ZipFile(values.zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
            # zf.writestr("debug.txt",f"{filenames_list}\n\n\n{oldCover_name}")
            zf.write(values.coverFilePath, new_coverFileName)
        logging.info("[SetCover][Overwrite] Finished overwriting")



# class cbz_handler:
#
#
#
#
#
#
#
#
#
#
#     def backup_delete_first_cover(new_zipFilePath, tmpname,overwrite=None):
#         backup_isdone = False
#         def is_folder(name:str,folders_list):
#             if name.split("/")[0] + "/" in folders_list:
#                 return True
#             else:
#                 return False
#         with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
#             with zipfile.ZipFile(tmpname, 'w') as zout:
#                 # old_cover_filename = [v for v in zin.namelist() if v.startswith("OldCover_")]  # Find "OldCover_ file
#                 folders_list = [v for v in zin.namelist() if v.endswith("/")]  # Notes all folders to not process them.
#                 for item in zin.infolist():
#                     delog(f"[Backup] Iterating: " + item.filename)
#                     if item.filename.startswith("OldCover_"):  # delete existing "OldCover_00.ext.bak file from the zip
#                         continue
#
#                     if is_folder(item.filename, folders_list):  # We skip any file inside directory (for now)
#                         continue
#
#                     if not backup_isdone:
#                         # delog(f"File is cover/first and backup not done: {item.filename}")
#                         # We save the current cover with different name to back it up
#                         r = r"(?i)^0*\.[a-z]{3}$"
#                         if item.filename.startswith("000000000000.") or re.match(r, item.filename): # backup current first cover
#                             newname = f"OldCover_{item.filename}.bak"
#                             # zout.writestr(newname, zin.read(item.filename))
#                             backup_isdone = True
#                             delog(f"[Backup] Backed up customized first cover {item.filename}.")
#                             break
#
#
#
#
#     def backup_delete_comicinfo(new_zipFilePath, tmpname):
#         backup_isdone = False
#         def is_folder(name:str,folders_list):
#             if name.split("/")[0] + "/" in folders_list:
#                 return True
#             else:
#                 return False
#         with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
#             with zipfile.ZipFile(tmpname, 'w') as zout:
#                 # old_cover_filename = [v for v in zin.namelist() if v.startswith("OldCover_")]  # Find "OldCover_ file
#                 folders_list = [v for v in zin.namelist() if v.endswith("/")]  # Notes all folders to not process them.
#                 for item in zin.infolist():
#                     delog(f"[ComicInfoRemover][Processing][doRemoveComicinfo][Backup]Iterating: " + item.filename)
#                     if item.filename == "ComicInfo.xml":  # delete existing "OldCover_00.ext.bak file from the zip
#                         continue
#
#                     if is_folder(item.filename, folders_list):  # We skip any file inside directory (for now)
#                         continue
#
#                     if not backup_isdone:
#                         # delog(f"File is cover/first and backup not done: {item.filename}")
#                         # We save the current cover with different name to back it up
#                         r = r"(?i)comicinfo.xml"
#                         if re.match(r, item.filename): # backup current first cover
#                             newname = f"OldComInf_{item.filename}.bak"
#                             zout.writestr(newname, zin.read(item.filename))
#                             backup_isdone = True
#                             delog(f"[ComicInfoRemover][Processing][doRemoveComicinfo][Backup] Backed up old ComicInfo {item.filename}.")
#                             break
#
#
#
#                 for item in zin.infolist():
#                     r = r"(?i)^comicinfo.xml$"
#                     if re.match(r, item.filename):  # ignore old comicinfo already in file with new name
#                         delog(f"[ComicInfoRemover][Processing][doRemoveComicinfo][Backup] Deleting" + item.filename)
#                         continue
#                     if is_folder(item.filename, folders_list):  # We skip any file inside directory (for now)
#                         zout.writestr(item.filename, zin.read(item.filename))
#
#                         continue
#                     else:
#                         item_filename = item.filename
#                         zout.writestr(item_filename, zin.read(item.filename))
#                         delog(f"[ComicInfoRemover][Processing][doRemoveComicinfo][Backup] Adding {item.filename} back to the new tempfile")
#                         continue
#
#     def doRemoveComicinfo(zipFilePath):
#         oldZipFilePath = zipFilePath
#         new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", zipFilePath)[0])
#         delog(f"[ComicInfoRemover][Processing][doRemoveComicinfo] -  {new_zipFilePath}")
#         os.rename(zipFilePath, new_zipFilePath)
#         tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
#         os.close(tmpfd)
#         backup_delete_comicinfo(new_zipFilePath, tmpname)  # Overwrite true because we want to backup the cover with different name
#
#         # checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)
#
#         os.remove(new_zipFilePath)
#         os.rename(tmpname, new_zipFilePath)
#         os.rename(new_zipFilePath, oldZipFilePath)
#
#     def doDeleteCover(zipFilePath):
#
#         oldZipFilePath = zipFilePath
#         new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", zipFilePath)[0])
#         delog(f"Inside doDeleteCover - .cbz will be renamed to {new_zipFilePath}")
#         os.rename(zipFilePath, new_zipFilePath)
#
#         tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
#         os.close(tmpfd)
#         backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=True) # Overwrite true because we want to backup the cover with different name
#
#         # checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)
#
#         os.remove(new_zipFilePath)
#         os.rename(tmpname, new_zipFilePath)
#         os.rename(new_zipFilePath, oldZipFilePath)
#
#
#     def doUpdateZip(values: cover_process_item_info):
#         velog("Updating file (overwriting 0001.ext)")
#         v = values
#
#
#         try:
#             os.rename(v.zipFilePath, new_zipFilePath)
#         except PermissionError as e:
#             mb.showerror("Can't access the file because it's being used by a different process", f"Exception:{e}")
#         tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(v.zipFilePath))
#         os.close(tmpfd)
#         backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=True)
#
#
#         os.remove(new_zipFilePath)
#         os.rename(tmpname, new_zipFilePath)
#         with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
#             zf.write(v.coverFilePath, new_coverFileName)
#         os.rename(new_zipFilePath, v.zipFilePath)
#         logging.info("Finished processing of file")
#
#
#     def doAppendZip(values: cover_process_item_info):
#         velog("Append file (append 0001.ext)")
#         v = values
#         new_zipFilePath = "{}.zip".format(re.findall(r'(?i)(.*)(?:\.[a-z]{3})$', v.zipFilePath)[0])
#         try:
#             os.rename(v.zipFilePath, new_zipFilePath)
#         except PermissionError as e:
#             mb.showerror("Can't access the file because it's being used by a different process", f"Exception:{e}")
#         tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(new_zipFilePath))
#         os.close(tmpfd)
#
#         backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=False)
#
#         new_coverFileName = f"000000000000{v.coverFileFormat}"
#         os.remove(new_zipFilePath)
#         os.rename(tmpname, new_zipFilePath)
#         with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
#             zf.write(v.coverFilePath, new_coverFileName)
#         os.rename(new_zipFilePath, v.zipFilePath)
#         velog("Finished processing of file")


# if __name__ == "__main__":
#     path_23 = r"I:\Mi unidad\Programacion\Python\MangaManagerProject\tests\Sample CBZ Chapter 23.cbz"
#     path_24 = r"I:\Mi unidad\Programacion\Python\ASCRIPT_MANGA_ZIPPER\tests\Sample CBZ Chapter 24.cbz"
#     test_path = path_23
#     with zipfile.ZipFile(test_path, 'r') as zin:
#         item_count = len(zin.namelist())
#         print("\n".join(zin.namelist()))
#     values_to_process = cover_process_item_info(cbz_file=test_path)
#     SetCover(values_to_process).append()
#
#     with zipfile.ZipFile(test_path, 'r') as zin:
#         item_count2 = len(zin.namelist())
#         print("newResult")
#         print("\n".join(zin.namelist()))
#
#     if item_count == item_count2:
#         print(f"####\n{item_count}\nSAME CONTENT\n{item_count2}\n####")


