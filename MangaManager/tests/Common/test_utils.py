import unittest

from src.Common.utils import update_people_from_mapping
from src.MetadataManager.comicinfo import ComicInfo


class MyTestCase(unittest.TestCase):
    def test_update_people_from_mapping(self):
        people_mapping = {
            "Author": [
                "Writer"
            ],
            "Artist": [
                "Penciller",
                "Inker",
            ]
        }

        data = {
            "authors": [
                {
                    "name": "Author 1",
                    "role": "Author"
                },
                {
                    "name": "Artist 1",
                    "role": "Artist"
                },
            ]
        }

        comicinfo = ComicInfo()

        update_people_from_mapping(data["authors"], people_mapping, comicinfo,
                                   lambda item: item["name"],
                                   lambda item: item["role"])

        self.assertEqual("Author 1", comicinfo.Writer)
        self.assertEqual("Artist 1", comicinfo.Penciller)
        self.assertEqual("Artist 1", comicinfo.Inker)


if __name__ == '__main__':
    unittest.main()
