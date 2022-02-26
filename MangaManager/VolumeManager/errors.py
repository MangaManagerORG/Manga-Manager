class NoFilesSelected(Exception):
    """
    Exception raised when there is no selected files to process
    """

    def __init__(self):
        super().__init__(f'No files selected.')