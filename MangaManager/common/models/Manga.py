from enum import Enum


class Manga(str, Enum):
    UNKNOWN = 'Unknown'
    NO = 'No'
    YES = 'Yes'
    YES_AND_RIGHT_TO_LEFT = 'YesAndRightToLeft'

    @classmethod
    def list(cls):  # pragma: no cover
        return list(map(lambda c: c.value, cls))
