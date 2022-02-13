import unittest
import zipfile
from CoverManagerLib.models import *
from CoverManagerLib.cbz_handler import *


class CbzControllerTester(unittest.TestCase):
    def test_append(self):
        path_23 = r"I:\Mi unidad\Programacion\Python\MangaManagerProject\tests\Sample CBZ Chapter 23.cbz"
        path_24 = r"I:\Mi unidad\Programacion\Python\ASCRIPT_MANGA_ZIPPER\tests\Sample CBZ Chapter 24.cbz"

        sample_cover = r"F:\Anime_Series_Pelis\MANGA\tmp\SAMPLE_COVER.jpg"
        test_path = path_23
        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count = len(zin.namelist())
            # print("\n".join(zin.namelist()))
        values_to_process = cover_process_item_info(
            cbz_file=test_path,
            cover_path=sample_cover,
            cover_format="jpg"

        )
        SetCover(values_to_process)

        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count2 = len(zin.namelist())
            # print("\n\n\nNEW RESULT\n ")
            # print("\n".join(zin.namelist()))

        # if item_count == item_count2:
        #     print(f"####\n{item_count}\nSAME CONTENT\n{item_count2}\n####")
        print(f"Asserting {item_count} vs {item_count2}, delta 1")
        self.assertAlmostEqual(item_count, item_count2, delta=1)  # add assertion here

    def test_overwrite(self):
        path_23 = r"I:\Mi unidad\Programacion\Python\MangaManagerProject\tests\Sample CBZ Chapter 23.cbz"
        path_24 = r"I:\Mi unidad\Programacion\Python\ASCRIPT_MANGA_ZIPPER\tests\Sample CBZ Chapter 24.cbz"

        sample_cover = r"F:\Anime_Series_Pelis\MANGA\tmp\SAMPLE_COVER.jpg"
        test_path = path_23
        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count = len(zin.namelist())
            # print("\n".join(zin.namelist()))
        values_to_process = cover_process_item_info(
            cbz_file=test_path,
            cover_path=sample_cover,
            cover_format="jpg",
            coverOverwrite=True

        )
        SetCover(values_to_process)

        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count2 = len(zin.namelist())
            # print("\n\n\nNEW RESULT\n ")
            # print("\n".join(zin.namelist()))

        # if item_count == item_count2:
        #     print(f"####\n{item_count}\nSAME CONTENT\n{item_count2}\n####")
        print(f"Asserting {item_count} vs {item_count2}, delta 1")
        self.assertAlmostEqual(item_count, item_count2, delta=1)  # add assertion here

    def test_delete(self):
        path_23 = r"I:\Mi unidad\Programacion\Python\MangaManagerProject\tests\Sample CBZ Chapter 23.cbz"
        path_24 = r"I:\Mi unidad\Programacion\Python\ASCRIPT_MANGA_ZIPPER\tests\Sample CBZ Chapter 24.cbz"

        sample_cover = r"F:\Anime_Series_Pelis\MANGA\tmp\SAMPLE_COVER.jpg"
        test_path = path_23
        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count = len(zin.namelist())
            # print("\n".join(zin.namelist()))
        values_to_process = cover_process_item_info(
            cbz_file=test_path,
            cover_path=sample_cover,
            cover_format="jpg",
            coverDelete=True


        )
        SetCover(values_to_process)

        with zipfile.ZipFile(test_path, 'r') as zin:
            item_count2 = len(zin.namelist())
            # print("\n\n\nNEW RESULT\n ")
            # print("\n".join(zin.namelist()))

        # if item_count == item_count2:
        #     print(f"####\n{item_count}\nSAME CONTENT\n{item_count2}\n####")
        print(f"Asserting {item_count} vs {item_count2}")
        self.assertAlmostEqual(item_count, item_count2,delta=1)  # add assertion here



if __name__ == '__main__':
    unittest.main()
