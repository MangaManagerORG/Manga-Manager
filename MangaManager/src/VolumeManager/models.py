from dataclasses import dataclass


@dataclass
class ChapterFileNameData:
    """Class to keep title data chapter and anything after chapter to join together after adding vol info Used in renaming"""
    name: str
    chapterinfo: str
    afterchapter: str
    fullpath: str
    volume = int
    complete_new_path:str

    def __init__(self, name: str, chapterinfo: str, afterchapter: str, fullpath: str,
                 volume: int = None, complete_new_name: str = None):
        self.name = name
        self.chapterinfo = chapterinfo
        self.afterchapter = afterchapter
        self.fullpath = fullpath
        self.volume = volume
        self.complete_new_path = complete_new_name

@dataclass
class ProgressBarData:
    done: int = 0
    errors: int = 0
    total: int = 0
    progress_percentage: int = 0