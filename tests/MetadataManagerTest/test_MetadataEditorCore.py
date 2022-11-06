import os
import unittest
import zipfile
from unittest.mock import patch

from src.MangaManager_ThePromidius.MetadataManager import comicinfo
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib
from src.MangaManager_ThePromidius.MetadataManager.cbz_handler import LoadedComicInfo
from src.MangaManager_ThePromidius.MetadataManager.errors import NoMetadataFileFound


class CoreTesting(unittest.TestCase):
    def setUp(self) -> None:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)

    @patch.multiple(MetadataManagerLib, __abstractmethods__=set())
    def test(self):
        self.instance = MetadataManagerLib()
        # Test merging is done correctly:

        out_tmp_zipname = f"random_image_1_not_image.ext.cbz"
        out_tmp_zipname2 = f"random_image_1_not_image.ext.cbz"
        self.test_files_names = []

        with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
            zf.writestr("Dummyfile.ext", "Dummy")
        with zipfile.ZipFile(out_tmp_zipname2, "w") as zf:
            zf.writestr("Dummyfile.ext", "Dummy")
        print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)
        # Create a random int so the values in the cinfo are unique each test

        # Create metadata objects
        cinfo_1 = comicinfo.ComicInfo()
        cinfo_1.set_Series("This series from file 1 should be kept")
        cinfo_1.set_Writer("This writer from file 1 should NOT be kept")

        cinfo_2 = comicinfo.ComicInfo()
        cinfo_2.set_Series("This series from file 2 should be kept")
        cinfo_2.set_Writer("This writer from file 1 should NOT be kept")

        # Created loaded metadata objects
        metadata_1 = LoadedComicInfo(out_tmp_zipname, comicinfo=cinfo_1)
        metadata_2 = LoadedComicInfo(out_tmp_zipname2, comicinfo=cinfo_2)

        self.instance.loaded_cinfo_list = [metadata_1, metadata_2]

        # There is no edited comicinfo, it should fail
        self.assertRaises(NoMetadataFileFound, self.instance.merge_changed_metadata)
