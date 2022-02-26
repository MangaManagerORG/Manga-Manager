class NoMetadataFileFound(Exception):
    """
    Exception raised when not enough data is given to create a Metadata object.
    """

    def __init__(self, cbz_path):
        super().__init__(f'ComicInfo.xml not found inside {cbz_path}')


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

