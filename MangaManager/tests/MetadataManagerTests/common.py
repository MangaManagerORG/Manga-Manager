import unittest
import zipfile

import _tkinter


def create_dummy_files(nfiles):
    test_files_names = []
    for i in range(nfiles):
        out_tmp_zipname = f"random_image_{i}_not_image.ext.cbz"
        test_files_names.append(out_tmp_zipname)
        with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
            zf.writestr("Dummyfile.ext", "Dummy")
    return test_files_names


class TKinterTestCase(unittest.TestCase):
    """These methods are going to be the same for every GUI test,
    so refactored them into a separate class
    """
    root = None

    def setUp(self):
        ...

    def tearDown(self):
        if self.root:
            self.root.destroy()
            self.pump_events()

    def pump_events(self):
        while self.root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
            pass
