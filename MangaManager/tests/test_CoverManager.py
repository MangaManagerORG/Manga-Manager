import io
import os
import pathlib
import random
import tempfile
import unittest
import zipfile

from PIL import Image

from CoverManagerLib.cbz_handler import SetCover
from CoverManagerLib.models import cover_process_item_info


class CoverManagerTester(unittest.TestCase):
    """
    This test checks the functionality of coverManager and makes sure that the content of the files do not get wiped
    """

    def setUp(self) -> None:
        self.test_files_names = []  # Simulated list of filepaths
        print("\n", self._testMethodName)
        print("Setup:")
        image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
        image.format = "JPEG"
        imgByteArr = io.BytesIO()
        image.save(imgByteArr, format=image.format)
        imgByteArr = imgByteArr.getvalue()
        for ai in range(3):  # Create 3 archives.cbz
            out_tmp_zipname = f"Test_{ai}_{random.randint(1, 6000)}.cbz"
            self.test_files_names.append(os.path.abspath(out_tmp_zipname))
            self.temp_folder = tempfile.mkdtemp()
            print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)

            with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
                for i in range(1, 6):
                    zf.writestr(f"{str(i).zfill(3)}.jpg", imgByteArr)

        image.save("Test_4_sample_cover.jpg", format=image.format)
        self.test_files_names.append(os.path.abspath("Test_4_sample_cover.jpg"))
        self.sample_cover = os.path.abspath("Test_4_sample_cover.jpg")
        self.initial_dir_count = len(os.listdir(os.getcwd()))

    def tearDown(self) -> None:
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_appendCover_ShouldAppendOne(self):
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count = len(zin.namelist())

        values_to_process = cover_process_item_info(
            cbz_file=self.test_files_names[0],
            cover_path=self.sample_cover,
            cover_format="jpg"
        )
        SetCover(values_to_process)
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count2 = len(zin.namelist())
        print(f"Asserting new file has original files + new cover since its appended - {item_count} vs {item_count2}")
        self.assertEqual((item_count + 1), item_count2)

        print(pathlib.Path(self.test_files_names[0]))
        # print(os.path.dirname(self.test_files_names[0]))
        final_dir_count = len(os.listdir(os.path.dirname(self.test_files_names[0])))
        print(f"Asserting {self.initial_dir_count} vs {final_dir_count}")
        self.assertEqual(self.initial_dir_count, final_dir_count)

    def test_appendCover_ShouldOverwriteFirst(self):
        # Append one image named 0000.ext
        with zipfile.ZipFile(self.test_files_names[0], mode='a') as zf:
            image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
            image.format = "JPEG"
            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format=image.format)
            imgByteArr = imgByteArr.getvalue()
            zf.writestr(f"0000.jpg", imgByteArr)
        # Count files in archive
        with zipfile.ZipFile(self.test_files_names[0], mode='r') as zin:
            item_count = len(zin.namelist())
        values_to_process = cover_process_item_info(
            cbz_file=self.test_files_names[0],
            cover_path=self.sample_cover,
            cover_format="jpg"
        )
        # Append cover
        SetCover(values_to_process)
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count2 = len(zin.namelist())
        print(
            f"Asserting new file has original files + 1. First cover should be backed up since named 0000.ext - {item_count} vs {item_count2 - 1}")
        self.assertEqual(item_count, item_count2 - 1)

        final_dir_count = len(os.listdir(os.path.dirname(self.test_files_names[0])))
        print(f"Asserting {self.initial_dir_count} vs {final_dir_count}")
        self.assertEqual(self.initial_dir_count, final_dir_count)

    def test_overwriteCover(self):
        # Count files in archive
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count = len(zin.namelist())
        values_to_process = cover_process_item_info(
            cbz_file=self.test_files_names[0],
            cover_path=self.sample_cover,
            cover_format="jpg",
            coverOverwrite=True
        )
        # Overwrite cover
        SetCover(values_to_process)
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count2 = len(zin.namelist())
        print(
            f"Asserting new file has original files. First image should be backed up- {item_count} vs {item_count2 - 1}")
        self.assertEqual(item_count, item_count2 - 1)

        final_dir_count = len(os.listdir(os.path.dirname(self.test_files_names[0])))
        print(f"Asserting {self.initial_dir_count} vs {final_dir_count}")
        self.assertEqual(self.initial_dir_count, final_dir_count)

    def test_deleteCover(self):
        # Count files in archive
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count = len(zin.namelist())
        values_to_process = cover_process_item_info(
            cbz_file=self.test_files_names[0],
            cover_path=self.sample_cover,
            cover_format="jpg",
            coverDelete=True,
        )
        # Delete cover
        SetCover(values_to_process)
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count2 = len(zin.namelist())
        print(f"Asserting new file has original files. First image should be backed up - {item_count} vs {item_count2}")
        self.assertEqual(item_count, item_count2)

        final_dir_count = len(os.listdir(os.path.dirname(self.test_files_names[0])))
        print(f"Asserting {self.initial_dir_count} vs {final_dir_count}")
        self.assertEqual(self.initial_dir_count, final_dir_count)

    def test_recoverCover(self):
        # Append OldCover_*.ext.bak
        with zipfile.ZipFile(self.test_files_names[0], mode="a") as zf:
            image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
            image.format = "JPEG"
            imgByteArr = io.BytesIO()
            image.save(imgByteArr, format=image.format)
            imgByteArr = imgByteArr.getvalue()
            zf.writestr(f"OldCover_0000.jpg.bak", imgByteArr)
        # Count files in archive
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count = len(zin.namelist())
        values_to_process = cover_process_item_info(
            cbz_file=self.test_files_names[0],
            cover_path=self.sample_cover,
            cover_format="jpg",
            coverRecover=True
        )
        # Delete cover
        SetCover(values_to_process)
        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            item_count2 = len(zin.namelist())
            print("Asserting renamed file 0000.ext is in namelist")
            print(zin.namelist())
            self.assertTrue("0000.jpg" in zin.namelist())
        print(
            f"Asserting new file has original files. OldCover should be renamed to 000.ext - {item_count} vs {item_count2}")
        self.assertEqual(item_count, item_count2)

        final_dir_count = len(os.listdir(os.path.dirname(self.test_files_names[0])))
        print(f"Asserting {self.initial_dir_count} vs {final_dir_count}")
        self.assertEqual(self.initial_dir_count, final_dir_count)
