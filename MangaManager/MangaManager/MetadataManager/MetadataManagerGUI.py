from __future__ import annotations

import glob
import logging
import os
import tkinter
from tkinter import Frame

from ComicInfo import ComicInfo
from MangaManager.Common import ResourceLoader
from MangaManager.Common.parser import parse_volume, parse_series, parse_number
from MangaManager.Common.utils import get_platform, open_folder
from MangaManager.MetadataManager.GUI.ControlManager import ControlManager
from MangaManager.MetadataManager.GUI.MessageBox import MessageBoxWidgetFactory as mb
from MangaManager.MetadataManager.GUI.windows.AboutWindow import AboutWindow
from MangaManager.MetadataManager.GUI.windows.LoadingWindow import LoadingWindow
from MangaManager.Settings import SettingHeading
from MangaManager.Settings.Settings import Settings

if get_platform() == "linux":
    from MangaManager.MetadataManager.GUI.FileChooserWindow import askopenfiles, askdirectory
else:
    from tkinter.filedialog import askopenfiles, askdirectory
from _tkinter import TclError
from tkinterdnd2.TkinterDnD import Tk
from MangaManager.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from MangaManager.MetadataManager.GUI.widgets import ComboBoxWidget, OptionMenuWidget, WidgetManager, ButtonWidget
from MangaManager.MetadataManager.GUI.windows.SettingsWindow import SettingsWindow
from MangaManager.MetadataManager.MetadataManagerLib import MetadataManagerLib


class GUIApp(Tk, MetadataManagerLib):

    """
    This is the main logic and app
    """
    main_frame: Frame
    """
    A loading indicator to help not process changes in MainWindow when GUI is performing loading of files
    """
    inserting_files = False
    widget_mngr = WidgetManager()
    control_mngr = ControlManager()  # widgets that should be disabled while processing
    loading_window: LoadingWindow | None = None

    def __init__(self):
        super(GUIApp, self).__init__()
        self.last_folder = ""

        # self.wm_minsize(1000, 660)
        self.tk.eval('package require tile')
        self.geometry("1000x820")
        self.title("Manga Manager")

        self.selected_files_path = None
        self.loaded_cinfo_list: list[LoadedComicInfo] = []
        self.log = logging.getLogger("MetaManager.GUI")

        # MENU
        self.main_frame = Frame(self)
        self.main_frame.pack(expand=True, fill="both")


        # Add binds
        self.bind('<Control-o>', lambda x: self.select_files())
        self.bind('<Control-s>', lambda x: self.pre_process())
        self.bind('<Control-f>', self.process_fetch_online)

        # Icons
        icon_path = ResourceLoader.get('settings.png')
        self.settings_icon = tkinter.PhotoImage(name="settings_icon", master=self, file=icon_path)

        icon_path = ResourceLoader.get('clear_icon.png')
        self.clear_icon = tkinter.PhotoImage(name="clear_icon", master=self, file=icon_path)

        icon_path = ResourceLoader.get('fetch_online_ico.png')
        self.fetch_online_icon = tkinter.PhotoImage(name="fetch_online_icon", master=self, file=icon_path)

        icon_path = ResourceLoader.get('save_icon.png')
        self.save_icon = tkinter.PhotoImage(name="save_icon", master=self, file=icon_path)

        icon_path = ResourceLoader.get('filename_fill_icon.png')
        self.filename_fill_icon = tkinter.PhotoImage(name="filename_fill", master=self, file=icon_path)

        icon_path = ResourceLoader.get('open_folder.png')
        self.open_folder_icon = tkinter.PhotoImage(name="open_folder", master=self, file=icon_path)

        icon_path = ResourceLoader.get('open_file.png')
        self.open_file_icon = tkinter.PhotoImage(name="open_file", master=self, file=icon_path)

        # Floating icons
        frame = Frame(self)
        frame.place(anchor=tkinter.NE, relx=1,rely=0.003)
        ButtonWidget(master=frame, text="Settings", image=self.settings_icon, font=('Arial', 10), compound="left",
                     command=self.show_settings).pack(side="left", fill="y", padx=(0, 5))

        ButtonWidget(master=frame, text="About", font=('Arial', 10), command=self.show_about).pack(side="left", fill="y", padx=(0, 5))
    def report_callback_exception(self, *_):
        """
        Overrides builtin method so exceptions get loged and are not silent
        :param _:
        :return:
        """
        self.log.exception("Unhandled exception")

    @property
    def cinfo_tags(self):
        return self.widget_mngr.cinfo_tags

    @property
    def selected_items(self):
        """
        Returns the list of selected loaded_cinfo if any is selected. Else returns loaded_cinfo list
        :return:
        """
        return self.selected_files_treeview.get_selected() or self.loaded_cinfo_list

    #########################################################
    # GUI Control Methods
    ############

    def select_files(self):
        # These are some tricks to make it easier to select files.
        # Saves last opened folder to not have to browse to it again
        if not self.last_folder:
            initial_dir = Settings().get(SettingHeading.Main, 'library_path')
        else:
            initial_dir = self.last_folder
        self.log.debug("Selecting files")
        # Open select files dialog
        selected_paths_list = askopenfiles(parent=self, initialdir=initial_dir,
                                           title="Select file(s)",
                                           filetypes=(("CB* Files", (".cbz", ".cbr")), ("CBZ Files", ".cbz"),
                                                      ("CBR Files", ".cbr"), ("All Files", "*"), ("Zip files", ".zip"))
                                           # ("Zip files", ".zip"))
                                           ) or []

        if selected_paths_list:
            selected_parent_folder = os.path.dirname(selected_paths_list[0].name)
            if self.last_folder != selected_parent_folder or not self.last_folder:
                self.last_folder = selected_parent_folder
        else:
            return
        self.selected_files_path = [file.name for file in selected_paths_list]
        self.load_selected_files()

    def select_folder(self):
        # These are some tricks to make it easier to select files.
        # Saves last opened folder to not have to browse to it again
        if not self.last_folder:
            initial_dir = Settings().get(SettingHeading.Main, 'library_path')
        else:
            initial_dir = self.last_folder
        self.log.debug("Selecting files")
        # Open select files dialog

        folder_path = askdirectory(initialdir=initial_dir)
        if not folder_path:
            return
        self.selected_files_path = glob.glob(root_dir=folder_path, pathname=os.path.join(folder_path, "**/*.cbz"),
                                             recursive=True)
        # TODO: Auto select recursive or not
        # self.selected_files_path = [str(Path(folder_path, file)) for file in os.listdir(folder_path) if file.endswith(".cbz")]
        self.load_selected_files()

    def load_selected_files(self,new_selection:list=None,is_event_dragdrop = False):

        self.control_mngr.lock()
        self.widget_mngr.toggle_widgets(enabled=False)
        append_and_keep = is_event_dragdrop and not Settings().get(SettingHeading.Main,"remove_old_selection_on_drag_drop")
        if append_and_keep: # Should keep previously selected files. Just load the new ones in selection
            self.selected_files_path = list(set((self.selected_files_path or []) + new_selection))
        else:
            # Append new files and keep the old ones
            self.widget_mngr.clean_widgets()  # New file selection. Proceed to clean the ui to a new state
            self.image_cover_frame.clear()
            self.selected_files_path = self.selected_files_path if new_selection is None else new_selection
            self.selected_files_treeview.clear()
        self.selected_files_path = sorted(self.selected_files_path)
        self.log.debug(f"Selected files [{', '.join(self.selected_files_path)}]")
        self.inserting_files = True
        self.loading_window = LoadingWindow(self.master, len(self.selected_files_path))

        if self.open_cinfo_list(self.loading_window.is_abort,append_and_keep):
            self._serialize_cinfolist_to_gui()
        else:
            self.clean_selected()
        self.loading_window.finish_loading()
        self.loading_window = None
        self.inserting_files = False
        self.control_mngr.unlock()
        self.widget_mngr.toggle_widgets(enabled=True)

    def show_settings(self):
        SettingsWindow(self)

    def show_about(self):
        AboutWindow(self)

    def are_unsaved_changes(self, exist_unsaved_changes=False):
        """
        Displays the text "unsaved changes"
        :return:
        """
        if exist_unsaved_changes:  # Place the warning sign
            self.changes_saved.place(anchor=tkinter.NE, relx=0.885)
        else:  # remove the warning sign
            self.changes_saved.place_forget()

    def update_item_saved_status(self, loaded_cinfo):
        """
        Adds a warning in the filename if the loadedcinfo has changes
        :param loaded_cinfo:
        :return:
        """
        try:
            self.selected_files_treeview.item(loaded_cinfo.file_path,
                                              text=f"{'⚠' if loaded_cinfo.has_changes else ''}{loaded_cinfo.file_name}")
        except TclError:  # Tests fails due to not being correctly populated. Log and skip
            self.log.error(f"Error updating saved status for item {loaded_cinfo.file_path}")

    def show_not_saved_indicator(self, loaded_cinfo_list=None):
        """
        Shows a litle triangle when files are not saved and are modified
        :param loaded_cinfo_list:
        :param mark_saved:
        :return:
        """
        if loaded_cinfo_list is None:
            loaded_cinfo_list = self.loaded_cinfo_list
        any_has_changes = False
        for loaded_cinfo in loaded_cinfo_list:
            self.update_item_saved_status(loaded_cinfo)
            if loaded_cinfo.has_changes:
                any_has_changes = True
        self.are_unsaved_changes(any_has_changes)

    #########################################################
    # INTERFACE IMPLEMENTATIONS
    ############

    def on_item_loaded(self, loaded_cinfo: LoadedComicInfo, cursor, total) -> bool:
        """
        Called by backend when an item gets added to the loaded comic info list
        :param loaded_cinfo:
        :return:
        """
        if self.loading_window.initialized:
            self.loading_window.update()
            self.loading_window.loaded_file(loaded_cinfo.file_name)
        self.selected_files_treeview.insert(loaded_cinfo)
        self.image_cover_frame.update_cover_image([loaded_cinfo])
        self.update()
        return self.loading_window.abort_flag
    #########################################################
    # Errors handling / hooks implementations
    ############

    def on_processed_item(self, loaded_info: LoadedComicInfo):
        self.pb.increase_processed()
        self.update_item_saved_status(loaded_info)
        self.update()

    def on_badzipfile_error(self, exception, file_path: LoadedComicInfo):  # pragma: no cover
        mb.showerror(self.main_frame, "Error loading file",
                     f"Failed to read the file '{file_path}'.\nThis can be caused by wrong file format"
                     f" or broken file.\n"
                     f"Read the logs for more information.\n"
                     f"Skipping file...")

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.pb.increase_failed()
        mb.showerror(self.main_frame, "Unhandled exception",
                     "There was an exception that was not handled while writing the changes to the file."
                     "Please check the logs and raise an issue so this can be investigated")

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.pb.increase_failed()
        mb.showerror(self.main_frame, "Error writing to file",
                     "There was an error writing to the file. Please check the logs.")

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        mb.showwarning(self.main_frame, f"Error reading the metadata from file",
                       f"Failed to read metadata from '{loaded_info.file_path}'\n"
                       "The file data couldn't be parsed probably because of corrupted data or bad format.\n"
                       f"Recovery was attempted and failed.\nCreating new metadata object...")

    def on_manga_not_found(self, exception, series_name):  # pragma: no cover
        mb.showerror(self.main_frame, "Couldn't find matching series",
                     f"The metadata source couldn't find the series '{series_name}'")

    def on_missing_rar_tools(self, exception):
        box = mb.get_onetime_messagebox()("missing_rar_tools")
        box.with_title("Missing Rar Tools"). \
            with_description("CBR files can't be read because third party rar tools are missing. Skipping files"). \
            with_icon(mb.get_onetime_messagebox().icon_error). \
            with_actions([mb.get_box_button()(0, "Ok")]). \
            build().prompt()

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
        if Settings().get(SettingHeading.Main, 'cache_cover_images'):
            self.image_cover_frame.update_cover_image(loaded_cinfo_list)

        # Iterate all cinfo tags. Should there be any values that are not equal. Show "different values selected"

        for cinfo_tag in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cinfo_tag)
            tag_values = set()
            for loaded_cinfo in loaded_cinfo_list:
                tag_value = str(loaded_cinfo.cinfo_object.get_by_tag_name(cinfo_tag))
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

    def _serialize_gui_to_cinfo(self) -> ComicInfo:
        """
        Parses current UI values to a 'new_edited_cinfo'
        :return:
        """
        # is_metadata_modified
        LOG_TAG = "[UI->CINFO] "
        ci = ComicInfo()
        for cinfo_tag in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cinfo_tag)
            widget_value = widget.widget.get()

            match widget_value:
                case self.MULTIPLE_VALUES_CONFLICT:
                    self.log.trace(LOG_TAG + f"Omitting {cinfo_tag}. Keeping original")
                    ci.set_by_tag_name(cinfo_tag, self.MULTIPLE_VALUES_CONFLICT)
                case "None":
                    if widget.name == "Format":
                        ci.set_by_tag_name(cinfo_tag, "")
                case widget.default:  # If it matches the default then do nothing
                    self.log.trace(LOG_TAG + f"Omitting {cinfo_tag}. Has default value")
                case "":
                    ci.set_by_tag_name(cinfo_tag, "")
                    self.log.trace(LOG_TAG + f"Tag '{cinfo_tag}' content was reset or was empty")
                case _:
                    ci.set_by_tag_name(cinfo_tag, widget_value)
                    self.log.trace(LOG_TAG + f"Tag '{cinfo_tag}' has overwritten content: '{widget_value}'")
                    # self.log.warning(f"Unhandled case: {widget_value}")
        return ci

    def process_gui_update(self, old_selection: list[LoadedComicInfo], new_selection: list[LoadedComicInfo]):
        self.new_edited_cinfo = self._serialize_gui_to_cinfo()
        self.merge_changed_metadata(old_selection)

        self.show_not_saved_indicator(old_selection)
        self.widget_mngr.clean_widgets()
        # Display new selection data
        self._serialize_cinfolist_to_gui(new_selection)


    def fill_from_filename(self) -> None:
        """Handles taking the currently selected file and parsing any information out of it and writing to Empty fields"""
        if not self.selected_files_path:
            mb.showwarning(self.main_frame, "No files selected", "No files were selected.")
            self.log.warning("No files selected")
            return

        self.control_mngr.toggle(enabled=False)
        self.changes_saved.place_forget()
        self.pb.start(len(self.loaded_cinfo_list))
        # Make sure current view is saved:
        self.process_gui_update(self.selected_items, self.selected_items)
        any_items_changed = False
        try:
            for item in self.selected_items:
                # We can parse Series, Volume, Number, and Scan Info
                if not item.cinfo_object.volume:
                    vol = parse_volume(item.file_name)
                    if vol:
                        item.cinfo_object.volume = vol
                        item.has_changes = True
                        any_items_changed = True

                if not item.cinfo_object.series:
                    series = parse_series(item.file_name)
                    if series:
                        item.cinfo_object.series = series
                        item.has_changes = True
                        any_items_changed = True

                if not item.cinfo_object.number:
                    number = parse_number(item.file_name)
                    if number:
                        item.cinfo_object.number = number
                        item.has_changes = True
                        any_items_changed = True
        finally:
            self.pb.stop()
        self.show_not_saved_indicator(self.loaded_cinfo_list)
        if any_items_changed:
            self.show_not_saved_indicator(self.selected_items)
            self._serialize_cinfolist_to_gui(self.selected_items)
        self.control_mngr.toggle(enabled=True)

    def pre_process(self) -> None:
        """
        Handles UI stuff to be started prior to processing such as converting ui data to comicinfo and starting the timer
        """
        if not self.selected_files_path:
            mb.showwarning(self.main_frame, "No files selected", "No files were selected.")
            self.log.warning("No files selected")
            return
        self.control_mngr.toggle(enabled=False)
        self.changes_saved.place_forget()
        self.pb.start(len(self.loaded_cinfo_list))
        # Make sure current view is saved:
        self.process_gui_update(self.selected_items, self.selected_items)
        try:
            self.process()
        finally:
            self.pb.stop()
        self.show_not_saved_indicator(self.loaded_cinfo_list)
        self.new_edited_cinfo = None  # Nulling value to be safe
        self.control_mngr.toggle(enabled=True)

    # Unique methods
    def _fill_filename(self):
        if len(self.selected_items) == 1:
            self.widget_mngr.get_widget("Series").set(self.selected_items[0].file_name)

    def _fill_foldername(self):
        if len(self.selected_items) == 1:
            self.widget_mngr.get_widget("Series").set(
                os.path.basename(os.path.dirname(self.selected_items[0].file_path)))
        else:
            for loaded_cinfo in self.selected_items:
                _ = loaded_cinfo.cinfo_object
                loaded_cinfo.cinfo_object.series = os.path.basename(os.path.dirname(loaded_cinfo.file_path))
                loaded_cinfo.has_changes = True
            self.show_not_saved_indicator(self.selected_items)
            self.widget_mngr.clean_widgets()
            # Display new selection data
            self._serialize_cinfolist_to_gui(self.selected_items)

    def _treeview_open_explorer(self, file):
        open_folder(os.path.dirname(file), file)
        ...

    def _treview_reset(self, event=None):
        ...

    def display_extensions(self, parent_frame):
        from MangaManager import loaded_extensions
        for loaded_extension in loaded_extensions:
            tkinter.Button(parent_frame, text=loaded_extension.name, command=lambda load_ext=loaded_extension:
            load_ext(parent_frame, super_=self)).pack(side="top")

    def process_fetch_online(self, *_):
        series_name = self.widget_mngr.get_widget("Series").get().strip()
        if series_name == self.MULTIPLE_VALUES_CONFLICT:
            mb.showwarning(self.main_frame, "Not a valid series name. Multiple values conflict.")
            self.log.info("Not a valid series name - Conflic with other series name in selection")
            return
        if series_name in (None, "") and self.widget_mngr.get_widget("Web").get() in (None,""):
            mb.showwarning(self.main_frame, "Not a valid series name", "The current series name is empty or not valid.")
            self.log.info("Not a valid series name - The current series name is empty or not valid.")
            return

        # If multiple files are selected, validate that all files have the same series name
        if len(self.selected_items) > 1:
            if not all(series_name == item.cinfo_object.series.strip() for item in self.selected_items):
                mb.showwarning(self.main_frame, "All series MUST match and may not contain blanks",
                               "All files' series names are not the same.")
                self.log.info(
                    "All series MUST match and may not contain blanks - All files' series names are not the same.")
                return

        cinfo = self.fetch_online(self._serialize_gui_to_cinfo())
        if cinfo is None:
            return

        self._serialize_cinfolist_to_gui([LoadedComicInfo(None, cinfo, load_default_metadata=False)])

    def clean_selected(self):

        self.widget_mngr.clean_widgets()
        self.image_cover_frame.clear()
        self.selected_files_path = list()
        self.selected_files_treeview.clear()