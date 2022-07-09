import pathlib
import random
import tkinter as tk
import unittest

from PIL import Image

from MangaManager.VolumeManager import VolumeManager
from MetadataManagerLib.cbz_handler import *


class VolumeManagerTester(unittest.TestCase):
    def setUp(self) -> None:
        self.test_files_names = []  # Simulated list of filepaths
        print("\n", self._testMethodName)
        print("Setup:")
        image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
        image.format = "JPEG"
        imgByteArr = io.BytesIO()
        self.random_series_name = f"Test_{random.randint(1, 6000)}"
        image.save(imgByteArr, format=image.format)
        imgByteArr = imgByteArr.getvalue()
        for ai in range(1, 7):  # Create 7 archives.cbz
            out_tmp_zipname = f"Test_{ai}_{random.randint(1, 6000)} Ch.{ai}.cbz"
            self.test_files_names.append(os.path.abspath(out_tmp_zipname))
            self.temp_folder = tempfile.mkdtemp()
            print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)
            cinfo = ComicInfo.ComicInfo()
            cinfo.set_Series(self.random_series_name)
            export_io = io.StringIO()
            cinfo.export(export_io, 0)
            _export_io = export_io.getvalue()
            with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
                for i in range(1, 6):
                    zf.writestr(f"{str(i).zfill(3)}.jpg", imgByteArr)
                zf.writestr("ComicInfo.xml", _export_io)
        self.initial_dir_count = len(os.listdir(os.getcwd()))

    def tearDown(self) -> None:
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_rename(self):

        test_path = self.test_files_names[0]

        random_vol_number = random.randint(1, 500)
        test_path_dir = os.path.dirname(test_path)
        file_regex_finds = VolumeManager.parse_fileName(test_path, random_vol_number)
        new_file_path = os.path.dirname(test_path)
        new_fileName_toAssert = str(pathlib.Path(new_file_path,
                                                 f"{file_regex_finds.name} Vol.{random_vol_number} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}".replace(
                                                     "  ", " ")))

        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            initial_dir_count = len(zin.namelist())
        root = tk.Tk()
        app = VolumeManager.App(root)
        app.cli_set_volume(random_vol_number)
        app.cli_select_files([test_path])
        self.test_files_names[0] = new_fileName_toAssert
        # app.checkbutton_4_settings_val.set(True)  # Enables saving to comicinfo
        app.process()
        print(f"Asserting if renamed file exists in directory ({os.path.basename(new_fileName_toAssert)} in Folder)")
        items_in_test_path_dir = os.listdir(test_path_dir)
        self.assertTrue(os.path.basename(new_fileName_toAssert) in items_in_test_path_dir)

    # @unittest.SkipTest
    def test_addVolume_toComicInfo(self):

        test_path = self.test_files_names[0]
        with zipfile.ZipFile(test_path, 'r') as zin:
            initial_dir_count = len(zin.namelist())
        random_vol_number = random.randint(1, 500)
        test_path_dir = os.path.dirname(test_path)
        new_file_path = os.path.dirname(test_path)
        with zipfile.ZipFile(test_path, 'r') as zin:
            initial_dir_count = len(zin.namelist())
        root = tk.Tk()
        app = VolumeManager.App(root)
        app.checkbutton_4_5_settings_val.set(True)  # Do not rename the file
        app.checkbutton_4_settings_val.set(True)  # Enables saving to comicinfo
        app.cli_set_volume(random_vol_number)
        app.cli_select_files([test_path])
        app.process()

        app = ReadComicInfo(test_path, ignore_empty_metadata=False).to_ComicInfo()

        with zipfile.ZipFile(test_path, 'r') as zin:
            final_dir_count = len(zin.namelist())

        print(f"Asserting if new volume number in comicinfo is saved ({random_vol_number}=={app.get_Volume()})")
        self.assertEqual(random_vol_number, app.get_Volume())

        # final_dir_count = len(os.listdir(os.path.dirname(test_path)))
        print(f"Asserting leftover files {initial_dir_count} vs {final_dir_count}")
        self.assertEqual(initial_dir_count, (final_dir_count - 1))

        print("Asserting series name is kept")
        self.assertEqual(self.random_series_name, app.get_Series())

    def test_addVolume_and_rename(self):

        test_path = self.test_files_names[0]

        random_vol_number = random.randint(1, 500)
        test_path_dir = os.path.dirname(test_path)
        file_regex_finds = VolumeManager.parse_fileName(test_path, random_vol_number)
        new_file_path = os.path.dirname(test_path)
        new_fileName_toAssert = str(pathlib.Path(new_file_path,
                                                 f"{file_regex_finds.name} Vol.{random_vol_number} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}".replace(
                                                     "  ", " ")))

        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            initial_dir_count = len(zin.namelist())
        root = tk.Tk()
        app = VolumeManager.App(root)
        app.cli_set_volume(random_vol_number)
        app.cli_select_files([test_path])
        self.test_files_names[0] = new_fileName_toAssert
        app.checkbutton_4_settings_val.set(True)  # Enables saving to comicinfo
        app.process()
        print(f"Asserting if renamed file exists in directory ({os.path.basename(new_fileName_toAssert)} in Folder)")
        items_in_test_path_dir = os.listdir(test_path_dir)
        self.assertTrue(os.path.basename(new_fileName_toAssert) in items_in_test_path_dir)

        app = ReadComicInfo(new_fileName_toAssert, ignore_empty_metadata=False).to_ComicInfo()
        print(f"Asserting if new volume number in comicinfo is saved ({random_vol_number}=={app.get_Volume()})")
        self.assertEqual(random_vol_number, app.get_Volume())
        with zipfile.ZipFile(new_fileName_toAssert, 'r') as zin:
            final_dir_count = len(zin.namelist())
        # final_dir_count = len(os.listdir(os.path.dirname(test_path)))
        print(f"Asserting leftover files {initial_dir_count} vs {final_dir_count}")
        self.assertEqual(initial_dir_count, (final_dir_count - 1))


#
#
# class Epub2CbzTester(unittest.TestCase):
#     # TODO: This unit test needs to be rewritten. It's too messy
#     def setUp(self) -> None:
#         self.newEpubFileName = "TestEpub.epub"
#         self.newEpubFilePath = rf"{os.getcwd()}/{self.newEpubFileName}"
#         self.generatedImagesNumber = random.randint(1, 15)
#         with ZipFile(self.newEpubFilePath, "w") as zout:
#             for newFile_number in range(self.generatedImagesNumber):
#                 new_name = f"{newFile_number}".zfill(3)
#                 zout.write(sample_cover, f"images/{new_name}.jpg")
#
#         self.root = tk.Tk()
#
#     def test_convert(self):
#         app = epub2cbz.App(self.root, [self.newEpubFilePath])
#         app.output_folder = os.getcwd()
#
#         newCbzPath = (os.getcwd() + "/" + self.newEpubFileName).replace(
#             re.findall(r"(?i).*(\.[a-z]+$)", self.newEpubFilePath)[0]
#             , ".cbz")
#         app.start()
#         app = None
#         try:
#             with ZipFile(newCbzPath, 'r') as zipCbz:
#                 print("")
#                 print(
#                     f"Assert number of files in epub/images == files in cbz -> {len(zipCbz.namelist())}=={self.generatedImagesNumber}")
#                 self.assertEqual(len(zipCbz.namelist()), self.generatedImagesNumber)
#         except AssertionError as e:
#             os.remove(self.newEpubFilePath)
#             os.remove(newCbzPath)
#             raise e
#         except PermissionError as e:
#             print("Can't delete the files")
#             raise e
#
#         try:
#             os.remove(self.newEpubFilePath)
#             os.remove(newCbzPath)
#         except Exception as e:
#             pass
#

if __name__ == '__main__':
    unittest.main()
