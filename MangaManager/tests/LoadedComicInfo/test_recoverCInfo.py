import os
import unittest
import zipfile

from src.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo, COMICINFO_FILE_BACKUP, COMICINFO_FILE

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
TEST_COMIC_INFO_STRING_BACKUP = """
        <ComicInfo>
            <Title>Title backup</Title>
            <AlternateSeries>AlternateSeries</AlternateSeries>
            <Summary>Summary backup</Summary>
            <Notes>Notes</Notes>
            <Writer>Writer backup</Writer>
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
            <Teams>Teams backup</Teams>
            <Locations>Locations</Locations>
            <ScanInformation>ScanInformation</ScanInformation>
            <StoryArc>StoryArc</StoryArc>
            <SeriesGroup>SeriesGroup backup</SeriesGroup>
            <AgeRating>Unknown</AgeRating>
            <CommunityRating>3</CommunityRating>
        </ComicInfo>
        """


class TestZipFile(unittest.TestCase):
    def setUp(self) -> None:
        with zipfile.ZipFile('test.zip', mode='w') as zf:
            zf.writestr(COMICINFO_FILE_BACKUP, TEST_COMIC_INFO_STRING_BACKUP)

    def tearDown(self) -> None:
        os.remove('test.zip')

    def test_backup_content_no_previous_comicinfoxml_only_backup(self):
        # create a test zipfile with a comicinfo.xml file

        lci = LoadedComicInfo("test.zip")
        lci.recover_comicinfo_xml(lci.file_path)

        with zipfile.ZipFile('test.zip', mode='r') as zf:
            backup_content = zf.read(COMICINFO_FILE).decode()
            # verify that the backup content matches the original content
            self.assertEqual(backup_content, TEST_COMIC_INFO_STRING_BACKUP)
            self.assertEqual(1, len(zf.namelist()))

    def test_backup_content(self):
        with zipfile.ZipFile('test.zip', mode='a') as zf:
            zf.writestr(COMICINFO_FILE, TEST_COMIC_INFO_STRING)

        lci = LoadedComicInfo("test.zip")
        lci.recover_comicinfo_xml(lci.file_path)

        with zipfile.ZipFile('test.zip', mode='r') as zf:
            backup_content = zf.read(COMICINFO_FILE).decode()
            # verify that the backup content matches the original content
            self.assertEqual(backup_content, TEST_COMIC_INFO_STRING_BACKUP)
            self.assertEqual(1, len(zf.namelist()))
