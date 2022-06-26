import time


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
