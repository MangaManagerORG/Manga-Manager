import logging
from tkinter import Label, Frame
from tkinter.ttk import Combobox

from Extensions.Interface import IExtensionApp
from src import settings_class

settings = settings_class.get_setting("main")
covers_folder_path = settings.covers_folder_path
logger = logging.getLogger()


# class UrlNotFound(Exception):
#     """
#     Exception raised when api returns 400 status code
#     """
#
#     def __init__(self, requestUrl):
#         super().__init__(f'Url {requestUrl} not found')
#
#
# def clean_filename(sourcestring, removestring="%:/,.\\[]<>*?\""):
#     """Clean a string by removing selected characters.
#
#     Creates a legal and 'clean' source string from a string by removing some
#     clutter and  characters not allowed in filenames.
#     A default set is given but the user can override the default string
#     changes spaces to underscore _
#
#     Args:
#         | sourcestring (string): the string to be cleaned.
#         | removestring (string): remove all these characters from the string (optional).
#
#     Returns:
#         | (string): A cleaned-up string.
#
#     Raises:
#         | No exception is raised.
#     """
#     # remove the undesireable characters
#     new_string = ''.join([c for c in sourcestring if c not in removestring]).replace(" ", "_")
#     return new_string
#
#
# def check_url_isImage(image_url):
#     """
#     Whether the url provided contains an image based on the headers
#     :param image_url:
#     :return:
#     """
#     image_formats = ("image/png", "image/jpeg", "image/jpg")
#     r = requests.head(image_url)
#     if r.headers["content-type"] in image_formats:
#         return True
#     return False

from src.DynamicLibController.extension_manager import load_extensions
try:
    loaded_extensions = load_extensions(EXTENSIONS_DIR)
except Exception:
    logger.exception("Exception loading the extensions")


class CoverDownloader(IExtensionApp):
    name = "Webp Converter"

    def serve_gui(self):
        if not self.master:
            return Exception("Tried to initialize ui with no master window")

        frame = Frame()
        frame.pack()

        Label(frame, text="Manga identifier").pack()

        Combobox(frame, state="readonly").pack()




    # def download_covers(self, manga_id, force_overwrite=False, test_run=False):
    #     """
    #     Downloads the covers from manga_id from mangadex.
    #     If the cover is already downloaded it won't re-download
    #
    #     :param manga_id: The manga id only.
    #     :param cover_folder: The folder where the series folder will be created.
    #     :param force_overwrite: If existing covers should be re-downloaded and overwritten
    #     :param test_run: Value to make a dry run where it asserts that each cover url is valid
    #     :return:
    #     """
    #
    #     data = {"manga[]": [manga_id], "includes[]": ["manga"], "limit": 50}
    #     # Request the list of covers in the provided manga
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
    #     destination_dirpath = Path(covers_folder_path, clean_filename(
    #         normalized_manga_name))  # The covers get stored in their own series folder inside the covers directory
    #     if not test_run:
    #         destination_dirpath.mkdir(parents=True, exist_ok=True)
    #     total = len(r_json.get("data"))
    #     # Todo: Implement progress bar
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
    #             if (not destination_filepath.exists() or force_overwrite) and not test_run:
    #                 image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
    #                 urllib.request.urlretrieve(image_url, destination_filepath)
    #                 logger.debug(f"Downloaded {destination_filename}")
    #             elif test_run:
    #                 image_url = f"https://mangadex.org/covers/{manga_id}/{cover_filename}"
    #                 print(f"Asserting if valid url: '{image_url}' ")
    #                 return check_url_isImage(image_url)
    #             else:
    #                 logger.info(f"Skipped 'https://mangadex.org/covers/{manga_id}/{cover_filename}' -> Already exists")
    #         except Exception as e:
    #             logger.error(e)
    #     logger.info(f"Files saved to: '{destination_dirpath}'")
