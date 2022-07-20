import io
import zipfile

if __name__ == '__main__':
    import os.path

    import ComicInfo
    from cbz_handler import ReadComicInfo
    from models import LoadedComicInfo
    import argparse


    def is_dir_path(path):

        if os.path.isfile(path):
            return path
        else:
            raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
else:
    import os
    from . import ComicInfo
    from .cbz_handler import ReadComicInfo
    from .models import LoadedComicInfo


def _read_metadata(loadedComicInfo) -> ComicInfo.ComicInfo:
    """
    Reads comicinfo without extracting the zip
    """
    archive = zipfile.ZipFile(loadedComicInfo.path, 'r')
    metadata = archive.read('ComicInfo.xml').decode()
    metadata = ReadComicInfo("", metadata).to_ComicInfo()
    archive.close()
    return metadata


def merge_singleList(out_list: list, list_to_append: str) -> list:
    return list(set(out_list + list_to_append.split(",")))


class MergeMetadata:
    def __init__(self, loadedComicInfo_list: list[LoadedComicInfo]):
        # merge_metadata_into_one=False,
        # merge_people=False,
        # merge_tags=False,
        # merge_genres=False,
        # merge_summary=False
        # ):
        """
        :param loadedComicInfo_list: Expects a ordered list of loadedComicInfo
        :param merge_metadata_into_one: If True: All metadata that can be merged will be merged 
        :param merge_people: If True: It will parse each type of people and merge them in the output file
        :param merge_tags: If True: It will parse tags and merge them in the output file 
        :param merge_genres: If True: It will parse genres and merge them in the output file 
        :param merge_summary: Will append each part on each line 
        """

        # TODO("Append multiple Summaries")
        self.output_cInfo = ComicInfo.ComicInfo()
        self.loadedComicInfo_list = loadedComicInfo_list

    def people(self):
        people = {
            "Writer": [],
            "Inker": [],
            "Colorist": [],
            "Letterer": [],
            "CoverArtist": [],
            "Editor": [],
            "Translator": [],
            "Publisher": [],
            "Imprint": [],
            "Characters": [],
            "Teams": [],
            "Locations": []
        }
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            people["Writer"] = merge_singleList(people["Writer"], ComicInfoObject.get_Writer())
            people["Inker"] = merge_singleList(people["Inker"], ComicInfoObject.get_Inker())
            people["Colorist"] = merge_singleList(people["Colorist"], ComicInfoObject.get_Colorist())
            people["Letterer"] = merge_singleList(people["Letterer"], ComicInfoObject.get_Letterer())
            people["CoverArtist"] = merge_singleList(people["CoverArtist"], ComicInfoObject.get_CoverArtist())
            people["Editor"] = merge_singleList(people["Editor"], ComicInfoObject.get_Editor())
            people["Translator"] = merge_singleList(people["Translator"], ComicInfoObject.get_Translator())
            people["Publisher"] = merge_singleList(people["Publisher"], ComicInfoObject.get_Publisher())
            people["Imprint"] = merge_singleList(people["Imprint"], ComicInfoObject.get_Imprint())
            people["Characters"] = merge_singleList(people["Characters"], ComicInfoObject.get_Characters())
            people["Teams"] = merge_singleList(people["Teams"], ComicInfoObject.get_Teams())
            people["Locations"] = merge_singleList(people["Locations"], ComicInfoObject.get_Locations())

        for item in people:
            people[item] = sorted([x.strip(' ') for x in people[item]])
            people[item] = ",".join(people[item])

        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            ComicInfoObject.set_Writer(people["Writer"])
            ComicInfoObject.set_Inker(people["Inker"])
            ComicInfoObject.set_Colorist(people["Colorist"])
            ComicInfoObject.set_Letterer(people["Letterer"])
            ComicInfoObject.set_CoverArtist(people["CoverArtist"])
            ComicInfoObject.set_Editor(people["Editor"])
            ComicInfoObject.set_Translator(people["Translator"])
            ComicInfoObject.set_Publisher(people["Publisher"])
            ComicInfoObject.set_Imprint(people["Imprint"])
            ComicInfoObject.set_Characters(people["Characters"])
            ComicInfoObject.set_Teams(people["Teams"])
            ComicInfoObject.set_Locations(people["Locations"])

            ComicInfoObject = self.output_cInfo
            ComicInfoObject.set_Writer(people["Writer"])
            ComicInfoObject.set_Inker(people["Inker"])
            ComicInfoObject.set_Colorist(people["Colorist"])
            ComicInfoObject.set_Letterer(people["Letterer"])
            ComicInfoObject.set_CoverArtist(people["CoverArtist"])
            ComicInfoObject.set_Editor(people["Editor"])
            ComicInfoObject.set_Translator(people["Translator"])
            ComicInfoObject.set_Publisher(people["Publisher"])
            ComicInfoObject.set_Imprint(people["Imprint"])
            ComicInfoObject.set_Characters(people["Characters"])
            ComicInfoObject.set_Teams(people["Teams"])
            ComicInfoObject.set_Locations(people["Locations"])

    def tags(self):
        parsed_tags = []
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            parsed_tags = merge_singleList(parsed_tags, ComicInfoObject.get_Tags())
        parsed_tags = sorted([x.strip() for x in parsed_tags])
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            ComicInfoObject.set_Tags(",".join(parsed_tags))
        self.output_cInfo.set_Tags(",".join(parsed_tags))

    def genres(self):
        parsed_genres = []
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            parsed_genres = merge_singleList(parsed_genres, ComicInfoObject.get_Genre())
        parsed_genres = sorted([x.strip(' ') for x in parsed_genres])
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            ComicInfoObject.set_Genre(",".join(parsed_genres))
        self.output_cInfo.set_Genre(",".join(parsed_genres))

    def return_one(self):
        """
        Returs one single comicinfo.
        Tags, Genre and people merge must be called before this if desired
        :return:
        """

        new_etters = zip(
            [
                self.output_cInfo.get_Title,
                self.output_cInfo.get_Series,
                self.output_cInfo.get_LocalizedSeries,
                self.output_cInfo.get_SeriesSort,
                self.output_cInfo.get_AlternateSeries,
                self.output_cInfo.get_Summary,
                self.output_cInfo.get_Notes,
                self.output_cInfo.get_Web,
                self.output_cInfo.get_SeriesGroup,
                self.output_cInfo.get_AgeRating,
                self.output_cInfo.get_CommunityRating,
                self.output_cInfo.get_ScanInformation,
                self.output_cInfo.get_StoryArc,
                self.output_cInfo.get_Number,
                self.output_cInfo.get_AlternateNumber,
                self.output_cInfo.get_Count,
                self.output_cInfo.get_AlternateCount,
                self.output_cInfo.get_Volume,
                self.output_cInfo.get_PageCount,
                self.output_cInfo.get_Year,
                self.output_cInfo.get_Month,
                self.output_cInfo.get_Day,
                self.output_cInfo.get_Format,
                self.output_cInfo.get_LanguageISO,
                self.output_cInfo.get_BlackAndWhite,
                self.output_cInfo.get_Manga,
                self.output_cInfo.get_StoryArcNumber
            ],
            [
                self.output_cInfo.set_Title,
                self.output_cInfo.set_Series,
                self.output_cInfo.set_LocalizedSeries,
                self.output_cInfo.set_SeriesSort,
                self.output_cInfo.set_AlternateSeries,
                self.output_cInfo.set_Summary,
                self.output_cInfo.set_Notes,
                self.output_cInfo.set_Genre,
                self.output_cInfo.set_Tags,
                self.output_cInfo.set_Web,
                self.output_cInfo.set_SeriesGroup,
                self.output_cInfo.set_AgeRating,
                self.output_cInfo.set_CommunityRating,
                self.output_cInfo.set_ScanInformation,
                self.output_cInfo.set_StoryArc,
                self.output_cInfo.set_Number,
                self.output_cInfo.set_AlternateNumber,
                self.output_cInfo.set_Count,
                self.output_cInfo.set_AlternateCount,
                self.output_cInfo.set_Volume,
                self.output_cInfo.set_PageCount,
                self.output_cInfo.set_Year,
                self.output_cInfo.set_Month,
                self.output_cInfo.set_Day,
                self.output_cInfo.set_Format,
                self.output_cInfo.set_LanguageISO,
                self.output_cInfo.set_BlackAndWhite,
                self.output_cInfo.set_Manga,
                self.output_cInfo.set_StoryArcNumber]
        )
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            etters = zip(
                [
                    ComicInfoObject.get_Title,
                    ComicInfoObject.get_Series,
                    ComicInfoObject.get_LocalizedSeries,
                    ComicInfoObject.get_SeriesSort,
                    ComicInfoObject.get_AlternateSeries,
                    ComicInfoObject.get_Summary,
                    ComicInfoObject.get_Notes,
                    ComicInfoObject.get_Web,
                    ComicInfoObject.get_SeriesGroup,
                    ComicInfoObject.get_AgeRating,
                    ComicInfoObject.get_CommunityRating,
                    ComicInfoObject.get_ScanInformation,
                    ComicInfoObject.get_StoryArc,
                    ComicInfoObject.get_Number,
                    ComicInfoObject.get_AlternateNumber,
                    ComicInfoObject.get_Count,
                    ComicInfoObject.get_AlternateCount,
                    ComicInfoObject.get_Volume,
                    ComicInfoObject.get_PageCount,
                    ComicInfoObject.get_Year,
                    ComicInfoObject.get_Month,
                    ComicInfoObject.get_Day,
                    ComicInfoObject.get_Format,
                    ComicInfoObject.get_LanguageISO,
                    ComicInfoObject.get_BlackAndWhite,
                    ComicInfoObject.get_Manga,
                    ComicInfoObject.get_StoryArcNumber
                ],
                [
                    ComicInfoObject.set_Title,
                    ComicInfoObject.set_Series,
                    ComicInfoObject.set_LocalizedSeries,
                    ComicInfoObject.set_SeriesSort,
                    ComicInfoObject.set_AlternateSeries,
                    ComicInfoObject.set_Summary,
                    ComicInfoObject.set_Notes,
                    ComicInfoObject.set_Web,
                    ComicInfoObject.set_SeriesGroup,
                    ComicInfoObject.set_AgeRating,
                    ComicInfoObject.set_CommunityRating,
                    ComicInfoObject.set_ScanInformation,
                    ComicInfoObject.set_StoryArc,
                    ComicInfoObject.set_Number,
                    ComicInfoObject.set_AlternateNumber,
                    ComicInfoObject.set_Count,
                    ComicInfoObject.set_AlternateCount,
                    ComicInfoObject.set_Volume,
                    ComicInfoObject.set_PageCount,
                    ComicInfoObject.set_Year,
                    ComicInfoObject.set_Month,
                    ComicInfoObject.set_Day,
                    ComicInfoObject.set_Format,
                    ComicInfoObject.set_LanguageISO,
                    ComicInfoObject.set_BlackAndWhite,
                    ComicInfoObject.set_Manga,
                    ComicInfoObject.set_StoryArcNumber]
            )
            for item in new_etters:
                old_etters = next(etters)
                new_getter = item[0]
                new_setter = item[1]
                old_getter = old_etters[0]
                old_setter = old_etters[1]

                if not new_getter():
                    if old_getter():
                        new_setter(old_getter())

        export_io = io.StringIO()
        self.output_cInfo.export(export_io, 0)
        # output_cInfo.set_Number()
        print(export_io.getvalue())
        return self.output_cInfo

    def ageRating(self):
        highest_value = 0
        highest_enum = None
        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            if ComicInfo.AgeRating.get_max_value(ComicInfoObject.get_AgeRating()) >= highest_value:
                highest_value = ComicInfo.AgeRating.get_max_value(ComicInfoObject.get_AgeRating())
                highest_enum = ComicInfoObject.get_AgeRating()

        for loadedComicInfo in self.loadedComicInfo_list:
            ComicInfoObject = loadedComicInfo.comicInfoObj
            ComicInfoObject.set_AgeRating(highest_enum)
        self.output_cInfo.set_AgeRating(highest_enum)

    def merge_all_into_one(self):
        self.people()
        self.tags()
        self.genres()
        self.ageRating()

    def extract(self) -> list[LoadedComicInfo]:
        return self.loadedComicInfo_list


class MergeChapterFiles:
    """
    Very inefficient code overall should be rewritten at some point
    """

    def __init__(self, loadedComicInfo_list: LoadedComicInfo = None):
        if loadedComicInfo_list is None:
            loadedComicInfo_list = list[LoadedComicInfo]()
        ...
        self._initialized_UI = False
        self.loadedComicInfo_list = loadedComicInfo_list

    def parse_chapters(self):
        for loadedComicInfo in self.loadedComicInfo_list:
            if loadedComicInfo.comicInfoObj is None:
                loadedComicInfo.comicInfoObj = _read_metadata(loadedComicInfo)
                metadata = loadedComicInfo.comicInfoObj
                loadedComicInfo.chapter = metadata.get_Number()
                loadedComicInfo.parsed_chapter = int(float(metadata.get_Number()))
                loadedComicInfo.parsed_part = float(metadata.get_Number())

    def order_chapters(self):
        self.loadedComicInfo_list = sorted(self.loadedComicInfo_list, key=lambda loadedInfo: loadedInfo.chapter,
                                           reverse=False)

    def group_chapters(self):
        self.grouped_chapters = dict()

        for loadedInfo in self.loadedComicInfo_list:
            if loadedInfo.parsed_chapter is None:
                raise Exception("No parsed chapter")
            if not self.grouped_chapters.get(loadedInfo.parsed_chapter):
                self.grouped_chapters[loadedInfo.parsed_chapter] = []
            self.grouped_chapters[loadedInfo.parsed_chapter].append(loadedInfo)


if __name__ == '__main__':
    cinfo_1 = ComicInfo.ComicInfo()
    cinfo_1.set_Tags("Tag_1, Tag_2")
    cinfo_1.set_Series("Serie_1")
    cinfo_1.set_Writer("Writer_1")
    cinfo_2 = ComicInfo.ComicInfo()
    cinfo_2.set_Series("Serie_2")
    cinfo_2.set_Tags("Tag_1, Tag_3, Tag_4")
    cinfo_2.set_Writer("Writer_2")
    test = MergeMetadata([LoadedComicInfo("", cinfo_1), LoadedComicInfo("", cinfo_2)])
    test.tags()
    test.merge_all_into_one()
    test.return_one()
