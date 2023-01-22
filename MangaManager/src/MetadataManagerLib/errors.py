class NoMetadataFileFound(Exception):
    """
    Exception raised when not enough data is given to create a Metadata object.
    """
    def __init__(self, cbz_path):
        super().__init__(f"ComicInfo.xml not found inside '{cbz_path}'")


class CorruptedComicInfo(Exception):
    """
    Exception raised when the attempt to recover comicinfo file fails..
    """
    def __init__(self, cbz_path):
        super().__init__(f'Failed to recover ComicInfo.xml data in {cbz_path}')


class CancelComicInfoLoad(Exception):
    """
    Exception raised when the users wants to stop loading comicInfo.
    Triggered when an exception is found.
    """

    def __init__(self):
        super().__init__(f'Loading cancelled')


class CancelComicInfoSave(Exception):
    """
    Exception raised when the users cancels parsing.
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


class NoComicInfoLoaded(Exception):
    """
    Exception raised when the list of LoadedComicInfo is empty.
    """

    def __init__(self, info=None):
        super().__init__(f'No ComicInfo Loaded' + info)
