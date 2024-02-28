class NoMetadataFileFound(Exception):
    """
    Exception raised when not enough data is given to create a Metadata object.
    """

    def __init__(self, cbz_path):
        super().__init__(f"ComicInfo.xml not found inside '{cbz_path}'")


class MangaNotFoundError(Exception):
    """
    Exception raised when the manga cannot be found in the results from the provided source.
    """
    def __init__(self, source, manga_title):
        super().__init__(f'{source} did not return any results for series name "{manga_title}"'
                         f'This may be due to a difference in manga series titles')


class EditedCinfoNotSet(RuntimeError):
    def __init__(self, message=None):
        super(EditedCinfoNotSet, self).__init__(message)


class CorruptedComicInfo(Exception):
    """
    Exception raised when the attempt to recover comicinfo file fails..
    """

    def __init__(self, cbz_path):
        super().__init__(f'Failed to recover ComicInfo.xml data in {cbz_path}')


class CancelComicInfoLoad(Exception):
    """
    Exception raised when the users want to stop loading comicInfo.
    Triggered when an exception is found.
    """

    def __init__(self):
        super().__init__(f'Loading cancelled')


class CancelComicInfoSave(Exception):
    """
    Exception raised when the users cancel parsing.
    Triggered when the user wants to cancel.
    """

    def __init__(self):
        super().__init__(f'Saving cancelled')


class NoFilesSelected(Exception):
    """
    Exception raised when a method that requires selected files is called and no selected files.
    """

    def __init__(self):
        super().__init__(f'No Files Selected')


class BadZipFile(Exception):
    """
    Exception raise when the file is broken or is not a zip file
    """

    def __init__(self):
        super().__init__(f'File is broken or not a valid zip file')


class NoComicInfoLoaded(Exception):
    """
    Exception raised when the list of LoadedComicInfo is empty.
    """

    def __init__(self, info=""):
        super().__init__(f'No ComicInfo Loaded' + info)


class NoModifiedCinfo(Exception):
    """
    Exception raised when a processing is attempted but there are no loaded_cinfo with it's comicinfo modified
    """

    def __init__(self):
        super().__init__(f'No loaded_cinfo to process')


class FailedBackup(RuntimeError):
    """
    Exception raised when a file fails to create a backup
    """

    def __init__(self):
        super(FailedBackup, self).__init__()

class MissingRarTool(Exception):
    """Exception raised when there is no installed tool"""

    def __init__(self):
        super(MissingRarTool, self).__init__()