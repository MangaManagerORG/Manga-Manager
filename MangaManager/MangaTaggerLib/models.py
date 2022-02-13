from dataclasses import dataclass
from . import ComicInfo


@dataclass()
class LoadedComicInfo:

    path: str
    comicInfoObj: ComicInfo
    originalComicObj: ComicInfo
    """
        This class represents a loaded comicinfo.

        :param comicInfoObj: This is the ComicInfo class object
        """
    def __init__(self, path, comicInfo, original=None):
        self.path = path
        self.comicInfoObj = comicInfo
        if original:
            self.originalComicObj = original
