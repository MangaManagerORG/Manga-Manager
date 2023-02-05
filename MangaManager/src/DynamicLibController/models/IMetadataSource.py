import abc
from typing import final

from src.MetadataManager.comicinfo import ComicInfo


class IMetadataSource(abc.ABC):
    name = ''
    """
        A set of settings which will be found in the main settings dialog of Manga Manager and used for the source
    """
    settings = []

    @classmethod
    @abc.abstractmethod
    def get_cinfo(cls, series_name) -> ComicInfo:
        ...

    def save_settings(self):
        """
        When a setting update occurs, this is invoked and internal state should be updated from Settings()
        """
        pass

    @final
    def __init__(self, master, super_=None, **kwargs):
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(
                f"Error initializing the {self.__class__.__name__} Extension. The 'name' attribute must be set in the CoverSource class.")
        # if self.embedded_ui:
        super().__init__(master=master, **kwargs)
        if super_ is not None:
            self._super = super_