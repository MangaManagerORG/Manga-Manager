import zipfile
from operator import attrgetter

if __name__ == '__main__':
    import os.path

    import ComicInfo
    from cbz_handler import ReadComicInfo, MergeChapter
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
    from .cbz_handler import ReadComicInfo, MergeChapter
    from .models import LoadedComicInfo


def _get_getters(ComicInfoObject: ComicInfo.ComicInfo):
    """



    :param ComicInfoObject:
    :return:
    """
    return [
        (ComicInfoObject.get_Title, ComicInfoObject.set_Title),
        (ComicInfoObject.get_Series, ComicInfoObject.set_Series),
        (ComicInfoObject.get_LocalizedSeries, ComicInfoObject.set_LocalizedSeries),
        (ComicInfoObject.get_SeriesSort, ComicInfoObject.set_SeriesSort),
        (ComicInfoObject.get_AlternateSeries, ComicInfoObject.set_AlternateSeries),
        (ComicInfoObject.get_Notes, ComicInfoObject.set_Notes),
        (ComicInfoObject.get_Web, ComicInfoObject.set_Web),
        (ComicInfoObject.get_SeriesGroup, ComicInfoObject.set_SeriesGroup),
        (ComicInfoObject.get_CommunityRating, ComicInfoObject.set_CommunityRating),
        (ComicInfoObject.get_ScanInformation, ComicInfoObject.set_ScanInformation),
        (ComicInfoObject.get_StoryArc, ComicInfoObject.set_StoryArc),
        (ComicInfoObject.get_AlternateNumber, ComicInfoObject.set_AlternateNumber),
        (ComicInfoObject.get_Format, ComicInfoObject.set_Format),
        (ComicInfoObject.get_LanguageISO, ComicInfoObject.set_LanguageISO),
        (ComicInfoObject.get_StoryArcNumber, ComicInfoObject.set_StoryArcNumber),
        (ComicInfoObject.get_Summary, ComicInfoObject.set_Summary)
    ]


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
        """
        Every loadedCinfo must be from the first the same chapter. S
            (1.2, 1.3, 1.4) is good, (1.2, 2.3, 3.4) is not.
        :param loadedComicInfo_list: Expects an ordered list of loadedComicInfo from the same chapter
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

    def _other_fields(self):
        """(If the first file has the tag filled, thats the one will be in the output).
        File ch_1 has series: 'Serie_1'
        File ch_2 has series: 'Serie_2'
        Per sorting, file chapter 1 value will be output. -> series will be 'Serie_1'

Merges the following tags:
    Title, 
    Series, Done
    get_LocalizedSeries,
    SeriesSort,
    get_AlternateSeries,
    Notes,
    Web,
    SeriesGroup,
    CommunityRating,
    ScanInformation,
    StoryArc,
    AlternateNumber,
    Format,
    LanguageISO,
    StoryArcNumberm,
    Volume,
    Number,
    Summary

        """
        new_etters = _get_getters(self.output_cInfo)
        min_year = min(list((loadedCinfo.comicInfoObj.Year for loadedCinfo in self.loadedComicInfo_list if
                             loadedCinfo.comicInfoObj.Year not in (0, -1))), default=-1)
        max_count = max(self.loadedComicInfo_list, key=attrgetter('comicInfoObj.Count'))
        if max_count:
            max_count = max_count.comicInfoObj.get_Count()
        else:
            max_count = -1

        for loadedComicInfo in self.loadedComicInfo_list:

            loaded_etters = _get_getters(loadedComicInfo.comicInfoObj)
            for item in zip(loaded_etters, new_etters):
                loadedInfo_etters = item[0]
                loadedInfo_get = loadedInfo_etters[0]
                # loadedInfo_set = loadedInfo_etters[1] # NOT used

                output_etters_field = item[1]
                output_field_get = output_etters_field[0]
                output_field_set = output_etters_field[1]

                if not output_field_get():
                    if loadedInfo_get():
                        output_field_set(loadedInfo_get())

            loadedComicInfo.comicInfoObj.set_Number(str(int(float(loadedComicInfo.comicInfoObj.get_Number()))))
            self.output_cInfo.set_Number(int(float(loadedComicInfo.comicInfoObj.get_Number())))

            self.output_cInfo.set_Volume(int(float(loadedComicInfo.comicInfoObj.get_Volume())))

            loadedComicInfo.comicInfoObj.set_Count(max_count)
            self.output_cInfo.set_Count(max_count)

            loadedComicInfo.comicInfoObj.set_Year(min_year)
            self.output_cInfo.set_Year(min_year)
    def sumPageCount(self):
        """
        Sets the output PageCount to be the sum of all PageCount in loadedCinfoList
        :return: [Optional] Returns the sum of PageCount
        """
        total_PageCount = sum(loadedCinfo.comicInfoObj.PageCount for loadedCinfo in self.loadedComicInfo_list)
        self.output_cInfo.set_PageCount(total_PageCount)
        total_AltPageCount = sum(loadedCinfo.comicInfoObj.AlternateCount for loadedCinfo in self.loadedComicInfo_list)
        self.output_cInfo.set_AlternateCount(total_AltPageCount)
        # return total_PageCount

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
        self._other_fields()
        self.sumPageCount()

    def get_merged_cInfo(self):
        return self.output_cInfo

    # def extract_merged(self) -> ComicInfo.ComicInfo:
    #     """
    #     Returs one single comicinfo.
    #     Tags, Genre and people merge must be called before this if desired
    #     :return:
    #     """
    #
    #     # export_io = io.StringIO()
    #     # self.output_cInfo.export(export_io, 0)
    #     # print(export_io.getvalue())
    #     return self.output_cInfo

    def get_merged_loadedCinfo_list(self) -> list[LoadedComicInfo]:
        return self.loadedComicInfo_list


class MergeChapterFilesApp:
    """
    Very inefficient code overall should be rewritten at some point
    """

    def __init__(self, loadedComicInfo_list: list[LoadedComicInfo] = None):
        if loadedComicInfo_list is None:
            loadedComicInfo_list = list[LoadedComicInfo]()
        ...
        self._initialized_UI = False
        self.loadedComicInfo_list = loadedComicInfo_list

        self.merged_metadata: ComicInfo.ComicInfo = None

    def parse_chapters(self):
        for loadedComicInfo in self.loadedComicInfo_list:
            if not loadedComicInfo.comicInfoObj:
                loadedComicInfo.comicInfoObj = _read_metadata(loadedComicInfo)

            metadata = loadedComicInfo.comicInfoObj
            loadedComicInfo.chapter = metadata.get_Number()
            loadedComicInfo.parsed_chapter = int(float(metadata.get_Number()))
            loadedComicInfo.parsed_part = float(metadata.get_Number())

    def order_chapters(self):
        self.loadedComicInfo_list = sorted(self.loadedComicInfo_list, key=attrgetter("comicInfoObj.Number"),
                                           reverse=False)

    def group_chapters(self):
        self.grouped_chapters = dict()

        for loadedInfo in self.loadedComicInfo_list:
            if loadedInfo.parsed_chapter is None:
                raise Exception("No parsed chapter")
            if not self.grouped_chapters.get(loadedInfo.parsed_chapter):
                self.grouped_chapters[loadedInfo.parsed_chapter] = []
            self.grouped_chapters[loadedInfo.parsed_chapter].append(loadedInfo)

    def process(self):
        """

        :return: List with the new filenames. For unit testing cleanup
        """
        new_filenames = []
        for chapter in self.grouped_chapters:
            chapter_loadedCinfo_list = self.grouped_chapters[chapter]
            metadata_merge_app = MergeMetadata(chapter_loadedCinfo_list)
            metadata_merge_app.merge_all_into_one()

            chapter_loadedCinfo_list = metadata_merge_app.get_merged_loadedCinfo_list()
            chapter_loadedInfo_single = metadata_merge_app.get_merged_cInfo()

            new_name = f"{chapter_loadedInfo_single.get_Series()}{(f' v.{str(chapter_loadedInfo_single.get_Volume()).zfill(2)}' if (chapter_loadedInfo_single.get_Volume() != -1) else '')} Ch.{chapter}.cbz"

            created_file = MergeChapter(ordered_loadedComicInfo=chapter_loadedCinfo_list,
                                        output_filename=str(new_name))

            new_filenames.append(created_file)
        return new_filenames
