import unittest

from common.models import ComicInfo
from src.DynamicLibController.models.IMetadataSource import IMetadataSource


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

        IMetadataSource.update_people_from_mapping(data["authors"], people_mapping, comicinfo,
                                   lambda item: item["name"],
                                   lambda item: item["role"])

        self.assertEqual("Author 1", comicinfo.writer)
        self.assertEqual("Artist 1", comicinfo.penciller)
        self.assertEqual("Artist 1", comicinfo.inker)


if __name__ == '__main__':
    unittest.main()
