from enum import Enum


class YesNo(str, Enum):
    UNKNOWN = 'Unknown'
    NO = 'No'
    YES = 'Yes'

    @classmethod
    def list(cls):  # pragma: no cover
        return list(map(lambda c: c.value, cls))