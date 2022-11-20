import os
import random
from tkinter.filedialog import askopenfiles

from MangaManager_ThePromidius.Common.loadedcomicinfo import LoadedComicInfo
from src.MangaManager_ThePromidius.MetadataManager import MetadataManagerGUI
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

    def test_all_fields_map_to_cinfo(self):
        self.root = app = MetadataManagerGUI.App()
        # new_edited = comicinfo.ComicInfo()
        # app.new_edited_cinfo = new_edited
        app.loaded_cinfo_list = [LoadedComicInfo(filename).load_all() for filename in self.test_files_names]
        self.pump_events()
        app.focus_set()
        random_number = random.random()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            if widget.validation:
                app.widget_mngr.get_widget(cinfo_tag).set(random_number)
            try:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag)
            except AttributeError:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag)
        # Set different entry types values

        app.widget_mngr.get_widget("Summary").widget.set("Summary")
        app.widget_mngr.get_widget("AgeRating").widget.set("AgeRating")
        app.widget_mngr.get_widget("BlackAndWhite").widget.set("BlackAndWhite")
        app.widget_mngr.get_widget("Manga").widget.set("Manga")
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
        # app.proces()

    def test_full_flow(self):
        def custom_askopenfiles(*_, **__):
            return [open(filename, "r") for filename in self.test_files_names]

        MetadataManagerGUI.askopenfiles = custom_askopenfiles
        self.root = app = MetadataManagerGUI.App()
        self.pump_events()
        app.select_files()
        app.loaded_cinfo_list = [LoadedComicInfo(filename).load_all() for filename in self.test_files_names]
        self.pump_events()
        app.focus_set()

        random_number = random.random()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            if widget.validation:
                app.widget_mngr.get_widget(cinfo_tag).set(random_number)
            try:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag)
            except AttributeError:
                app.widget_mngr.get_widget(cinfo_tag).set(cinfo_tag)
        # Set different entry types values

        app.widget_mngr.get_widget("Summary").widget.set("Summary")
        app.widget_mngr.get_widget("AgeRating").widget.set("AgeRating")
        app.widget_mngr.get_widget("BlackAndWhite").widget.set("BlackAndWhite")
        app.widget_mngr.get_widget("Manga").widget.set("Manga")
        app.pre_process()
