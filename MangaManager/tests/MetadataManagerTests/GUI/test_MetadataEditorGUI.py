import glob
import importlib
import os
import random
from tkinter.filedialog import askopenfiles

from ComicInfo import ComicInfo
from logging_setup import add_trace_level
from MangaManager.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from MangaManager.MetadataManager import MetadataManagerGUI
from MangaManager.MetadataManager.MetadataManagerLib import MetadataManagerLib
from tests.common import create_dummy_files, TKinterTestCase, parameterized_class, create_test_cbz

add_trace_level()
layouts_path = os.path.abspath("src/Layouts")
print(layouts_path)

modules = glob.glob(os.path.join(layouts_path, "*.py"))
print(f"Found modules: [{', '.join(modules)}]")
extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
print(f"Found extensions: [{', '.join(extensions)}]")
loaded_layouts = []
# Note: Layout is the class
for ext in extensions:
    loaded_layouts.append([importlib.import_module(f'.{ext}', package="src.Layouts").Layout])


@parameterized_class(('GUI',), loaded_layouts)
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
        self.root = app = self.GUI()
        app.is_test = True
        app.title("test_all_ui_fields_loaded")
        for tag in MetadataManagerLib.cinfo_tags:
            with self.subTest(f"{tag}"):
                print(f"Assert '{tag}' widget is displayed")
                self.assertTrue(tag in app.widget_mngr.get_tags())
        app.destroy()

    def test_all_fields_map_to_cinfo(self):
        self.root = app = self.GUI()
        app.is_test = True
        app.title("test_all_fields_map_to_cinfo")
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

        app._serialize_gui_to_cinfo()
        for cinfo_tag in app.cinfo_tags:
            widget = app.widget_mngr.get_widget(cinfo_tag)
            # if not isinstance(widget, ComboBoxWidget):
            #     continue
            with self.subTest(f"{cinfo_tag}"):
                print(f"Comparing '{widget.get()}' vs ('{cinfo_tag}' or '{random_number}')")
                self.assertTrue(widget.get() == cinfo_tag or widget.get() == random_number or str(random_number))
        # app.process()
        app.destroy()

    def test_full_flow(self):
        def custom_askopenfiles(*_, **__):
            return [open(filename, "r") for filename in self.test_files_names]

        MetadataManagerGUI.askopenfiles = custom_askopenfiles
        self.root = app = self.GUI()
        app.is_test = True
        app.title("test_full_flow")
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
        app.destroy()


@parameterized_class(('GUI',), loaded_layouts)
class CinfoToUiTest(TKinterTestCase):
    test_files_names = None

    def setUp(self) -> None:
        self.GUI.is_test = True
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            try:
                os.remove(file)
            except PermissionError:
                ...
        self.test_files_names = create_dummy_files(2)

    def tearDown(self) -> None:
        MetadataManagerGUI.askopenfiles = askopenfiles
        print("Teardown:")
        try:
            self.root.destroy()
        except:
            ...
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

        self.root = app = self.GUI()
        app.title("test_one_field_empty_should_not_be_overwritten_by_data_from_other_cinfo_with_field_filled")


        # Create metadata objects
        cinfo_1 = ComicInfo()
        cinfo_1.series = cinfo1_series
        cinfo_2 = ComicInfo()
        cinfo_2.series = cinfo2_series

        # Created loaded metadata objects
        metadata_1 = LoadedComicInfo(self.test_files_names[0], comicinfo=cinfo_1)
        metadata_2 = LoadedComicInfo(self.test_files_names[1], comicinfo=cinfo_2)
        app.loaded_cinfo_list = [metadata_1, metadata_2]
        # app.loaded_cinfo_list_to_process = app.loaded_cinfo_list
        # There is no edited comicinfo, it should fail
        new_cinfo = ComicInfo()
        app.new_edited_cinfo = new_cinfo
        app._serialize_cinfolist_to_gui()
        app._serialize_gui_to_cinfo()
        print("Assert original values will be kept")
        self.assertEqual(app.MULTIPLE_VALUES_CONFLICT, app.new_edited_cinfo.series)
        # self.assertEqual(cinfo1_series, metadata_2.cinfo_object.series)
        app.selected_files_path = self.test_files_names
        app.pre_process()
        # print("Assert final values match original")
        # self.assertEqual(app.MULTIPLE_VALUES_CONFLICT, app.new_edited_cinfo.series)
        app.destroy()


@parameterized_class(('GUI',), loaded_layouts)
class BulkLoadingTest(TKinterTestCase):

    def setUp(self) -> None:
        self.GUI.is_test = True
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)

        self.test_files_names = create_test_cbz(4, 3)

    def tearDown(self) -> None:
        MetadataManagerGUI.askopenfiles = askopenfiles
        print("Teardown:")
        try:
            self.root.destroy()
        except:
            ...
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    def test_bulk_selection(self):
        """
        This tests the flow of loading multiple file and selecting a single file.
        It's expected that the merged comicinfo has the right data
        :return:
        """
        def custom_askopenfiles(*_, **__):
            return [open(filename, "r") for filename in self.test_files_names]

        # MetadataManagerGUI.askopenfiles = custom_askopenfiles
        self.root = app = self.GUI()
        app.is_test = True
        app.title("test_bulk_selection")
        self.pump_events()


        for i, filepath in enumerate(self.test_files_names):
            cinfo = ComicInfo()
            cinfo.set_by_tag_name("Series", f"Series_sample - {i}")
            loaded_cinfo = LoadedComicInfo(filepath, comicinfo=cinfo).load_metadata()
            app.loaded_cinfo_list.append(loaded_cinfo)
            app.on_item_loaded(loaded_cinfo)

        self.pump_events()
        app.focus_set()
        app.selected_files_treeview.selection_set(app.selected_files_treeview.get_children()[1])
        self.pump_events()
        app.focus_set()
        self.assertFalse(any([True for lcinfo in app.loaded_cinfo_list if lcinfo.has_changes]))


@parameterized_class(('GUI',), loaded_layouts)
class GenericUITest(TKinterTestCase):
    def setUp(self):
        self.GUI.is_test = True
        super().setUp()

    def test_settings_window_correctly_displayed(self):
        self.root = app = self.GUI()

        app.show_settings()
