from abc import ABC, abstractmethod

from src.MangaManager_ThePromidius.MetadataManager import comicinfo


class Extension(ABC):
    name: str

    @abstractmethod
    def process(self) -> comicinfo.ComicInfo:
        ...

    @abstractmethod
    def serve_gui(self, frame):
        ...
