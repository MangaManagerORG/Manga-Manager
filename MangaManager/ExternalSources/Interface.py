import abc

from src.MetadataManager.comicinfo import ComicInfo


class IMetadataSource(abc.ABC):
    name = None

    @classmethod
    @abc.abstractmethod
    def get_cinfo(cls, series_name) -> ComicInfo:
        ...
