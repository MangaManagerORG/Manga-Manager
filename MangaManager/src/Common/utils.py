import logging
import os
import re
import subprocess
import sys
import time
import urllib.request
from io import BytesIO
from pathlib import Path
from typing import IO

from PIL import Image

from src.Common.naturalsorter import natsort_key_with_path_support

# Patterns for picking cover
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp')
covers_patterns = ['^!*0+.[a-z]+$', '.*cover.*.[a-z]+$']
COVER_PATTERN = re.compile(f"(?i)({'|'.join(covers_patterns)})")
cover_r3_alt = '^!*0+1\\.[a-z]+$'
ALT_COVER_PATTERN = re.compile(f"(?i)({'|'.join([cover_r3_alt])})")
IS_IMAGE_PATTERN = re.compile(rf"(?i).*.(?:{'|'.join(IMAGE_EXTENSIONS)})$")

logger = logging.getLogger()


def obtain_cover_filename(file_list) -> (str, str):
    """
    Helper function to find a cover file based on a list of filenames
    :param file_list:
    :return:
    """
    list_image_files = [filename for filename in file_list if IS_IMAGE_PATTERN.findall(filename)]
    latest_cover = sorted(list_image_files, key=natsort_key_with_path_support, reverse=True)
    if latest_cover:
        latest_cover = latest_cover[0]
    else:
        latest_cover = None
    # Cover stuff
    possible_covers = [filename for filename in file_list
                       if IS_IMAGE_PATTERN.findall(filename) and COVER_PATTERN.findall(filename)]
    if possible_covers:
        cover = possible_covers[0]
        return cover, latest_cover
    # Try to get 0001
    possible_covers = [filename for filename in file_list if ALT_COVER_PATTERN.findall(filename)]
    if possible_covers:
        cover = possible_covers[0]
        return cover, latest_cover
    # Resource back to first filename available that is a cover
    # list_image_files = (filename for filename in file_list if IS_IMAGE_PATTERN.findall(filename))
    cover = sorted(list_image_files, key=natsort_key_with_path_support, reverse=False)
    if cover:
        cover = cover[0]
        return cover, latest_cover


webp_supported_formats = (".png", ".jpeg", ".jpg")


def getNewWebpFormatName(currentName: str) -> str:
    filename, file_format = os.path.splitext(currentName)
    if filename.endswith("."):
        filename = filename.strip(".")
    return filename + ".webp"


def convertToWebp(image_bytes_to_convert: IO[bytes]) -> bytes:
    """
    Converts the provided image to webp and returns the converted image bytes
    :param image_bytes_to_convert: The image that has to be converted
    :return:
    """
    # TODO: Bulletproof image passed not image
    image = Image.open(image_bytes_to_convert).convert()
    # print(image.size, image.mode, len(image.getdata()))
    converted_image = BytesIO()

    image.save(converted_image, format="webp")
    image.close()
    return converted_image.getvalue()


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }

    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


class ShowPathTreeAsDict:
    """Builds a tree like structure out of a list of paths"""

    def __init__(self, base_path, paths: list):

        new_path_dict = {"subfolders": [],
                         "files": [],
                         "current": Path(base_path)}
        self.new_path_dict = new_path_dict
        for path in paths:
            self._recurse(new_path_dict, Path(path).parts)
        ...

    def _recurse(self, parent_dic: dict, breaked_subpath):

        if len(breaked_subpath) == 0:
            return
        if len(breaked_subpath) == 1:
            # parent_dic[breaked_subpath[0]] = None
            parent_dic["files"].append(breaked_subpath[0])
            self.on_file(parent_dic, breaked_subpath[0])
            return

        key, *new_chain = breaked_subpath
        if key == "\\":
            key = "root"
        if key not in parent_dic:
            parent_dic[key] = {"subfolders": [], "files": [], "current": Path(parent_dic.get("current"), key)}
            parent_dic["subfolders"].append(key)
            # parent_dic["current"] = Path(parent_dic.get("current"),key)
            self.on_subfolder(parent_dic, key)
        self._recurse(parent_dic[key], new_chain)
        return

    def get(self):
        return self.new_path_dict

    def on_file(self, parent_dict: dict, breaked_subpath):
        ...

    def on_subfolder(self, parent_dict: dict, subfolder):
        ...


def get_elapsed_time(start_time: float) -> str:
    """
    This functions returns a string of how much time has elapsed

    :param start_time: The start time (time.time())
    :return: "{minutes:int} minutes and {seconds:int} seconds"
    """
    if start_time == -1:
        return 0
    current_time = time.time()
    seconds = current_time - start_time
    minutes, seconds = divmod(seconds, 60)

    return f"{int(round(minutes, 0))} minutes and {int(round(seconds, 0))} seconds"


def get_estimated_time(start_time: float, processed_files: int, total_files: int) -> str:
    """
    This functions returns a statistic of how much time is left to finish processing. (Uses elapsed time per file)

    :param start_time: The start time (time.time())
    :param processed_files: Number of files that have already been processed
    :param total_files: Total number of files to be processed
    :return: "{minutes:int} minutes and {seconds:int} seconds"
    """
    if start_time == -1:
        return 0
    try:
        current_time = time.time()
        elapsed_time = current_time - start_time

        time_perFile = elapsed_time / processed_files

        estimated_time = time_perFile * (total_files - processed_files)

        # seconds = current_time - start_time
        minutes, seconds = divmod(estimated_time, 60)
        return f"{int(round(minutes, 0))} minutes and {int(round(seconds, 0))} seconds"
    except ZeroDivisionError:
        return f"{int(round(0, 0))} minutes and {int(round(0, 0))} seconds"


def open_folder(folder_path, selected_file: str = None):
    try:
        if sys.platform == 'darwin':
            subprocess.check_call(['open', '--', folder_path])
        elif sys.platform == 'linux2':
            subprocess.check_call(['xdg-open', '--', folder_path])
        elif sys.platform == 'win32':
            if selected_file:
                subprocess.Popen(f'explorer /select, "{os.path.abspath(selected_file)}"',shell=True)
            else:
                subprocess.Popen(f'explorer "{os.path.abspath(folder_path)}"',shell=True)
        else:
            logger.error(f"Couldn't detect platform. Can't open settings_class folder. Please navigate to {folder_path}")
            return
    except Exception:
        logger.exception(f"Exception opening '{folder_path}' folder")

def get_language_iso_list():
    with urllib.request.urlopen(
            'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry.txt') as response:
        registry = response.read().decode('utf-8')

    # Split the registry into lines
    lines = registry.split('\n')

    # Initialize a list to store the language tags
    tags = []

    # Iterate over the lines
    for line in lines:
        # Check if the line starts with 'Language:'
        if line.startswith('Language:'):
            # Split the line into fields
            fields = line.split('\t')
            # Get the language tag from the second field
            tag = fields[1]
            # Add the tag to the list
            tags.append(tag)

    # Print the list of language tags
    print(tags)