import logging
import os
import re
import tempfile
import time
import zipfile
from io import BytesIO

from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import ProgressBar
from PIL import Image


def _getNewWebpFormatName(currentName: str) -> str:
    filename, file_format = os.path.splitext(currentName)
    if filename.endswith("."):
        filename = filename.strip(".")
    return filename + ".webp"


def _convertToWebp(open_zipped_file) -> bytes:
    # TODO: Bulletproof image passed not image
    image = Image.open(open_zipped_file)
    # print(image.size, image.mode, len(image.getdata()))
    converted_image = BytesIO()

    image.save(converted_image, format="webp")
    image.close()
    return converted_image.getvalue()

def get_file_format(path) -> tuple[str,str]:
    """

    :param path:
    :return:
    """
    return os.path.splitext(path)


FILE_FORMAT = re.compile(r"(?i)\.[a-z]+$")
class WebpConverterLib:
    _log = None
    _pathList: list[str]
    supported_formats = (".png", ".jpeg", ".jpg")

    def process(self):
        print(self._pathList)
        with patch_stdout():
            with ProgressBar() as pb:
                for file_path in pb(self._pathList, total=len(self._pathList)):
                    self._log.debug(f"Processing '{file_path}'")

                    tmpfd, self._tmpname = tempfile.mkstemp(dir=os.path.dirname(file_path))
                    os.close(tmpfd)
                    try:
                        with zipfile.ZipFile(file_path, 'r') as zin:
                            with zipfile.ZipFile(self._tmpname, 'w') as zout:
                                for zipped_image in zin.infolist():
                                    self._log.debug(f"processing '{zipped_image.filename}'")
                                    file_format = get_file_format(zipped_image.filename)
                                    if file_format:
                                        file_format = file_format[0]
                                    else:  # File doesn't have an extension, it is a folder. skip it
                                        zout.writestr(zipped_image.filename, zin.read(zipped_image.filename))
                                        self._log.debug(
                                            f"Added '{zipped_image.filename}' to new tempfile. File was not processed")
                                        continue

                                    file_name = zipped_image.filename.replace(file_format, "")
                                    if file_format in self.supported_formats:
                                        with zin.open(zipped_image) as open_zipped_file:
                                            zout.writestr(file_name + ".webp", _convertToWebp(open_zipped_file))
                                            self._log.debug(
                                                f"Added converted to webp file '{zipped_image.filename}' to new file")
                                            continue

                                    zout.writestr(zipped_image.filename, zin.read(zipped_image.filename))
                                    self._log.debug(
                                        f"Added '{zipped_image.filename}' to new tempfile. File was not processed")
                    except zipfile.BadZipfile as e:
                        self._log.exception(f"Error processing '{file_path}': {str(e)}")
                        os.remove(self._tmpname)
                        continue
                self._log.info("Completed processing for all selected files")




