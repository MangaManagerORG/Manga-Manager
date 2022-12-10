from abc import ABC, abstractmethod

from src.MetadataManager import comicinfo


class Extension(ABC):
    name: str

    @abstractmethod
    def process(self) -> comicinfo.ComicInfo:
        ...


class ExtensionGUI(ABC):
    @abstractmethod
    def serve_gui(self, parentframe):
        ...
