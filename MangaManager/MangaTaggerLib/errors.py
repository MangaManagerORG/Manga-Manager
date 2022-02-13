class NoMetadataFileFound(Exception):
    """
    Exception raised when not enough data is given to create a Metadata object.
    """

    def __init__(self, cbz_path):
        super().__init__(f'ComicInfo.xml not found inside {cbz_path}')
