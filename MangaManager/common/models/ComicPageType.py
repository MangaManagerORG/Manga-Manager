from enum import Enum


class ComicPageType(str, Enum):
    FRONT_COVER = 'FrontCover'
    INNER_COVER = 'InnerCover'
    ROUNDUP = 'Roundup'
    STORY = 'Story'
    ADVERTISMENT = 'Advertisment'
    EDITORIAL = 'Editorial'
    LETTERS = 'Letters'
    PREVIEW = 'Preview'
    BACK_COVER = 'BackCover'
    OTHER = 'Other'
    DELETED = 'Deleted'

    @classmethod
    def list(cls):  # pragma: no cover
        return list(map(lambda c: c.value, cls))