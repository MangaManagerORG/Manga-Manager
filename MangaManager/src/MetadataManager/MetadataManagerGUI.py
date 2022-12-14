from __future__ import annotations

#
import logging
import os
import tkinter
from tkinter import Tk, Frame, messagebox as mb

from src.Common.errors import NoFilesSelected
from src.Common.utils import get_platform, open_folder
from src.MetadataManager import comicinfo
from src.MetadataManager.extensions import GUIExtensionManager

if get_platform() == "linux":
    from src.Common.GUI.FileChooserWindow import askopenfiles
else:
    from tkinter.filedialog import askopenfiles
from _tkinter import TclError


from src.Common.loadedcomicinfo import LoadedComicInfo
from src.MetadataManager.MetadataManagerLib import MetadataManagerLib
from src.MetadataManager.GUI.widgets import ComboBoxWidget, OptionMenuWidget, WidgetManager, \
    SettingsWidgetManager, ButtonWidget

from src import settings_class
main_settings = settings_class.get_setting("main")


class GUIApp(Tk, MetadataManagerLib, GUIExtensionManager):
    main_frame: Frame
    _prev_selected_items: list[LoadedComicInfo] = []
    inserting_files = False

    def __init__(self):
        super(GUIApp, self).__init__()
        self.widget_mngr = WidgetManager()
        self.control_widgets = []  # widgets that should be disabled while processing

        # self.wm_minsize(1000, 660)
        self.geometry("1000x800")
        # super(MetadataManagerLib, self).__init__()
        self.title("Manga Manager")

        self.selected_files_path = None
        self.loaded_cinfo_list: list[LoadedComicInfo] = []
        self.cinfo_tags: list[str] = []
        self.log = logging.getLogger("MetadataManager.GUI")

        # MENU
        self.main_frame = Frame(self)

        # self.main_frame = ScrolledFrameWidget(self,scrolltype="both").create_frame()
        self.main_frame.pack(expand=True, fill="both")

        ButtonWidget(master=self, text="⚙ Settings", font=('Arial', 10), command=self.show_settings).place(anchor=tkinter.NE, relx=1)


        # Add binds
        self.bind('<Control-o>', lambda x: self.select_files())
        self.bind('<Control-s>', lambda x: self.pre_process())

        # Important:
        self.cinfo_tags = self.widget_mngr.get_tags()
        # print(self.widget_mngr.get_tags())

    @property
    def prev_selected_items(self):
        """
                Returns the list of selected loaded_cinfo if any is selected. Else returns loaded_cinfo list
                :return:
                """
        return self._prev_selected_items

    @property
    def selected_items(self):
        """
        Returns the list of selected loaded_cinfo if any is selected. Else returns loaded_cinfo list
        :return:
        """
        self.selected_files_treeview.get_selected() or self.loaded_cinfo_list

        return self.selected_files_treeview.get_selected() or self.loaded_cinfo_list

    #########################################################
    # GUI Control Methods
    ############

    def select_files(self):
        # New file selection. Proceed to clean the ui to a new state
        self.widget_mngr.clean_widgets()
        self.image_cover_frame.clear()
        self.selected_files_path = list()
        self.selected_files_treeview.clear()
        self.last_folder = ""
        self.inserting_files = True
        # These are some tricks to make it easier to select files.
        # Saves last opened folder to not have to browse to it again
        if not self.last_folder:
            initial_dir = main_settings.library_path.value
        else:
            initial_dir = self.last_folder
        self.log.debug("Selecting files")
        # Open select files dialog
        selected_paths_list = askopenfiles(parent=self, initialdir=initial_dir,
                                           title="Select file to apply cover",
                                           filetypes=(("CBZ Files", ".cbz"), ("All Files", "*"),)
                                           # ("Zip files", ".zip"))
                                           ) or []

        if selected_paths_list:
            selected_parent_folder = os.path.dirname(selected_paths_list[0].name)
            if self.last_folder != selected_parent_folder or not self.last_folder:
                self.last_folder = selected_parent_folder

        self.selected_files_path = [file.name for file in selected_paths_list]

        self.log.debug(f"Selected files [{', '.join(self.selected_files_path)}]")
        self.open_cinfo_list()

        self._serialize_cinfolist_to_gui()
        self.inserting_files = False

    def show_settings(self):
        print("Show_settings")
        SettingsWidgetManager(self)

    def are_unsaved_changes(self, exist_unsaved_changes=False):
        """
        Displays the text "unsaved changes"
        :return:
        """

        if exist_unsaved_changes:  # Place the warning sign
            self.changes_saved.place(anchor=tkinter.NE, relx=0.885)
        else:  # remove the warning sign
            self.changes_saved.place_forget()

    def update_item_saved_status(self,loaded_cinfo):
        """
        Adds a warning in the filename if the loadedcinfo has changes
        :param loaded_cinfo:
        :return:
        """
        try:
            self.selected_files_treeview.item(loaded_cinfo.file_path,
                                      text=f"{'⚠' if loaded_cinfo.has_changes else ''}{loaded_cinfo.file_name}")
        except TclError: # Tests fails due to not being correctly populated. Log and skip
            self.log.error(f"Error updating saved status for item {loaded_cinfo.file_path}")

    def show_not_saved_indicator(self, loaded_cinfo_list):
        """
        Shows a litle triangle while files are not saved.
        :param loaded_cinfo_list:
        :param mark_saved:
        :return:
        """
        any_has_changes = False
        for loaded_cinfo in loaded_cinfo_list:
            self.update_item_saved_status(loaded_cinfo)
            if loaded_cinfo.has_changes:
                any_has_changes = True
        self.are_unsaved_changes(any_has_changes)


    #########################################################
    # INTERFACE IMPLEMENTATIONS
    ############

    def on_item_loaded(self, loadedcomicInfo: LoadedComicInfo):
        """
        Called by backend when an item gets added to the loaded comic info list
        :param loadedcomicInfo:
        :return:
        """
        self.selected_files_treeview.insert(loadedcomicInfo)
        self.image_cover_frame.update_cover_image([loadedcomicInfo])
        self.update()

    #########################################################
    # Errors handling / hooks implementations
    ############

    def on_processed_item(self, loaded_info: LoadedComicInfo):
        self.pb.increase_processed()
        self.update_item_saved_status(loaded_info)
        self.update()

    def on_badzipfile_error(self, exception, file_path: LoadedComicInfo):  # pragma: no cover
        mb.showerror("Error loading file",
                     f"Failed to read the file '{file_path}'.\nThis can be caused by wrong file format"
                     f" or broken file.\n"
                     f"Read the logs for more information.\n"
                     f"Skipping file...")

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.pb.increase_failed()
        mb.showerror("Unhandled exception",
                     "There was an exception that was not handled while writing the changes to the file."
                     "Please check the logs and raise an issue so this can be investigated")

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.pb.increase_failed()
        mb.showerror("Error writing to file",
                     "There was an error writing to the file. Please check the logs.")

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        mb.showwarning(f"Error reading the metadata from file",
                       f"Failed to read metadata from '{loaded_info.file_path}'\n"
                       "The file data couldn't be parsed probably because of corrupted data or bad format.\n"
                       f"Recovery was attempted and failed.\nCreating new metadata object...")

    #########################################################
    # Processing Methods
    ############

    def _serialize_cinfolist_to_gui(self, loaded_cinfo_list=None):
        """
        Display the loaded cinfo values in the ui.
        If multiple values for one field, shows conflict (keeping values)
        :param loaded_cinfo_list:
        :return:
        """
        # Clear current values
        self.widget_mngr.clean_widgets()
        if loaded_cinfo_list is None:
            loaded_cinfo_list = self.selected_items
        if main_settings.cache_cover_images:
            self.image_cover_frame.update_cover_image(loaded_cinfo_list)

        # Iterate all cinfo tags. Should there be any values that are not equal. Show "different values selected"

        for cinfo_tag in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cinfo_tag)
            tag_values = set()
            for loaded_cinfo in loaded_cinfo_list:
                tag_value = str(loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag))
                tag_values.add(tag_value if tag_value != widget.default else "")
            tag_values = tuple(tag_values)
            tag_values_len = len(tag_values)

            # All files have the same content for this field

            if tag_values_len == 1 and tag_values[0] != widget.default:
                widget.set(tag_values[0])

            # Multiple values across different files for this field
            elif tag_values_len > 1:
                # Append "multiple_values" string to the suggestion listbox
                tag_values = (self.MULTIPLE_VALUES_CONFLICT,) + tag_values
                widget.widget.set(self.MULTIPLE_VALUES_CONFLICT)

            # If it's a combobox update the suggestions listbox with the loaded values
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = list(tag_values)
            elif isinstance(widget, OptionMenuWidget):
                if tag_values_len == 1:
                    widget.update_listed_values(tag_values[0], widget.get_options())
                elif tag_values_len > 1:
                    widget.append_first(self.MULTIPLE_VALUES_CONFLICT)

    def _serialize_gui_to_cinfo(self):
        """
        Parses current UI values to a 'new_edited_cinfo'
        :return:
        """
        # is_metadata_modified
        LOG_TAG = "[UI->CINFO] "
        self.new_edited_cinfo = comicinfo.ComicInfo()
        for cinfo_tag in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cinfo_tag)
            widget_value = widget.widget.get()

            match widget_value:
                case self.MULTIPLE_VALUES_CONFLICT:
                    self.log.trace(LOG_TAG + f"Omitting {cinfo_tag}. Keeping original")
                    self.new_edited_cinfo.set_attr_by_name(cinfo_tag,self.MULTIPLE_VALUES_CONFLICT)
                case "None":
                    if widget.name == "Format":
                        self.new_edited_cinfo.set_attr_by_name(cinfo_tag, "")
                case widget.default:  # If it matches the default then do nothing
                    self.log.trace(LOG_TAG + f"Omitting {cinfo_tag}. Has default value")
                    pass
                case "":
                    self.new_edited_cinfo.set_attr_by_name(cinfo_tag, widget.default)
                    self.log.trace(LOG_TAG + f"Tag '{cinfo_tag}' content was resetted")
                case _:
                    self.new_edited_cinfo.set_attr_by_name(cinfo_tag,widget_value)
                    self.log.trace(LOG_TAG + f"Tag '{cinfo_tag}' has overwritten content: '{widget_value}'")
                    # self.log.warning(f"Unhandled case: {widget_value}")
                    pass

    def process_gui_update(self, old_selection: list[LoadedComicInfo], new_selection: list[LoadedComicInfo]):
        self._serialize_gui_to_cinfo()
        self.merge_changed_metadata(old_selection)

        self.show_not_saved_indicator(old_selection)
        self.widget_mngr.clean_widgets()
        # Display new selection data
        self._serialize_cinfolist_to_gui(new_selection)

    def toggle_control_buttons(self, enabled=False) -> None:
        for widget in self.control_widgets:
            if enabled:
                widget.configure(state="normal")
            else:
                widget.configure(state="disabled")


    def pre_process(self) -> None:
        """
        Handles UI stuff to be started prior to processing such as converting ui data to comicinfo and starting the timer
        """
        if not self.selected_files_path:
            raise NoFilesSelected()
        self.toggle_control_buttons(enabled=False)
        self.changes_saved.place_forget()
        # self.loaded_cinfo_list_to_process = self.get_selected_loaded_cinfo_list()
        self.pb.start(len(self.loaded_cinfo_list))
        # Make sure current view is saved:
        self.process_gui_update(self.selected_items,self.selected_items)
        try:
            # self._serialize_gui_to_cinfo()
            # self.merge_changed_metadata(self.loaded_cinfo_list)
            self.process()
        finally:
            self.pb.stop()
        self.show_not_saved_indicator(self.loaded_cinfo_list)
        self.new_edited_cinfo = None  # Nulling value to be safe
        self.toggle_control_buttons(enabled=True)

    # Unique methods
    def _fill_filename(self):
        if len(self.selected_items) == 1:
            self.widget_mngr.get_widget("Series").set(self.selected_items[0].file_name)

    def _treeview_open_explorer(self, file):
        open_folder(os.path.dirname(file), file)
        ...

    def _treview_reset(self, event=None):
        ...
