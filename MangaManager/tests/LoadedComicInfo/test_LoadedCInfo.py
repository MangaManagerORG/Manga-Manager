import io
import os
import random
import tempfile
import unittest
import zipfile

from common.models import ComicInfo
from src.Common.loadedcomicinfo import LoadedComicInfo

TEST_COMIC_INFO_STRING = """
<ComicInfo>
    <Title>Title</Title>
    <AlternateSeries>AlternateSeries</AlternateSeries>
    <Summary>Summary</Summary>
    <Notes>Notes</Notes>
    <Writer>Writer</Writer>
    <Inker>Inker</Inker>
    <Colorist>Colorist</Colorist>
    <Letterer>Letterer</Letterer>
    <CoverArtist>CoverArtist</CoverArtist>
    <Editor>Editor</Editor>
    <Translator>Translator</Translator>
    <Publisher>Publisher</Publisher>
    <Imprint>Imprint</Imprint>
    <Genre>Genre</Genre>
    <Tags>Tags</Tags>
    <Web>Web</Web>
    <Characters>Characters</Characters>
    <Teams>Teams</Teams>
    <Locations>Locations</Locations>
    <ScanInformation>ScanInformation</ScanInformation>
    <StoryArc>StoryArc</StoryArc>
    <SeriesGroup>SeriesGroup</SeriesGroup>
    <AgeRating>Unknown</AgeRating>
    <CommunityRating>3</CommunityRating>
</ComicInfo>
"""


class LoadedComicInfo_MetadataTests(unittest.TestCase):
    """
    The purpose of this Test case is to test the LoadedComicInfo class against simple scenarios where
    it's only the comicinfo.xml file
    """

    def setUp(self) -> None:
        print(os.getcwd())
        # Make sure there are no test files else delete them:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")
                          or listed.startswith("tmp")]
        for file in leftover_files:
            os.remove(file)
        self.test_files_names = []
        print("\n", self._testMethodName)
        print("Setup:")
        self.random_int = random.random() + random.randint(1, 40)
        for ai in range(3):
            out_tmp_zipname = f"Test__{ai}_{random.randint(1, 6000)}.cbz"
            self.test_files_names.append(out_tmp_zipname)
            self.temp_folder = tempfile.mkdtemp()
            print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)
            # Create a random int so the values in the cinfo are unique each test

            with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
                zf.writestr("Dummyfile1.ext", "Dummy")
                zf.writestr("Dummyfile2.ext", "Dummy")
                zf.writestr("Dummyfile3.ext", "Dummy")
                zf.writestr("Dummyfile4.ext", "Dummy")
                cinfo = ComicInfo()
                cinfo.series = f"Series-{ai}-{self.random_int}"
                cinfo.writer = f"Writer-{ai}-{self.random_int}"
                zf.writestr("ComicInfo.xml", str(cinfo.to_xml()))
            self.initial_dir_count = len(os.listdir(os.getcwd()))

    def tearDown(self) -> None:
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_simple_read(self):
        for i, file_names in enumerate(self.test_files_names):
            with self.subTest(f"Testing individual file read metadata - {i + 1}/{len(self.test_files_names)}"):
                cinfo = LoadedComicInfo(file_names).load_metadata()
                self.assertEqual(f"Series-{i}-{self.random_int}", cinfo.cinfo_object.series)
                self.assertEqual(f"Writer-{i}-{self.random_int}", cinfo.cinfo_object.writer)

    def test_simple_write(self):
        print("Writing new values")
        for i, file_names in enumerate(self.test_files_names):
            with self.subTest(f"Testing individual file read metadata - {i + 1}/{len(self.test_files_names)}"):
                cinfo = LoadedComicInfo(file_names).load_metadata()
                cinfo.cinfo_object.notes = f"This text was modified - {self.random_int}"
                cinfo.write_metadata()


        print("Test files keep all images")
        for file_names in self.test_files_names:
            with zipfile.ZipFile(file_names, "r") as zf:
                self.assertAlmostEqual(len(zf.namelist()), 5,delta=1)
        # check changes are saved
        print("Testing reading saved values")
        for i, file_names in enumerate(self.test_files_names):
            with self.subTest(f"Testing individual write metadata - {i + 1}/{len(self.test_files_names)}"):
                cinfo = LoadedComicInfo(file_names).load_metadata()
                self.assertEqual(f"This text was modified - {self.random_int}", cinfo.cinfo_object.notes)

    def test_simple_backup(self):
        for i, file_names in enumerate(self.test_files_names):
            with self.subTest(f"Backing up individual metadata - {i + 1}/{len(self.test_files_names)}"):
                cinfo = LoadedComicInfo(file_names).load_metadata()
                cinfo.write_metadata()
                with zipfile.ZipFile(file_names, "r") as zf:
                    print("Asserting backup is in the file")
                    # In this test there should only be the backed up file because the new modified metadata file gets
                    # appended later, after the backup flow is run.
                    self.assertTrue("Old_ComicInfo.xml.bak" in zf.namelist())

                    print("Making sure the backed up file has content and matches original values:")
                    cinfo = ComicInfo.from_xml(zf.open("Old_ComicInfo.xml.bak").read())
                    self.assertEqual(f"Series-{i}-{self.random_int}", cinfo.series)



if __name__ == '__main__':
    unittest.main()
