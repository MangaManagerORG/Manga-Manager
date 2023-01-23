import logging

from src.DynamicLibController.models.CoverSourceInterface import ICoverSource

logger = logging.getLogger()


class MangaDex(ICoverSource):
    name = "MangaDex"

    @classmethod
    def download(cls, identifier: str):
        """
        Downloads the covers from manga_id from mangadex.
        If the cover is already downloaded it won't re-download

        :param identifier: The manga id only.
        """

    @classmethod
    def parse_input(cls, value) -> str:
        """
        Accepts a mangadex id or URL
        :param value:
        :return: mangadex managa id
        """

        if "https://mangadex.org/title/" in value:
            value = value.replace("https://mangadex.org/title/", "").split("/")[0]
        return value

