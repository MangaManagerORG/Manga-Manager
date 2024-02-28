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

from .naturalsorter import natsort_key_with_path_support

# Patterns for picking cover
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp')
covers_patterns = ['^!*0+.[a-z]+$', '.*cover.*.[a-z]+$']
COVER_PATTERN = re.compile(f"(?i)({'|'.join(covers_patterns)})")
cover_r3_alt = '^!*0+1\\.[a-z]+$'
ALT_COVER_PATTERN = re.compile(f"(?i)({'|'.join([cover_r3_alt])})")
IS_IMAGE_PATTERN = re.compile(rf"(?i).*.(?:{'|'.join(IMAGE_EXTENSIONS)})$")

logger = logging.getLogger()
from PIL import Image, ImageStat

try:
    from anytree import Node, RenderTree
except ImportError:
    logger.exception("Failed to import anytree. Some cli functionality might break. Make sure all requirements are installed")

def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1) ** is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else:  # character is not a [balanced] bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return (''.join(saved_chars)).strip()

import unicodedata

def normalize_filename(filename):
    # Normalize the filename using the NFC form
    normalized_filename = unicodedata.normalize('NFC', filename)
    # Replace all non-ASCII characters with their ASCII equivalents
    ascii_filename = normalized_filename.encode('ascii', 'ignore').decode('ascii')
    return ascii_filename

def clean_filename(sourcestring, removestring=" %:/,.\\[]<>*?\""):
    """Clean a string by removing selected characters.

    Creates a legal and 'clean' source string from a string by removing some
    clutter and  characters not allowed in filenames.
    A default set is given but the user can override the default string.

    Args:
        | sourcestring (string): the string to be cleaned.
        | removestring (string): remove all these characters from the string (optional).

    Returns:
        | (string): A cleaned-up string.

    Raises:
        | No exception is raised.
    """
    # remove the undesireable characters
    return ''.join([c for c in sourcestring if c not in removestring])


def find_chapter(text):
    r = r"(?i)(?:chapter|ch)(?:\s|\.)?(?:\s|\.)?(\d+)"
    match = re.findall(r, text)
    if match:
        return match[0]
    return match


def fetch_chapter(text):
    r = r"(?i)(?:chapter|ch|#)(?:\s|\.)?(?:\s|\.)?(\d+)"
    return re.findall(r, text)


def fetch_volume(text):
    r = r"(?i)(?:volume|vol|v)(?:\s|\.)?(?:\s|\.)?(\d+)"
    return re.findall(r, text)


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


def get_new_webp_name(currentName: str) -> str:
    filename, file_format = os.path.splitext(currentName)
    if filename.endswith("."):
        filename = filename.strip(".")
    return filename + ".webp"

max_dimensions = (16383, 16383)
def convert_to_webp(image_raw_data: IO[bytes]) -> bytes:
    """
    Converts the provided image to webp and returns the converted image bytes
    :param image_bytes_to_convert: The image that has to be converted
    :return:
    """
    try:
        logger.info("Converting image")
        image = Image.open(image_raw_data)
        # Check if resizing is needed
        is_grayscale = image.mode in ('L', 'LA') or all(
            min(channel) == max(channel) for channel in ImageStat.Stat(image).extrema
        )
        # Choose resampling method based on image content
        if is_grayscale:
            # For grayscale images (e.g., manga pages)
            resample_method = Image.NEAREST  # or Image.BILINEAR
        else:
            # For colored images (e.g., covers)
            resample_method = Image.BICUBIC  # or Image.LANCZOS
        # Check if resizing is needed
        if any(dim > max_dim for dim, max_dim in zip(image.size, max_dimensions)):
            # Resize the image with the chosen resampling method
            image.thumbnail(max_dimensions, resample=resample_method)
        converted_image_data = BytesIO()
        image.save(converted_image_data, format="webp")
        converted_image_data.seek(0)
        return converted_image_data.getvalue()
    except Exception as e:
        logger.error(f"Exception converting image: {e}")
        raise


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
    def display_tree(self) -> int:
        """

        :return: Number of lines printed
        """
        root = Node("Root")
        self._build_tree(root, self.new_path_dict)
        _counter = 0
        for pre, fill, node in RenderTree(root):
            print("%s%s" % (pre, node.name))
            _counter+=1
        return _counter
    def __init__(self,paths: list,  base_path = None):
        if not base_path:
            base_path = os.path.commonprefix(paths)
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
            parent_dic["files"].append(breaked_subpath[0])
            self.on_file(parent_dic, breaked_subpath[0])
            return

        key, *new_chain = breaked_subpath
        if key == "\\":
            key = "root"
        if key not in parent_dic:
            parent_dic[key] = {"subfolders": [], "files": [], "current": Path(parent_dic.get("current"), key)}
            parent_dic["subfolders"].append(key)
            self.on_subfolder(parent_dic, key)
        self._recurse(parent_dic[key], new_chain)

    def get(self):
        return self.new_path_dict

    def on_file(self, parent_dict: dict, breaked_subpath):
        ...

    def on_subfolder(self, parent_dict: dict, subfolder):
        ...

    def _build_tree(self, parent, data):
        for key, value in data.items():
            if key == "subfolders":
                for subfolder in value:
                    subfolder_node = Node(subfolder, parent=parent)
                    self._build_tree(subfolder_node, data[subfolder])
            elif key == "files":
                for file in value:
                    Node(file, parent=parent)


def get_elapsed_time(start_time: float) -> str:
    """
    This functions returns a string of how much time has elapsed

    :param start_time: The start time (time.time())
    :return: "{minutes:int} minutes and {seconds:int} seconds"
    """
    if start_time == -1:
        return ""
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
        return "0"
    try:
        current_time = time.time()
        elapsed_time = current_time - start_time

        time_per_file = elapsed_time / processed_files

        estimated_time = time_per_file * (total_files - processed_files)

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


def extract_folder_and_module(file_path):
    file_name, ext = os.path.splitext(os.path.basename(file_path))
    dir_name = os.path.basename(os.path.dirname(file_path))
    return dir_name, file_name


def match_pyfiles_with_foldername(file_path):
    folder, file_ = extract_folder_and_module(file_path)
    return folder == file_


def parse_bool(value: str) -> bool:
    if isinstance(value,bool):
        return value
    match value.lower():
        case "true" | "1" | 1:
            return True
        case "false" | "0" | 0:
            return False
        case _:
            raise ValueError(f"Invalid boolean string: {value}")

