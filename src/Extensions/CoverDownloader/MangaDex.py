import urllib
from pathlib import Path
from typing import Any

import requests

from Extensions.CoverDownloader.exceptions import UrlNotFound


def parse_mangadex_id(value) -> Any | None:
    """
    Accepts a mangadex id or URL
    :param value:
    :return: mangadex managa id
    """

    if "https://mangadex.org/title/" in value:
        return value.replace("https://mangadex.org/title/", "").split("/")[0]
    else:
        return None

#
# def download_covers(self, manga_id, forceOverwrite=False, test_run=False):
#     """
#     Downloads the covers from manga_id from mangadex.
#     If the cover is already downloaded it won't re-download
#
#     :param manga_id: The manga id only.
#     :param cover_folder: The folder where the series folder will be created.
#     :param forceOverwrite: If existing covers should be re-downloaded and overwritten
#     :param test_run: Value to make a dry run where it asserts that each cover url is valid
#     :return:
#     """
#
#     data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit": 50}
#     # Request the list of covers in the prrovided manga
#     r = requests.get(f"https://api.mangadex.org/cover", params=data)
#
#     if r.status_code == 400:
#         raise UrlNotFound(r.url)
#
#     r_json = r.json()
#     cover_attributes = r_json.get("data")[0].get("relationships")[0].get("attributes")
#
#     ja_title = list(filter(lambda p: p.get("ja-ro"),
#                            cover_attributes.get("altTitles")))
#     if ja_title:
#         ja_title = ja_title[0].get("ja-ro")
#
#     normalized_manga_name = (ja_title or cover_attributes.get("title").get("en"))
#
#
#
#
#     destination_dirpath = pathlib.Path(self.settings.get('cover_folder_path'), cleanFilename(
#         normalized_manga_name))  # The covers get stored in their own series folder inside the covers directory
#     if not test_run:
#         destination_dirpath.mkdir(parents=True, exist_ok=True)
#     total = len(r_json.get("data"))
#     self.progressbar = ProgressBar(self._initialized_UI, self._progressbar_frame, total)
#
#     for i, cover_data in enumerate(r_json.get("data")):
#         try:
#
#             cover_filename = cover_data.get("attributes").get("fileName")
#             filename, file_extension = os.path.splitext(cover_filename)
#
#             cover_volume = cover_data.get("attributes").get("volume")
#             cover_loc = cover_data.get("attributes").get("locale")
#
#             destination_filename = f"Cover_Vol.{str(cover_volume).zfill(2)}_{cover_loc}{file_extension}"
#             destination_filepath = Path(destination_dirpath, destination_filename)
#             if (not destination_filepath.exists() or forceOverwrite) and not test_run:
#                 image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
#                 urllib.request.urlretrieve(image_url, destination_filepath)
#                 logger.debug(f"Downloaded {destination_filename}")
#             elif test_run:
#                 image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
#                 print(f"Asserting if valid url: '{image_url}' ")
#                 return check_url_isImage(image_url)
#             else:
#                 logger.info(f"Skipped 'https://mangadex.org/covers/{manga_id}/{cover_filename}' -> Already exists")
#             self.progressbar.increaseCount()
#         except Exception as e:
#             logger.error(e)
#             self.progressbar.increaseError()
#     logger.info(f"Files saved to: '{destination_dirpath}'")
#     print(f"Files saved to: '{destination_dirpath}'")