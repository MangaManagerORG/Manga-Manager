import random
import re
import unittest

from PIL import Image

# from models import ChapterFileNameData

comicinfo_xml = """
<ComicInfo>
    <Title>Value</Title>
    <Series>Value</Series>
    <Number>4</Number>
    <Count>34555</Count>
    <Volume>2</Volume>
    <AlternateSeries>Value</AlternateSeries>
    <SeriesSort>Value</SeriesSort>
    <LocalizedSeries>Value</LocalizedSeries>
    <AlternateNumber>34555</AlternateNumber>
    <AlternateCount>34555</AlternateCount>
    <Summary>Value</Summary>
    <Notes>Value</Notes>
    <Year>34555</Year>
    <Month>34555</Month>
    <Day>34555</Day>
    <Writer>Value</Writer>
    <Inker>Value</Inker>
    <Colorist>Value</Colorist>
    <Letterer>Value</Letterer>
    <CoverArtist>Value</CoverArtist>
    <Editor>Value</Editor>
    <Translator>Value</Translator>
    <Publisher>Value</Publisher>
    <Imprint>Value</Imprint>
    <Genre>Value</Genre>
    <Tags>Value</Tags>
    <Web>Value</Web>
    <PageCount>34555</PageCount>
    <LanguageISO>Value</LanguageISO>
    <Format>Value</Format>
    <BlackAndWhite>Yes</BlackAndWhite>
    <Manga>Yes</Manga>
    <Characters>Value</Characters>
    <Teams>Value</Teams>
    <Locations>Value</Locations>
    <ScanInformation>Value</ScanInformation>
    <StoryArc>Value</StoryArc>
    <StoryArcNumber>34555</StoryArcNumber>
    <SeriesGroup>Value</SeriesGroup>
    <AgeRating>Rating Pending</AgeRating>
    <CommunityRating>34555</CommunityRating>
</ComicInfo>"""
# Manga Tagger
from MangaManager.MetadataManagerLib import MetadataManager, models
from MangaManager.MetadataManagerLib.cbz_handler import *
from MangaManager.VolumeManager import VolumeManager
from MangaManager.VolumeManager.models import ChapterFileNameData


class TestsMetadataManager(unittest.TestCase):
    def setUp(self) -> None:

        self.test_files_names = []
        print("\n", self._testMethodName)
        print("Setup:")
        for ai in range(3):
            out_tmp_zipname = f"Test_{ai}_{random.randint(1, 6000)}.cbz"
            self.test_files_names.append(out_tmp_zipname)
            self.temp_folder = tempfile.mkdtemp()
            # print("", self._testMethodName)
            print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)
            with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
                for i in range(5):
                    image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
                    image.format = "JPEG"
                    # file = tempfile.NamedTemporaryFile(suffix=f'.jpg', prefix=str(i).zfill(3), dir=self.temp_folder)
                    imgByteArr = io.BytesIO()
                    image.save(imgByteArr, format=image.format)
                    imgByteArr = imgByteArr.getvalue()
                    # image.save(file, format='JPEG')
                    # file.write(image.tobytes())
                    zf.writestr(os.path.basename(f"{str(i).zfill(3)}.jpg"), imgByteArr)

            self.initial_dir_count = len(os.listdir(os.getcwd()))

    def tearDown(self) -> None:
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_replace_file(self):
        """The number of files read in the output cbz must be the same as in the input (check needed to not end up
        with empty unreadable files """
        import tkinter as tk
        first_file_chapter = ""
        second_file_chapter = ""

        test_files = self.test_files_names
        opened_cbz = ReadComicInfo(test_files[0], ignore_empty_metadata=True)
        number_files_preprocess_1 = opened_cbz.total_files
        opened_cbz = 0  # reset so file gets closed
        opened_cbz = ReadComicInfo(test_files[1], ignore_empty_metadata=True)
        number_files_preprocess_2 = opened_cbz.total_files
        opened_cbz = 0  # reset so file gets closed

        random_int = random.random()
        root = tk.Tk()
        app: MetadataManager.App = MetadataManager.App(root)
        app.create_loadedComicInfo_list(test_files)

        for widget_var in app.widgets_var:
            if str(widget_var) == "OptionMenu_BlackWhite":
                widget_var.set(ComicInfo.YesNo.YES)
            elif str(widget_var) == "OptionMenu_Manga":
                widget_var.set(ComicInfo.Manga.YES_AND_RIGHT_TO_LEFT)
            elif str(widget_var) == "OptionMenu_AgeRating":
                widget_var.set(ComicInfo.AgeRating.RATING_PENDING)
            elif str(widget_var) == "CommunityRating":
                widget_var.set(int(random_int))
            elif isinstance(widget_var, tk.StringVar):
                widget_var.set(f"This is: {str(widget_var)} modified randint:{random_int}")

            # else:
            #     widget_var.set(random_int)
        app.input_1_summary_obj.set(f"This is the summary_{random_int}")

        # Chapter number must be kept when handling multiple files they can't be the same.

        app.do_save_UI()

        opened_cbz = ReadComicInfo(test_files[0])
        number_files_postprocess = opened_cbz.total_files
        xml_postprocess = opened_cbz.to_ComicInfo()
        if not first_file_chapter:
            first_file_chapter = xml_postprocess.get_Number()

        # self.assertAlmostEqual(number_files_preprocess, number_files_postprocess)
        print(f"Asserting first file {number_files_preprocess_1} vs {number_files_postprocess}, delta 1")
        self.assertAlmostEqual(number_files_preprocess_1, number_files_postprocess, delta=1)

        opened_cbz = ReadComicInfo(test_files[1])
        number_files_postprocess = opened_cbz.total_files
        xml_postprocess = opened_cbz.to_ComicInfo()
        print(f"Asserting second file {number_files_preprocess_2} vs {number_files_postprocess}, delta 1")
        self.assertAlmostEqual(number_files_preprocess_2, number_files_postprocess, delta=1)

        print(f"Random assertion values")
        app: MetadataManager.App = MetadataManager.App(root)
        app.create_loadedComicInfo_list(test_files)
        for i in range(7):
            with self.subTest(i=i):
                widget_var = app.widgets_var[random.randint(0, len(app.widgets_var))]
                if str(widget_var) == "OptionMenu_BlackWhite":
                    widget_var.set(ComicInfo.YesNo.YES)
                elif str(widget_var) == "OptionMenu_Manga":
                    self.assertEqual(widget_var.get(), ComicInfo.Manga.YES_AND_RIGHT_TO_LEFT)
                elif str(widget_var) == "OptionMenu_AgeRating":
                    self.assertEqual(widget_var.get(), ComicInfo.AgeRating.RATING_PENDING)
                elif isinstance(widget_var, models.LongText):
                    self.assertEqual(widget_var.get(), f"This is the summary_{random_int}")
                elif str(widget_var) == "CommunityRating":
                    self.assertEqual(widget_var.get(), int(random_int))
                elif isinstance(widget_var, tk.StringVar):
                    self.assertEqual(widget_var.get(), f"This is: {str(widget_var)} modified randint:{random_int}")

                # else:
                #     self.assertEqual(widget_var.get(), random_int)


def get_newFilename(files: list[str], volumeNumber) -> str:
    for cbz_path in files:
        filepath = cbz_path
        filename = os.path.basename(filepath)
        regexSearch = re.findall(r"(?i)(.*)((?:Chapter|CH)(?:\.|\s)[0-9]+[.]*[0-9]*)(\.[a-z]{3})", filename)
        if regexSearch:
            r = regexSearch[0]
            file_regex_finds: ChapterFileNameData = ChapterFileNameData(name=r[0], chapterinfo=r[1],
                                                                        afterchapter=r[2], fullpath=filepath,
                                                                        volume=volumeNumber)
        else:
            regexSearch = re.findall(r"(?i)(.*\s)([0-9]+[.]*[0-9]*)(\.[a-z]{3}$)",
                                     filename)  # TODO: this regex must be improved yo cover more test cases
            if regexSearch:
                r = regexSearch[0]
                file_regex_finds: ChapterFileNameData = ChapterFileNameData(name=r[0], chapterinfo=r[1],
                                                                            afterchapter=r[2],
                                                                            fullpath=filepath,
                                                                            volume=volumeNumber)
        new_file_path = os.path.dirname(filepath)
        newFile_Name = f"{new_file_path}/{file_regex_finds.name} Vol.{volumeNumber} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}".replace(
            "  ", " ")
        return newFile_Name


class TestsVolumeManager(unittest.TestCase):
    def setUp(self) -> None:

        self.test_files_names = []
        print("\n", self._testMethodName)
        print("Setup:")
        for ai in range(3):
            out_tmp_zipname = f"Test_{ai}_Vol.05_Ch.032_{random.randint(1, 6000)}.cbz"
            self.test_files_names.append(out_tmp_zipname)
            self.temp_folder = tempfile.mkdtemp()
            # print("", self._testMethodName)
            print(f"     Creating: {out_tmp_zipname}")  # , self._testMethodName)
            with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
                for i in range(5):
                    image = Image.new('RGB', size=(20, 20), color=(255, 73, 95))
                    image.format = "JPEG"
                    # file = tempfile.NamedTemporaryFile(suffix=f'.jpg', prefix=str(i).zfill(3), dir=self.temp_folder)
                    imgByteArr = io.BytesIO()
                    image.save(imgByteArr, format=image.format)
                    imgByteArr = imgByteArr.getvalue()
                    # image.save(file, format='JPEG')
                    # file.write(image.tobytes())
                    zf.writestr(os.path.basename(f"{str(i).zfill(3)}.jpg"), imgByteArr)

            self.initial_dir_count = len(os.listdir(os.getcwd()))

    def tearDown(self) -> None:
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)
        try:
            print(f"     Deleting: {self.new_filePath}")  # , self._testMethodName)
            os.remove(self.new_filePath)
        except Exception as e:
            print(e)

    @unittest.skip("Not implemented")
    def test_rename(self):
        import tkinter as tk
        # original_cleanup_var1 = 0
        # initial_dir_count = len(os.listdir(os.path.dirname(test_path)))
        random_vol_number = random.randint(1, 500)
        test_path_dir = os.getcwd()

        new_filePath = get_newFilename(self.test_files_names, random_vol_number)
        self.new_filePath = new_filePath
        asert_name = os.path.basename(new_filePath)

        with zipfile.ZipFile(self.test_files_names[0], 'r') as zin:
            initial_dir_count = len(zin.namelist())

            #  Proceed with testing
            root = tk.Tk()
            app = VolumeManager.App(root)
            app.cli_set_volume(random_vol_number)
            app.cli_select_files([self.test_files_names[0]])
            app.checkbutton_4_settings_val.set(True)  # Enables saving to comicinfo
            app.process()

            app = ReadComicInfo(new_filePath, ignore_empty_metadata=False).to_ComicInfo()

            with zipfile.ZipFile(new_filePath, 'r') as zin:
                final_dir_count = len(zin.namelist())
            items_in_test_path_dir = os.listdir(test_path_dir)
            print(f"Aserting if renamed file exists in directory ({asert_name} in Folder)")
            self.assertTrue(asert_name in items_in_test_path_dir)
            print(f"Aserting if new volume numer in comicinfo is saved ({random_vol_number}=={app.get_Volume()})")
            self.assertEqual(random_vol_number, app.get_Volume())

        # self.test_files_names[0] = os.path.basename(new_filePath)


if __name__ == '__main__':
    unittest.main()
