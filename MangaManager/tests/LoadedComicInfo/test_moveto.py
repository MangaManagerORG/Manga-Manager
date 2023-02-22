import unittest

from common.models import ComicInfo
from src.Common.loadedcomicinfo import LoadedComicInfo, CoverActions
from src.Common.utils import obtain_cover_filename
from tests.common import CBZManipulationTests, create_test_cbz

class MoveToTemplate(unittest.TestCase):
    def test_template(self):
        cinfo = ComicInfo()
        cinfo.volume = 11
        cinfo.number = 22
        cinfo.publisher = "Publisher33"
        cinfo.series = "Series44"
        cinfo.title = "Title55"
        filename = "filename66.cbz"
        a = LoadedComicInfo(None,cinfo,False)
        a.file_name = filename

        self.assertEqual("Series44 - Publisher33",a.get_template_filename("{series} - {publisher}"))
        self.assertEqual("Series44 - Vol.11 Ch.22 - Title55", a.get_template_filename("{series} - Vol.{volume} Ch.{chapter} - {title}"))

        self.assertIsNone(a.get_template_filename("this {key_here} does not exist"))