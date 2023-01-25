import abc
import dataclasses
from typing import final


class ICoverSource(abc.ABC):
    name = None
    @classmethod
    @abc.abstractmethod
    def download(cls, identifier: str):
        ...

    @final
    def __init__(self, master, super_=None, **kwargs):
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(
                f"Error initializing the {self.__class__.__name__} Extension."
                f"The 'name' attribute must be set in the CoverSource class.")
        # if self.embedded_ui:
        super().__init__(master=master, **kwargs)
        if super_ is not None:
            self._super = super_


@dataclasses.dataclass
class Cover:
    series_name: str
    vol: int
    alternative: int
    url: str

    image_bytes: bytes

