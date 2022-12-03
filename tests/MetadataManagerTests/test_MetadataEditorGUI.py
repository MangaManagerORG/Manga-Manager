import os
import random
from tkinter.filedialog import askopenfiles

from src.MangaManager_ThePromidius.Common.loadedcomicinfo import LoadedComicInfo
from src.MangaManager_ThePromidius.MetadataManager import MetadataManagerGUI
from src.MangaManager_ThePromidius.MetadataManager import comicinfo
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib
from tests.MetadataManagerTests.common import create_dummy_files, TKinterTestCase


class UiToCinfoTest(TKinterTestCase):
    test_files_names = None

    def setUp(self) -> None:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)
        self.test_files_names = create_dummy_files(2)

    def tearDown(self) -> None:
        MetadataManagerGUI.askopenfiles = askopenfiles
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)
    def test_all_ui_fields_loaded(self):
        self.root = app = MetadataManagerGUI.App()
        for tag in MetadataManagerLib.cinfo_tags:
            with self.subTest(f"{tag}"):
                print(f"Assert '{tag}' widget is displayed")
                self.assertTrue(tag in app.widget_mngr.get_tags())

    def test_all_fields_map_to_cinfo(self):
        self.root = app = MetadataManagerGUI.App()
        # new_edited = comicinfo.ComicInfo()
        # app.new_edited_cinfo = new_edited
        app.loaded_cinfo_list = [LoadedComicInfo(filename).load_metadata() for filename in self.test_files_names]
        self.pump_events()
        app.focus_set()
        random_number = random.random()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            if widget.validation:
                app.widget_mngr.get_widget(cinfo_tag).set(random_number, )
            try:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag, )
            except AttributeError:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag, )
        # Set different entry types values

        app.widget_mngr.get_widget("Summary").widget.set("Summary", )
        app.widget_mngr.get_widget("AgeRating").widget.set("AgeRating", )
        app.widget_mngr.get_widget("BlackAndWhite").widget.set("BlackAndWhite", )
        app.widget_mngr.get_widget("Manga").widget.set("Manga", )
        # app.serialize_gui_to_edited_cinfo()
        # app.pre_process()

        app.serialize_gui_to_edited_cinfo()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            # if not isinstance(widget, ComboBoxWidget):
            #     continue
            with self.subTest(f"{cinfo_tag}"):
                print(f"Comparing '{widget.get()}' vs ('{cinfo_tag}' or '{random_number}')")
                self.assertTrue(widget.get() == cinfo_tag or widget.get() == random_number or str(random_number))
        # app.process()

    def test_full_flow(self):
        def custom_askopenfiles(*_, **__):
            return [open(filename, "r") for filename in self.test_files_names]

        MetadataManagerGUI.askopenfiles = custom_askopenfiles
        self.root = app = MetadataManagerGUI.App()
        self.pump_events()
        app.select_files()
        app.loaded_cinfo_list = [LoadedComicInfo(filename).load_metadata() for filename in self.test_files_names]
        self.pump_events()
        app.focus_set()

        random_number = random.random()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            if widget.validation:
                app.widget_mngr.get_widget(cinfo_tag).set(random_number, )
            try:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag, )
            except AttributeError:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag, )
        # Set different entry types values

        app.widget_mngr.get_widget("Summary").widget.set("Summary", )
        app.widget_mngr.get_widget("AgeRating").widget.set("AgeRating", )
        app.widget_mngr.get_widget("BlackAndWhite").widget.set("BlackAndWhite", )
        app.widget_mngr.get_widget("Manga").widget.set("Manga", )
        app.pre_process()


class CinfoToUiTest(TKinterTestCase):
    test_files_names = None

    def setUp(self) -> None:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)
        self.test_files_names = create_dummy_files(2)

    def tearDown(self) -> None:
        MetadataManagerGUI.askopenfiles = askopenfiles
        print("Teardown:")
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_one_field_empty_should_not_be_overwritten_by_data_from_other_cinfo_with_field_filled(self):
        # TEST DATA
        cinfo1_series = "This series from file 1 should be kept and not be applied to cinfo 2"
        cinfo2_series = ""

        self.root = app = MetadataManagerGUI.App()


        # Create metadata objects
        cinfo_1 = comicinfo.ComicInfo()
        cinfo_1.set_Series(cinfo1_series)
        cinfo_2 = comicinfo.ComicInfo()
        cinfo_2.set_Series(cinfo2_series)

        # Created loaded metadata objects
        metadata_1 = LoadedComicInfo(self.test_files_names[0], comicinfo=cinfo_1)
        metadata_2 = LoadedComicInfo(self.test_files_names[1], comicinfo=cinfo_2)
        app.loaded_cinfo_list = [metadata_1, metadata_2]
        app.loaded_cinfo_list_to_process = app.loaded_cinfo_list
        # There is no edited comicinfo, it should fail
        new_cinfo = comicinfo.ComicInfo()
        app.new_edited_cinfo = new_cinfo
        app._serialize_cinfolist_to_gui()
        app.serialize_gui_to_edited_cinfo()
        print("Assert original values will be kept")
        self.assertEqual(app.MULTIPLE_VALUES_CONFLICT, app.new_edited_cinfo.get_Series())
        # self.assertEqual(cinfo1_series, metadata_2.cinfo_object.get_Series())
        app.selected_files_path = self.test_files_names
        app.pre_process()
        # print("Assert final values match original")
        # self.assertEqual(app.MULTIPLE_VALUES_CONFLICT, app.new_edited_cinfo.get_Series())


