import unittest

from ComicInfo import ComicInfo
from tests.common import is_valid_xml


class ComicInfoTests(unittest.TestCase):
    def test_sample_xml_isvalid(self):
        cinfo = ComicInfo()
        cinfo.series = "SeriesName"
        cinfo.writer = "WriterName"

        self.assertTrue(is_valid_xml(cinfo.to_xml()))
    def test_valid_xml(self):
        TEST_COMIC_INFO_STRING = """<ComicInfo>
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
            <Other>Other field</Other>
        </ComicInfo>
        """
        self.assertTrue(is_valid_xml(TEST_COMIC_INFO_STRING))

if __name__ == '__main__':
    unittest.main()