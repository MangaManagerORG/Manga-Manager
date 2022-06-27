import time

import requests


def get_elapsed_time(start_time: float) -> str:
    """
    This functions returns a string of how much time has elapsed

    :param start_time: The start time (time.time())
    :return: "{minutes:int} minutes and {seconds:int} seconds"
    """
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


def create_settings():
    return {
        "library_folder_path": None,
        "cover_folder_path": None
    }


def cleanFilename(sourcestring, removestring="%:/,.\\[]<>*?\""):
    """Clean a string by removing selected characters.

    Creates a legal and 'clean' source string from a string by removing some
    clutter and  characters not allowed in filenames.
    A default set is given but the user can override the default string
    changes spaces to underscore _

    Args:
        | sourcestring (string): the string to be cleaned.
        | removestring (string): remove all these characters from the string (optional).

    Returns:
        | (string): A cleaned-up string.

    Raises:
        | No exception is raised.
    """
    # remove the undesireable characters
    new_string = ''.join([c for c in sourcestring if c not in removestring]).replace(" ", "_")
    return new_string


def check_url_isImage(image_url):
    """
    Whether the url provided contains an image based on the headers
    :param image_url:
    :return:
    """
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False
