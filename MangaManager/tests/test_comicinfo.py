import unittest

from common.models import AgeRating, Manga, YesNo, Formats


class LoadedCInfo_Utils(unittest.TestCase):
    def test_ComicInfo_ToList_methods_work(self):
        classes_to_test_list_implementation = (AgeRating, Manga, YesNo)

        for class_ in classes_to_test_list_implementation:
            with self.subTest(f"Testing {class_} has list method"):
                self.assertTrue(len(class_.list()) > 1)
        with self.subTest("Testing format_list is populated"):
            self.assertTrue(len(Formats) > 1)
