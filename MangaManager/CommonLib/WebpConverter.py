#!/usr/bin/env python3
import logging
import os
import re
import tempfile
import zipfile
from io import BytesIO
from typing import IO

from PIL import Image

logger = logging.getLogger(__name__)


class WebpConverter:
    def __init__(self, cbzFilePathList: list[str], overrideSupportedFormat=(".png", ".jpeg", ".jpg")):
        logger.info(f"Loaded file list: \n" + "\n".join(cbzFilePathList))
        l = len(cbzFilePathList)
        printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
        for i, cbzFilepath in enumerate(cbzFilePathList):
            # print(i)
            # print(cbzFilepath)
            # cbzFilepath in cbzFilePathList:
            logger.info(f"Processing '{cbzFilepath}'")
            self.zipFilePath = cbzFilepath

            tmpfd, self._tmpname = tempfile.mkstemp(dir=os.path.dirname(self.zipFilePath))
            os.close(tmpfd)

            self._supported_formats = overrideSupportedFormat
            # logger.info("Processing...")
            try:
                self._process()

                os.remove(self.zipFilePath)
                os.rename(self._tmpname, self.zipFilePath)
                logger.info(f"Done")
                # time.sleep(2)
                print(" " * int(66 + len(os.path.basename(cbzFilePathList[i]))), end="\r")
                print(f"Processed '{os.path.basename(cbzFilePathList[i])}'")
            except zipfile.BadZipfile as e:

                print("   " * int(61 + len(os.path.basename(cbzFilePathList[i]))), end="\r")
                print(f"Error. Not processed '{os.path.basename(cbzFilePathList[i])}'")
                logger.error(f"Error processing '{cbzFilepath}': {str(e)}", exc_info=True)
                os.remove(self._tmpname)
            printProgressBar(i + 1, l, prefix=f"Progress:", suffix='Complete', length=50)
        logger.info("Completed processing for all selected files")
    def _process(self):
        with zipfile.ZipFile(self.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(self._tmpname, 'w') as zout:
                for zipped_file in zin.infolist():
                    # logger.debug(f"Processing file {zipped_file.filename}")
                    file_format = re.findall(r"(?i)\.[a-z]+$", zipped_file.filename)
                    if file_format:
                        file_format = file_format[0]
                    else:  # File doesn't have an extension, it is a folder. skip it
                        zout.writestr(zipped_file.filename, zin.read(zipped_file.filename))
                        logger.debug(f"Added '{zipped_file.filename}' to new tempfile. File was not processed")
                        continue
                    file_name = zipped_file.filename.replace(file_format, "")
                    if file_format in self._supported_formats:
                        with zin.open(zipped_file) as open_zipped_file:
                            zout.writestr(file_name + ".webp", convert(open_zipped_file))
                            logger.debug(f"Converted '{zipped_file.filename}' to webp")
                            # logger.debug(f"Added '{zipped_file.filename}' to new tempfile")
                            continue
                    zout.writestr(zipped_file.filename, zin.read(zipped_file.filename))
                    logger.debug(f"Added '{zipped_file.filename}' to new tempfile. File was not processed")


# CLI ProgressBar


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def convert(open_zipped_file: IO[bytes]) -> bytes:
    image = Image.open(open_zipped_file)
    # print(image.size, image.mode, len(image.getdata()))
    converted_image = BytesIO()
    image.save(converted_image, format="webp")
    image.close()
    return converted_image.getvalue()


if __name__ == '__main__':
    import pathlib
    from logging.handlers import RotatingFileHandler
    import glob

    PROJECT_PATH = pathlib.Path(__file__).parent
    rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/WebpConverter.log", maxBytes=1025760,
                                                backupCount=1)

    logging.getLogger('PIL').setLevel(logging.WARNING)
    # formatter = logging.Formatter()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - WebpConverter - %(levelname)s - %(message)s',
                        handlers=[rotating_file_handler, ]
                        # filename='/tmp/myapp.log'
                        )
    logger.info("Starting standalone Converter")

    inputStr = input("Write the path to the zip-compatible files you want to convert its images to webp.")
    if not inputStr:
        print("No files selected")
        exit()
    filenames = glob.glob(inputStr)
    if not filenames:
        print("No files found")
        exit()
    app = WebpConverter(filenames)
