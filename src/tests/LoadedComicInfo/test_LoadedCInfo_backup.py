import os
import random
import tempfile
import unittest
import zipfile

from ComicInfo import ComicInfo
from MangaManager.Settings import Settings, SettingHeading

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


class LoadedComicInfo_SaveTests(unittest.TestCase):
    """
    The purpose of this Test case is to test the LoadedComicInfo class against simple scenarios where
    it's only the comicinfo.xml file
    """

    s = Settings()

    def setUp(self) -> None:
        print(os.getcwd())
        self.s.set(SettingHeading.Main, "create_backup_comicinfo", False)
        # Make sure there are no test files else delete them:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")
                          or listed.startswith("tmp")]
        for file in leftover_files:
            os.remove(file)
        self.test_files_names = []
        print("\n", self._testMethodName)
        print("Setup:")
        self.random_int = random.random() + random.randint(1, 40)
        for ai in range(1):
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

    # I give up, I can't figure out how to do it and mock settings
    # def test_simple_backup_doesnt_create_when_turned_off(self):
    #     self.s.set(SettingHeading.Main, "create_backup_comicinfo", False)
    #     for i, file_names in enumerate(self.test_files_names):
    #         with self.subTest(f"Backing up individual metadata - {i + 1}/{len(self.test_files_names)}"):
    #             cinfo = LoadedComicInfo(file_names).load_metadata()
    #             cinfo.write_metadata()
    #             with zipfile.ZipFile(file_names, "r") as zf:
    #                 print("Asserting backup is in the file")
    #                 # In this test there should only be the backed up file because the new modified metadata file gets
    #                 # appended later, after the backup flow is run.
    #                 self.assertFalse("Old_ComicInfo.xml.bak" in zf.namelist())





if __name__ == '__main__':
    unittest.main()
