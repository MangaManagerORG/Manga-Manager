import logging
from dataclasses import dataclass
from tkinter import Text, INSERT

from . import ComicInfo

logger = logging.getLogger(__name__)


@dataclass()
class LoadedComicInfo:
    path: str
    comicInfoObj: ComicInfo
    originalComicObj: ComicInfo = None


    def __init__(self, path, comicInfo, original=None):
        self.path = path
        self.comicInfoObj = comicInfo
        if original:
            self.originalComicObj = original


class LongText:
    linked_text_field: Text = None
    name: str
    _value: str = ""
    def __init__(self, name=None):
        if name:
            self.name = name
    def set(self, value: str):
        if not self.linked_text_field:  # If its not defined then UI is not being use. Store value in class variable.
            self._value = value
            return self._value
        self.linked_text_field.insert(INSERT, value)

    def get(self):
        if not self.linked_text_field:  # If its not defined then UI is not being use. Store value in class variable.
            return self._value

        return self.linked_text_field.get(index1="1.0", index2='end-1c')


    def __str__(self):
        return self.name
