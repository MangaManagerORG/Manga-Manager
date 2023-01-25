import logging
import urllib
from pathlib import Path

import requests

from Extensions.CoverDownloader.CoverDownloader import covers_folder_path
from src.Common.utils import clean_filename
from src.DynamicLibController.models.CoverSourceInterface import ICoverSource, Cover

logger = logging.getLogger()




class MangaDex(ICoverSource):
    name = "MangaDex"

    @staticmethod
    def parse_identifier(identifier) -> str:
        ...

    @classmethod
    def get_covers(cls, identifier: str) -> list[Cover]:
        """
        Downloads the covers from manga_id from mangadex.
        If the cover is already downloaded it won't re-download

        :param identifier: The manga identifier only.
        """

        manga_id = cls.parse_identifier(identifier)



        data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit": 50}
        # Request the list of covers in the provided manga
        r = requests.get(f"https://api.mangadex.org/cover", params=data)

        if r.status_code == 400:
            logger.error("MangaDex api returned 400 for ")
            raise Exception("status code 400")

        r_json = r.json()
        cover_attributes = r_json.get("data")[0].get("relationships")[0].get("attributes")

        ja_title = list(filter(lambda p: p.get("ja-ro"),
                               cover_attributes.get("altTitles")))
        if ja_title:
            ja_title = ja_title[0].get("ja-ro")

        normalized_manga_name = (ja_title or cover_attributes.get("title").get("en"))

        destination_dirpath = Path(covers_folder_path, clean_filename(
            normalized_manga_name))  # The covers get stored in their own series folder inside the covers directory
        total = len(r_json.get("data"))
        # Todo: Implement progress bar
        for i, cover_data in enumerate(r_json.get("data")):
            try:

                cover_filename = cover_data.get("attributes").get("fileName")
                filename, file_extension = os.path.splitext(cover_filename)

                cover_volume = cover_data.get("attributes").get("volume")
                cover_loc = cover_data.get("attributes").get("locale")

                destination_filename = f"Cover_Vol.{str(cover_volume).zfill(2)}_{cover_loc}{file_extension}"
                destination_filepath = Path(destination_dirpath, destination_filename)
                if (not destination_filepath.exists() or force_overwrite) and not test_run:
                    image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
                    urllib.request.urlretrieve(image_url, destination_filepath)
                    logger.debug(f"Downloaded {destination_filename}")
                elif test_run:
                    image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
                    print(f"Asserting if valid url: '{image_url}' ")
                    return check_url_isImage(image_url)
                else:
                    logger.info(f"Skipped 'https://mangadex.org/covers/{manga_id}/{cover_filename}' -> Already exists")
            except Exception as e:
                logger.error(e)
        logger.info(f"Files saved to: '{destination_dirpath}'")

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

