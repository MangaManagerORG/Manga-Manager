
from dataclasses import dataclass
from . import ComicInfo
from tkinter import Text, INSERT
import logging
logger = logging.getLogger(__name__)

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


class LongEntry:
    linked_text_field: Text
    name: str
    value: str
    def __init__(self, name=None):
        if name:
            self.name = name

    def set(self, value):
        if not self.linked_text_field:
            self.value = value
            return
        self.linked_text_field.insert(INSERT, value)

    def get(self):
         return self.linked_text_field.get(index1="1.0", index2='end-1c')

    def __str__(self):
        return self.name
