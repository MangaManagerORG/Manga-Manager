from __future__ import annotations

import logging
import os
import tkinter
from tkinter import Tk, Frame, Label, messagebox as mb, ttk

from src.MangaManager_ThePromidius import settings
from src.MangaManager_ThePromidius.Common.errors import NoFilesSelected
from src.MangaManager_ThePromidius.Common.utils import get_platform
from src.MangaManager_ThePromidius.MetadataManager.extensions import GUIExtensionManager

if get_platform() == "linux":
    from src.MangaManager_ThePromidius.Common.GUI.FileChooserWindow import askopenfiles
else:
    from tkinter.filedialog import askopenfiles

from src.MangaManager_ThePromidius.MetadataManager import comicinfo
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib
from src.MangaManager_ThePromidius.Common.loadedcomicinfo import LoadedComicInfo
from src.MangaManager_ThePromidius.Common.GUI.widgets import ComboBoxWidget, LongTextWidget, OptionMenuWidget, \
    ScrolledFrameWidget, WidgetManager, CoverFrame, ButtonWidget, SettingsWidgetManager, TreeviewWidget, \
    ProgressBarWidget

# import MangaManager_ThePromidius.settings
main_settings = settings.get_setting("main")



class App(Tk, MetadataManagerLib, GUIExtensionManager):
    main_frame: Frame
    _prev_selected_items: list[LoadedComicInfo] = []
    inserting_files = False

    def __init__(self):
        super(App, self).__init__()
        self.control_widgets = []  # widgets that should be disabled while processing
        # self.wm_minsize(1000, 660)
        self.geometry("1000x800")
        # super(MetadataManagerLib, self).__init__()
        self.title("Manga Manager")

        self.widget_mngr = WidgetManager()
        self.selected_files_path = None
        self.loaded_cinfo_list: list[LoadedComicInfo] = []
        self.cinfo_tags: list[str] = []
        style = ttk.Style()
        current_theme = style.theme_use()
        style.theme_settings(current_theme, {"TNotebook.Tab": {"configure": {"padding": [20, 5],
                                                                             "font": ('Arial', 20)}}})

        self.log = logging.getLogger("MetadataManager.GUI")
        self._initialize_frames()
        self.display_side_bar()
        self.display_widgets()
        self.display_extensions(self.extensions_tab_frame)
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
        new_selection = self.selected_files_treeview.get_selected() or self.loaded_cinfo_list

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
            initial_dir = main_settings.library_path
        else:
            initial_dir = self.last_folder
        self.log.debug("Selecting files")
        # Open select files dialog
        selected_paths_list = askopenfiles(parent=self.master, initialdir=initial_dir,
                                           title="Select file to apply cover",
                                           filetypes=(("CBZ Files", ".cbz"), ("All Files", "*"),)
                                           # ("Zip files", ".zip"))
                                           )
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

    def unsaved_files(self, saved=False):
        """
        Displays the text "unsaved changes"
        :return:
        """
        if saved:
            self.changes_saved.place_forget()
        else:
            self.changes_saved.place(anchor=tkinter.NE, relx=0.885)
        # self.update()

    def show_not_saved_indicator(self, loaded_cinfo_list, mark_saved=False):
        """
        Shows a litle triangle while files are not saved.
        :param loaded_cinfo_list:
        :param mark_saved:
        :return:
        """
        for loaded_cinfo in loaded_cinfo_list:
            if loaded_cinfo.is_metadata_modified(self.cinfo_tags):
                # treeview_index = self.selected_files_treeview.index(cinfo.file_path)
                self.selected_files_treeview.item(loaded_cinfo.file_path, text=f"{'' if mark_saved else '⚠'}{loaded_cinfo.file_name}")
                # self.update()
        self.unsaved_files(not any([cinfo.has_changes for cinfo in loaded_cinfo_list]))

    #########################################################
    # GUI Display Methods
    ############

    def _initialize_frames(self) -> None:
        # MENU
        self.main_frame = Frame(self)

        # self.main_frame = ScrolledFrameWidget(self,scrolltype="both").create_frame()
        self.main_frame.pack(expand=True, fill="both")

        setting_btn = ButtonWidget(master=self, text="⚙ Settings", font=('Arial', 10), command=self.show_settings)
        # self.main_frame.configure(pady=10, padx=10)
        # self.main_frame.configure(bg="blue", borderwidth=2)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side="right", expand=True, fill="both")

        tab_1 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.basic_info_frame = tab_1.create_frame()

        self.notebook.add(tab_1, text="Basic Info")

        tab_2 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.people_info_frame = tab_2.create_frame()
        self.people_info_frame.configure(padx=20)
        self.notebook.add(tab_2, text="People Info")

        tab_3 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.numbering_info_frame = tab_3.create_frame()
        self.numbering_info_frame.configure(padx=20)
        self.notebook.add(tab_3, text="Numbering")

        extension_tab = ScrolledFrameWidget(self.notebook, scrolltype="Vertical")
        self.extensions_tab_frame = extension_tab.create_frame()
        self.notebook.add(extension_tab, text="Extensions")

        # self.numbering_info_frame = Frame(self.misc_frame_numbering)
        # self.numbering_info_frame.grid(row=0)

        # self.main_frame.configure(height='630', width='200')
        self.main_frame.pack(side="top")
        # self.main_frame.pack(expand=False, fill='both')
        self.changes_saved = Label(master=self, text="Changes are not saved", font=('Arial', 10))
        self.focus()
        setting_btn.place(anchor=tkinter.NE, relx=1)

    def display_side_bar(self) -> None:
        ################
        # Sidebar actions and covers
        ################
        self.side_info_frame = Frame(self.main_frame)
        self.side_info_frame.pack(side="left", padx=30, expand=False, fill="both")

        # Action Buttons
        control_frame = Frame(self.side_info_frame)
        control_frame.pack(side="top", fill="both", expand=False, pady=(0, 20))
        btn = ButtonWidget(master=control_frame, text="Open Files", tooltip="Load the metadata and cover to edit them")
        btn.configure(command=self.select_files)
        btn.pack(fill="both", expand=True)
        self.control_widgets.append(btn)
        btn = ButtonWidget(master=control_frame, text="Process", tooltip="Save the metadata and cover changes")
        btn.configure(command=self.pre_process)
        btn.pack(fill="both", expand=True)
        self.control_widgets.append(btn)

        # Show Selected Files - ListBox
        self.files_selected_frame = tkinter.LabelFrame(self.side_info_frame, background="green")

        self.files_selected_frame.selected_files_label = Label(self.files_selected_frame, text="Opened Files:")
        self.files_selected_frame.selected_files_label.pack(expand=False, fill="x", anchor="nw")
        # self.selected_files_treeview = ListboxWidget(self.files_selected_frame, selectmode="multiple")
        self.selected_files_treeview = TreeviewWidget(self.files_selected_frame)
        self.selected_files_treeview.pack(expand=True, fill="both")

        # Selected Covers
        self.image_cover_frame = CoverFrame(self.side_info_frame)

        self.selected_files_treeview.add_hook_item_selected(self.on_file_selection_preview)

        # self.selected_files_treeview.update_cover_image = self.image_cover_frame.update_cover_image
        self.image_cover_frame.pack(expand=False, fill='x')
        self.files_selected_frame.pack(expand=True, fill="both", pady=(20, 0))

        progress_bar_frame = tkinter.Frame(self.side_info_frame)
        self.progress_bar = ProgressBarWidget(progress_bar_frame)
        progress_bar_frame.pack(expand=True, fill="both", side="bottom")

    def display_widgets(self) -> None:

        #################
        # Basic info - first column
        #################
        parent_frame = Frame(self.basic_info_frame, padx=20)
        parent_frame.pack(side="right", expand=True, fill="both")

        self.widget_mngr.Series = ComboBoxWidget(parent_frame, cinfo_name="Series",
                                                 tooltip="The name of the series").pack()
        self.widget_mngr.LocalizedSeries = ComboBoxWidget(parent_frame, cinfo_name="LocalizedSeries",
                                                          label_text="LocalizedSeries",
                                                          tooltip="The translated series name").pack()
        self.widget_mngr.SeriesSort = ComboBoxWidget(parent_frame, cinfo_name="SeriesSort",
                                                     label_text="Series Sort").pack()
        self.widget_mngr.SeriesGroup = ComboBoxWidget(parent_frame, cinfo_name="SeriesGroup",
                                                      label_text="Series Group").pack()

        self.widget_mngr.Title = ComboBoxWidget(parent_frame, cinfo_name="Title",
                                                tooltip="The title of the chapter").pack()
        self.widget_mngr.Summary = LongTextWidget(parent_frame, cinfo_name="Summary").pack()
        self.widget_mngr.Genre = ComboBoxWidget(parent_frame, cinfo_name="Genre").pack()
        self.widget_mngr.Tags = ComboBoxWidget(parent_frame, cinfo_name="Tags").pack()
        self.widget_mngr.Web = ComboBoxWidget(parent_frame, cinfo_name="Web").pack()
        # TODO: add global tag and genre
        self.widget_mngr.StoryArc = ComboBoxWidget(parent_frame, "StoryArc", label_text="Story Arc").pack()
        self.widget_mngr.AlternateSeries = ComboBoxWidget(parent_frame, cinfo_name="AlternateSeries",
                                                          label_text="Alternate Series").pack()

        com_age_rat_frame = Frame(parent_frame)
        com_age_rat_frame.pack(side="top", expand=False, fill="x")
        self.widget_mngr.AgeRating = OptionMenuWidget(com_age_rat_frame, "AgeRating", "Age Rating", 18,
                                                      "Unknown", *comicinfo.AgeRating.list()).pack(expand=True,
                                                                                                   fill="both",
                                                                                                   side="left")

        self.widget_mngr.CommunityRating = ComboBoxWidget(com_age_rat_frame, cinfo_name="CommunityRating",
                                                          label_text="Community Rating",
                                                          validation="rating").pack(expand=True, fill="both",
                                                                                    side="right")

        self.widget_mngr.AlternateCount = ComboBoxWidget(parent_frame, cinfo_name="AlternateCount",
                                                         label_text="Alternate Count",
                                                         default="-1", validation="int", width=20).pack()
        self.widget_mngr.ScanInformation = ComboBoxWidget(parent_frame, cinfo_name="ScanInformation",
                                                          label_text="Scan Information").pack()
        self.widget_mngr.Notes = ComboBoxWidget(parent_frame, cinfo_name="Notes").pack()

        #################
        # People column
        #################
        parent_frame = self.people_info_frame
        self.widget_mngr.Writer = ComboBoxWidget(parent_frame, "Writer").pack()
        self.widget_mngr.Penciller = ComboBoxWidget(parent_frame, "Penciller").pack()
        self.widget_mngr.Inker = ComboBoxWidget(parent_frame, "Inker").pack()
        self.widget_mngr.Colorist = ComboBoxWidget(parent_frame, "Colorist").pack()
        self.widget_mngr.Letterer = ComboBoxWidget(parent_frame, "Letterer").pack()
        self.widget_mngr.CoverArtist = ComboBoxWidget(parent_frame, "CoverArtist").pack()
        self.widget_mngr.Editor = ComboBoxWidget(parent_frame, "Editor").pack()
        self.widget_mngr.Translator = ComboBoxWidget(parent_frame, "Translator").pack()
        self.widget_mngr.Publisher = ComboBoxWidget(parent_frame, "Publisher").pack()
        self.widget_mngr.Imprint = ComboBoxWidget(parent_frame, "Imprint").pack()
        self.widget_mngr.Characters = ComboBoxWidget(parent_frame, "Characters").pack()
        self.widget_mngr.Teams = ComboBoxWidget(parent_frame, "Teams").pack()
        self.widget_mngr.Locations = ComboBoxWidget(parent_frame, "Locations").pack()

        #################
        # Numbering column
        # #################
        parent_frame = self.numbering_info_frame
        combo_width = 10
        self.widget_mngr.Number = ComboBoxWidget(parent_frame, "Number", width=combo_width,
                                                 tooltip="The chapter absolute number").grid(0, 0)
        self.widget_mngr.AlternateNumber = ComboBoxWidget(parent_frame, "AlternateNumber", width=combo_width,
                                                          label_text="Alternate Number", validation="int").grid(0, 1)
        self.widget_mngr.Count = ComboBoxWidget(parent_frame, "Count", width=combo_width,
                                                validation="int", default="-1").grid(1, 0)
        self.widget_mngr.AlternateCount = ComboBoxWidget(parent_frame, "AlternateCount", label_text="Alternate Count",
                                                         width=combo_width,
                                                         validation="int", default="-1").grid(1, 1)
        self.widget_mngr.Volume = ComboBoxWidget(parent_frame, "Volume", width=combo_width,
                                                 validation="int", default="-1").grid(2, 0)
        # self.widget_mngr.PageCount = ComboBoxWidget(parent_frame, "PageCount", label_text="Page Count",
        #                                             width=combo_width,
        #                                             validation="int", default="0").grid(2, 1)
        self.widget_mngr.Year = ComboBoxWidget(parent_frame, "Year", width=combo_width,
                                               validation="int", default="-1").grid(3, 0)
        self.widget_mngr.Month = ComboBoxWidget(parent_frame, "Month", width=combo_width,
                                                validation="int", default="-1").grid(3, 1)
        self.widget_mngr.Day = ComboBoxWidget(parent_frame, "Day", width=combo_width,
                                              validation="int", default="-1").grid(4, 0)
        self.widget_mngr.StoryArcNumber = ComboBoxWidget(parent_frame, "StoryArcNumber", width=combo_width,
                                                         label_text="Story Arc Number").grid(4, 1)
        self.widget_mngr.LanguageISO = ComboBoxWidget(parent_frame, "LanguageISO", label_text="Language ISO",
                                                      width=combo_width,
                                                      ).grid(5, 0)

        format_value_list = ("", "Special", "Reference", "Director's Cut", "Box Set", "Annual", "Anthology", "Epilogue",
                             "One-Shot", "Prologue", "TPB", "Trade Paper Back", "Omnibus", "Compendium", "Absolute",
                             "Graphic Novel", "GN", "FCB")
        self.widget_mngr.Format = OptionMenuWidget(parent_frame, "Format", "Format", 18, "", *format_value_list).grid(5,
                                                                                                                      1)

        self.widget_mngr.BlackAndWhite = OptionMenuWidget(parent_frame, "BlackAndWhite", "Black And White", 18,
                                                          "Unknown", *("Unknown", "Yes", "No")).grid(6, 0)
        self.widget_mngr.Manga = OptionMenuWidget(parent_frame, "Manga", "Manga", 18,
                                                  "Unknown", *("Unknown", "Yes", "No", "YesAndRightToLeft")).grid(6, 1)

    def control_buttons(self, enabled=False) -> None:
        for widget in self.control_widgets:
            widget: tkinter.Button = widget
            if enabled:
                widget.configure(state="normal")
            else:
                widget.configure(state="disabled")

    def on_file_selection_preview(self, *args):
        """
        Method called when the users selects one or more files to previe the metadata
        Called dinamically
        :return:
        """
        new_selection, old_selection = args

        if not self.inserting_files:
            # self._serialize_gui_to_cinfo()  # Sets new_edited_cinfo
            # if not old_selection:
            #     self.merge_changed_metadata(self.selected_items)  # Reads new_edited_cinfo and applies to loaded cinfo
            # else:
            #     # Soft-save current modified data
            #     # Reads new_edited_cinfo and applies to each loaded cinfo
            self.process_gui_update(old_selection, new_selection)
        self.image_cover_frame.update_cover_image(new_selection)

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
        self.update()
        self.progress_bar.increase_processed()

    def on_badzipfile_error(self, exception, file_path: LoadedComicInfo):  # pragma: no cover
        mb.showerror("Error loading file",
                     f"Failed to read the file '{file_path}'.\nThis can be caused by wrong file format"
                     f" or broken file.\n"
                     f"Read the logs for more information.\n"
                     f"Skipping file...")

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.progress_bar.increase_failed()
        mb.showerror("Unhandled exception",
                     "There was an exception that was not handled while writing the changes to the file."
                     "Please check the logs and raise an issue so this can be investigated")

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):  # pragma: no cover
        self.progress_bar.increase_failed()
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
                tag_values.add(loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag) or "")
            tag_values = tuple(tag_values)
            tag_values_len = len(tag_values)

            # All files have the same content for this field

            if tag_values_len == 1:
                widget.set(tag_values[0])

            # Multiple values across different files for this field
            elif tag_values_len > 1:
                # Append "multiple_values" string to the suggestion listbox
                tag_values = (self.MULTIPLE_VALUES_CONFLICT,) + tag_values
                widget.widget.set(self.MULTIPLE_VALUES_CONFLICT)

            # If it's a combobox update the suggestions listbox with the loaded values
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = list(tag_values)

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
                    self.log.debug(LOG_TAG + f"Omitting {cinfo_tag}. Keeping original")
                    self.new_edited_cinfo.set_attr_by_name(cinfo_tag,self.MULTIPLE_VALUES_CONFLICT)
                case "None":
                    if widget.name == "Format":
                        self.new_edited_cinfo.set_attr_by_name(cinfo_tag, "")
                case widget.default:  # If it matches the default then do nothing
                    self.log.debug(LOG_TAG + f"Omitting {cinfo_tag}.")
                    pass
                case _:
                    self.new_edited_cinfo.set_attr_by_name(cinfo_tag,widget_value)
                    self.log.info(LOG_TAG + f"Tag '{cinfo_tag}' has overwritten content: '{widget_value}'")
                    # self.log.warning(f"Unhandled case: {widget_value}")
                    pass

    def process_gui_update(self, old_selection: list[LoadedComicInfo], new_selection: list[LoadedComicInfo]):
        self._serialize_gui_to_cinfo()
        unsaved_changes = self.merge_changed_metadata(old_selection)

        self.show_not_saved_indicator(old_selection, mark_saved=not unsaved_changes)
        self.widget_mngr.clean_widgets()
        # Display new selection data
        self._serialize_cinfolist_to_gui(new_selection)

    def pre_process(self) -> None:
        """
        Handles UI stuff to be started prior to processing such as converting ui data to comicinfo and starting the timer
        """
        if not self.selected_files_path:
            raise NoFilesSelected()
        self.control_buttons(enabled=False)
        self.changes_saved.place_forget()
        # self.loaded_cinfo_list_to_process = self.get_selected_loaded_cinfo_list()
        self.progress_bar.start(len(self.loaded_cinfo_list))
        # Make sure current view is saved:
        # self._serialize_gui_to_cinfo()
        # self.merge_changed_metadata(self.selected_files_path)
        self.process_gui_update(self.selected_items,self.selected_items)
        try:
            # self._serialize_gui_to_cinfo()
            # self.merge_changed_metadata(self.loaded_cinfo_list)
            self.process()
        finally:
            self.progress_bar.stop()
        self.new_edited_cinfo = None  # Nulling value to be safe
        self.control_buttons(enabled=True)

class _ProcessingModule(App):
    ...



