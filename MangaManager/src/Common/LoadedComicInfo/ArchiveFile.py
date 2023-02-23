import os
import zipfile

import rarfile


class ArchiveFile:
    """
    A class that provides a unified interface to read and write archive files.
    It automatically chooses between ZipFile and RarFile based on the
    file extension.
    """
    is_cbr = False

    def __init__(self, filename, mode='r', password=None):
        self.filename = filename
        self.mode = mode
        self.password = password
        self.archive = None

        ext = os.path.splitext(filename)[1].lower()
        if ext in ('.cbz', '.zip'):
            self.archive = zipfile.ZipFile(filename, mode)
        elif ext in ('.cbr', '.rar'):
            self.is_cbr = True
            self.archive = rarfile.RarFile(filename, mode)
            if password:
                self.archive.setpassword(password)
        else:
            raise ValueError('Unsupported file type: %s' % ext)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.archive is not None:
            self.archive.close()

    def namelist(self):
        return self.archive.namelist()

    def infolist(self):
        return self.archive.infolist()

    def getinfo(self, name):
        return self.archive.getinfo(name)

    def read(self, name):
        return self.archive.read(name)

    def open(self, name):
        # if self.is_cbr:
        #     return self.archive.read(name)
        return self.archive.open(name)

    def extract(self, member, path=None, password=None):
        if password:
            self.archive.setpassword(password)
        self.archive.extract(member, path)

    def extractall(self, path=None, members=None, password=None):
        if password:
            self.archive.setpassword(password)
        self.archive.extractall(path, members)
