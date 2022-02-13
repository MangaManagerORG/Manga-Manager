class CoverDoesNotExist(Exception):
    pass


class NoOverwriteSelected(Exception):
    pass


class NoCoverFile(FileNotFoundError):
    """
    Exception raised when cover path is not specified or not found.
    """

    def __init__(self,coverFilePath):
        super().__init__(f'Cover image file path not provided or image not found: {coverFilePath}')

# class NoMetadataFileFound(Exception):
#     """
#     Exception raised when not enough data is given to create a Metadata object.
#     """
#
#     def __init__(self, cbz_path):
#         super().__init__('ComicInfo.xml not found.')
