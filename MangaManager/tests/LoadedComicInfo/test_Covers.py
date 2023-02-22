import io
import unittest
import zipfile

from PIL import Image

from src.Common.LoadedComicInfo.LoadedComicInfo import CoverActions, LoadedComicInfo
from src.Common.utils import obtain_cover_filename
from tests.common import CBZManipulationTests, create_test_cbz


class LoadedCInfo_Utils(unittest.TestCase):
    def test_CoverParsing(self):
        list_filenames_to_test = [
            ("000001.jpg", ("0_ not valid image file 00001.jpg", "000001.jpg", "000002.jpg",
                            "this is a random image from page 4.png")),
            ("cover_0001.jpg", ("cover_0001.jpg", "0_ not valid image file 00001.jpg", "000001.jpg", "000002.jpg",
                                "this is a random image from page 4.png"))
        ]
        print("Running unit tests for cover filename parsing")
        for filename in list_filenames_to_test:
            with self.subTest(f"Subtest - Parsed name should match {filename[0]}"):
                selected = str(obtain_cover_filename(filename[1])[0])
                print(f"Selected file is: {selected}")
                self.assertEqual(filename[0], selected)

        # self.assertEqual(True, False)  # add assertion here

class CoverHandling_Recompressing_Tests(CBZManipulationTests):
    def setUp(self) -> None:
        super().setUp()
        self.test_files_names = create_test_cbz(2)
        image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
        image.format = "JPEG"
        # imgByteArr = io.BytesIO()
        self.test_image_file = "Test__new_cover.jpeg"
        image.save("Test__new_cover.jpeg", format=image.format)
        self.test_files_names.append("Test__new_cover.jpeg")

    def test_delete_cover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.cover_action = CoverActions.DELETE
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image less")
                self.assertEqual(3, len(zf.namelist()))

    def test_delete_backcover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.backcover_action = CoverActions.DELETE
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image less")
                self.assertEqual(3, len(zf.namelist()))

    def test_append_cover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.cover_action = CoverActions.APPEND
            lcinfo.new_cover_path = self.test_image_file
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image more")
                self.assertEqual(5, len(zf.namelist()))

    def test_append_backcover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.backcover_action = CoverActions.APPEND
            lcinfo.new_backcover_path = self.test_image_file
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image more")
                self.assertEqual(5, len(zf.namelist()))
                self.assertTrue(obtain_cover_filename(zf.namelist())[1].startswith("~99"))


    def test_replace_cover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.cover_action = CoverActions.REPLACE
            lcinfo.new_cover_path = self.test_image_file
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image more")
                self.assertEqual(4, len(zf.namelist()))
                image_data = zf.read(obtain_cover_filename(zf.namelist())[0])
                image = Image.open(io.BytesIO(image_data))
                image_color = image.getpixel((0,0))
                self.assertFalse(image_color == (255,255,255))

    def test_replace_backcover(self):
        for file in self.test_files_names:
            if not file.endswith(".cbz"):
                continue
            lcinfo = LoadedComicInfo(file).load_cover_info(False)
            lcinfo.backcover_action = CoverActions.REPLACE
            lcinfo.new_backcover_path = self.test_image_file
            lcinfo._process(False, False)
            with zipfile.ZipFile(file, "r") as zf:
                print("Asserting the processed file has one image more")
                self.assertEqual(4, len(zf.namelist()))
                image_data = zf.read(obtain_cover_filename(zf.namelist())[1])
                image = Image.open(io.BytesIO(image_data))
                image_color = image.getpixel((0,0))
                self.assertFalse(image_color == (255,255,255))

