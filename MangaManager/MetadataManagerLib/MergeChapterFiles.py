import zipfile

if __name__ == '__main__':
    import os.path

    from ComicInfo import ComicInfo
    from cbz_handler import ReadComicInfo
    from models import LoadedComicInfo, OrderedLoadedComicInfo
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


class MergeChapterFiles:
    def __init__(self, loadedComicInfo_list: LoadedComicInfo = None):
        if loadedComicInfo_list is None:
            loadedComicInfo_list = list[OrderedLoadedComicInfo]()
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

        print("stop")

    #
    #         if metadata.get_Number():
    #             loadedComicInfo.parsed_chapter = int(metadata.get_Number())
    #             item.parsed_part = metadata.get_Number().split(".")

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
