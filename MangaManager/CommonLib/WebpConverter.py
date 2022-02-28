#!/usr/bin/env python3
import logging
import os
import re
import tempfile
import zipfile
from io import BytesIO

from PIL import Image

logger = logging.getLogger(__name__)


# zipFilePath = f0
# dirname = os.path.dirname(zipFilePath)
# filename = os.path.basename(zipFilePath)
# dirname = os.path.dirname(self.zipFilePath)
# filename = os.path.basename(self.zipFilePath)
# new_zipFilePath = Path(dirname, "REFORMATED_TO_WEBP_" + os.path.basename(self.zipFilePath))

class WebpConverter:
    def __init__(self, cbzFilePathList: list[str], overrideSupportedFormat=(".png", ".jpeg", ".jpg")):
        logger.info(f"Loaded file list: " + "\n".join(cbzFilePathList))
        for cbzFilepath in cbzFilePathList:
            logger.info(f"Loading '{cbzFilepath}")
            self.zipFilePath = cbzFilepath

            tmpfd, self._tmpname = tempfile.mkstemp(dir=os.path.dirname(self.zipFilePath))
            os.close(tmpfd)

            self._supported_formats = overrideSupportedFormat
            logger.info("Processing...")
            self._process()

            os.remove(self.zipFilePath)
            os.rename(self._tmpname, self.zipFilePath)
            logger.info(f"Successfully processed")

    def _process(self):
        with zipfile.ZipFile(self.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(self._tmpname, 'w') as zout:
                for zipped_file in zin.infolist():
                    logger.debug(f"Processing file {zipped_file.filename}")
                    file_format = re.findall(r"(?i)\.[a-z]+$", zipped_file.filename)[0]
                    file_name = zipped_file.filename.replace(file_format, "")
                    if file_format in self._supported_formats:
                        with zin.open(zipped_file) as open_zipped_file:
                            image = Image.open(open_zipped_file)
                            # print(image.size, image.mode, len(image.getdata()))
                            converted_image = BytesIO()
                            image.save(converted_image, format="webp")
                            image.close()
                            zout.writestr(file_name + ".webp", converted_image.getvalue())
                            logger.debug(f"Added {zipped_file.filename} back converted to webp")
                            continue
                    zout.writestr(zipped_file.filename, zin.read(zipped_file.filename))
                    logger.debug(f"Added {zipped_file.filename} back without modifications")


if __name__ == '__main__':
    import sys
    import glob

    logging.getLogger('PIL').setLevel(logging.WARNING)
    formatter = logging.Formatter()

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout), ]
                        # filename='/tmp/myapp.log'
                        )
    logger.info("Starting standalone Converter")

    inputStr = input("Write the path to the zip-compatible files you want to convert its images to webp.")
    if not inputStr:
        print("No files selected")
    filenames = glob.glob(inputStr)
    if not filenames:
        print("No files found")
    app = WebpConverter(filenames)
