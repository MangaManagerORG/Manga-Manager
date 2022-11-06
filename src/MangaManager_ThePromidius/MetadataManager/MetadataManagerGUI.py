from __future__ import annotations

import logging
import os
import tkinter
from tkinter import Tk, Button, Frame, Label, Listbox, messagebox as mb, ttk

from src.MangaManager_ThePromidius.Common.utils import get_platform

if get_platform() == "linux":
    from src.MangaManager_ThePromidius.Common.GUI.FileChooserWindow import askopenfiles
else:
    from tkinter.filedialog import askopenfiles

from PIL import ImageTk, Image

from src.MangaManager_ThePromidius.MetadataManager import comicinfo
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib
from src.MangaManager_ThePromidius.MetadataManager.cbz_handler import LoadedComicInfo
from src.MangaManager_ThePromidius.Common.GUI.widgets import ComboBoxWidget, LongTextWidget, OptionMenuWidget, \
    ScrolledFrameWidget, WidgetManager




class App(Tk, MetadataManagerLib):
    main_frame: Frame

    def __init__(self):
        super(App, self).__init__()
        # super(MetadataManagerLib, self).__init__()

        self.widget_mngr = WidgetManager()
        self.selected_files_path = None
        self.loaded_cinfo_list = None
        self.cinfo_tags = list[str]()
        style = ttk.Style()
        current_theme = style.theme_use()
        style.theme_settings(current_theme, {"TNotebook.Tab": {"configure": {"padding": [20, 5],
                                                                             "font": ('Arial', 20)}}})

        self.log = logging.getLogger("MetadataManager.GUI")
        self._initialize_frames()
        self.display_widgets()

        self.side_info_frame = Frame(self.main_frame)
        self.side_info_frame.pack(side="left", anchor="nw")
        #################
        # Action Buttons
        #################
        self.control_frame = Frame(self.side_info_frame)
        btn = Button(self.control_frame, text="Load_data")
        btn.configure(command=self.load_data)
        btn.pack(fill="both", expand=True)
        btn = Button(self.control_frame, text="Load Files")
        btn.configure(command=self.select_files)
        btn.pack(fill="both", expand=True)

        btn = Button(self.control_frame, text="Process")
        btn.configure(command=self.pre_process)
        btn.pack(fill="both", expand=True)
        self.control_frame.pack(side="bottom", fill="both", expand=True)  # side="bottom")

        #################
        # Show Selected Files - ListBox
        #################
        self.files_selected_frame = Frame(self.side_info_frame)
        self.files_selected_frame.selected_files_label = Label(self.files_selected_frame, text="Selected Files:",
                                                               pady="10")
        self.files_selected_frame.selected_files_label.pack()
        self.files_selected_frame.listbox = Listbox(self.files_selected_frame)
        self.files_selected_frame.listbox.pack(expand=True, fill="both", anchor="center")

        # self.files_selected_frame.grid(row=1, column=0, sticky="wesn")
        self.files_selected_frame.pack(expand=True, fill="both")
        # self.files_selected_frame.pack()

        self.image_cover_frame = Frame(self.side_info_frame)

        # Create a photoimage object of the image in the path

        self.test_label1 = tkinter.Label(self.image_cover_frame)
        self.test_label1.pack()
        # self.image_cover_frame.grid(row=2, column=0, sticky="wesn")
        self.image_cover_frame.pack(expand=True, fill="both")

        # Important:
        self.cinfo_tags = self.widget_mngr.get_tags()
        # print(self.widget_mngr.get_tags())

    def _initialize_frames(self):
        self.main_frame = Frame(self)
        self.main_frame.configure(bg="blue", borderwidth=2)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side="right", expand=True, fill="both")

        tab_1 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.basic_info_frame = tab_1.create_frame()
        tab_2 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.people_info_frame = tab_2.create_frame()
        tab_3 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.misc_frame_numbering = tab_3.create_frame()

        self.numbering_info_frame = Frame(self.misc_frame_numbering)
        self.numbering_info_frame.grid(row=0)
        # #################º
        # # Show Selected Files
        # #################
        # self.files_selected_frame = Frame(self.misc_frame_numbering)
        # self.files_selected_frame.selected_files_label = Label(self.files_selected_frame, text="Selected Files:",
        #                                                        pady="10")
        # self.files_selected_frame.selected_files_label.pack()
        # self.files_selected_frame.listbox = Listbox(self.files_selected_frame)
        # self.files_selected_frame.listbox.pack(expand=True, fill="both", anchor="center")
        # self.files_selected_frame.grid(row=1, column=0, sticky="wesn")

        self.notebook.add(tab_1, text="Basic Info")
        self.notebook.add(tab_2, text="People Info")
        self.notebook.add(tab_3, text="Numbering")
        self.main_frame.configure(height='600', width='200')
        self.main_frame.pack(anchor='center', expand=True, fill='both', side='top')
        self.focus()

    def select_files(self):
        # New file selection. Proceed to clean the ui to a new state
        self.widget_mngr.clean_widgets()
        self.selected_files_path = list()
        self.files_selected_frame.listbox.delete(0, tkinter.END)
        self.last_folder = ""
        self.settings = {}

        # These are some tricks to make it easier to select files.
        # Saves last opened folder to not have to browse to it again
        if not self.last_folder:
            initial_dir = self.settings.get("library_folder_path")
        else:
            initial_dir = self.last_folder
        self.log.debug("Selecting files")
        # Open select files dialog
        selected_paths_list = askopenfiles(parent=self.master, initialdir=initial_dir,
                                           title="Select file to apply cover",
                                           filetypes=(("CBZ Files", ".cbz"),("All Files", "*"),)
                                           # ("Zip files", ".zip"))
                                           )
        if selected_paths_list:
            selected_parent_folder = os.path.dirname(selected_paths_list[0].name)
            if self.last_folder != selected_parent_folder or not self.last_folder:
                self.last_folder = selected_parent_folder
        self.selected_files_path = [file.name for file in selected_paths_list]

        self.log.debug(f"Selected files [{', '.join(self.selected_files_path)}]")
        self.load_cinfo_list()
        for loadedinfo in self.loaded_cinfo_list:
            self.files_selected_frame.listbox.insert(0, os.path.basename(loadedinfo.file_path))

        self.serialize_cinfolist_to_gui()

    def display_widgets(self):

        #################
        # Basic info - first column
        #################
        parent_frame = self.basic_info_frame
        self.widget_mngr.Title = ComboBoxWidget(parent_frame, cinfo_name="Title").pack()
        self.widget_mngr.Series = ComboBoxWidget(parent_frame, cinfo_name="Series").pack()
        self.widget_mngr.LocalizedSeries = ComboBoxWidget(parent_frame, cinfo_name="LocalizedSeries",
                                                          label_text="LocalizedSeries").pack()
        self.widget_mngr.SeriesSort = ComboBoxWidget(parent_frame, cinfo_name="SeriesSort",
                                                     label_text="Series Sort").pack()
        self.widget_mngr.Summary = LongTextWidget(parent_frame, cinfo_name="Summary")
        self.widget_mngr.Genre = ComboBoxWidget(parent_frame, cinfo_name="Genre").pack()
        self.widget_mngr.Tags = ComboBoxWidget(parent_frame, cinfo_name="Tags").pack()
        # TODO: add global tag and genre
        self.widget_mngr.AlternateSeries = ComboBoxWidget(parent_frame, cinfo_name="AlternateSeries",
                                                          label_text="Alternate Series").pack()
        self.widget_mngr.Notes = ComboBoxWidget(parent_frame, cinfo_name="Notes").pack()
        self.widget_mngr.AgeRating = OptionMenuWidget(parent_frame, "AgeRating", "Age Rating",
                                                      "Unknown", *comicinfo.AgeRating.list())
        self.widget_mngr.CommunityRating = ComboBoxWidget(parent_frame, cinfo_name="CommunityRating",
                                                          label_text="Community Rating",
                                                          validation="rating").pack()
        self.widget_mngr.ScanInformation = ComboBoxWidget(parent_frame, cinfo_name="ScanInformation",
                                                          label_text="Scan Information").pack()
        self.widget_mngr.StoryArc = ComboBoxWidget(parent_frame, "StoryArc", label_text="Story Arc").pack()

        self.widget_mngr.AlternateCount = ComboBoxWidget(parent_frame, cinfo_name="AlternateCount",
                                                         label_text="Alternate Count",
                                                         default="-1", validation="int", width=20)

        #################
        # People column
        #################
        parent_frame = self.people_info_frame
        self.widget_mngr.Writer = ComboBoxWidget(parent_frame, "Writer").pack()
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
        self.widget_mngr.Number = ComboBoxWidget(parent_frame, "Number", width=combo_width).grid(0, 0)
        self.widget_mngr.AlternateNumber = ComboBoxWidget(parent_frame, "AlternateNumber", width=combo_width,
                                                          label_text="Alternate Number", validation="int").grid(0, 1)
        self.widget_mngr.Count = ComboBoxWidget(parent_frame, "Count", width=combo_width,
                                                validation="int", default="-1").grid(1, 0)
        self.widget_mngr.AlternateCount = ComboBoxWidget(parent_frame, "AlternateCount", label_text="Alternate Count",
                                                         width=combo_width,
                                                         validation="int", default="-1").grid(1, 1)
        self.widget_mngr.Volume = ComboBoxWidget(parent_frame, "Volume", width=combo_width,
                                                 validation="int", default="-1").grid(2, 0)
        self.widget_mngr.PageCount = ComboBoxWidget(parent_frame, "PageCount", label_text="Page Count",
                                                    width=combo_width,
                                                    validation="int", default="0").grid(2, 1)
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

        format_value_list = ("Special", "Reference", "Director's Cut", "Box Set", "Annual", "Anthology", "Epilogue",
                             "One-Shot", "Prologue", "TPB", "Trade Paper Back", "Omnibus", "Compendium", "Absolute",
                             "Graphic Novel", "GN", "FCB")
        self.widget_mngr.Format = ComboBoxWidget(parent_frame, "Format", default_values=format_value_list,
                                                 width=combo_width,
                                                 ).grid(5, 1)

        self.widget_mngr.BlackAndWhite = OptionMenuWidget(parent_frame, "BlackAndWhite", "Black And White",
                                                          "Unknown", *("Unknown", "Yes", "No")).grid(6, 0)
        self.widget_mngr.Manga = OptionMenuWidget(parent_frame, "Manga", "Manga",
                                                  "Unknown", *("Unknown", "Yes", "No", "YesAndRightToLeft")).grid(6, 1)

    def serialize_cinfolist_to_gui(self):

        for loaded_cinfo in self.loaded_cinfo_list:
            if loaded_cinfo.cover_filename:
                image1 = Image.open(loaded_cinfo.get_cover_image_bytes()).resize((190, 260), Image.ANTIALIAS)
                self.test_image = ImageTk.PhotoImage(image1)
                self.test_label1.configure(image=self.test_image)
            for cinfo_tag in self.widget_mngr.get_tags():
                cinfo_field_value = str(loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag))
                widget = self.widget_mngr.get_widget(cinfo_tag)

                if isinstance(widget, ComboBoxWidget):
                    default_value = widget.default
                    if not widget.widget['values']:
                        if not cinfo_field_value:
                            widget.widget['values'] = (default_value,)
                        else:
                            widget.widget['values'] = (cinfo_field_value,)
                        widget.set(cinfo_field_value)

                    list_of_values = list(widget.widget['values'])
                    if cinfo_field_value not in list_of_values:
                        list_of_values.append(cinfo_field_value)
                    if len(list_of_values) > 1:
                        if self.multiple_values_conflict not in list_of_values:
                            list_of_values = [self.multiple_values_conflict] + list_of_values
                        widget.widget.set(self.multiple_values_conflict)
                    widget.widget['values'] = list_of_values
                    # widget['values'] = ["Value_a", "Valueb",widget_name]
                elif isinstance(widget, LongTextWidget):
                    if widget.get():
                        widget.set(self.multiple_values_conflict)

                    else:
                        widget.set(cinfo_field_value)

    def pre_process(self):
        self.serialize_gui_to_edited_cinfo()
        self.proces()
        self.new_edited_cinfo = None  # Nulling value to be safe

    def serialize_gui_to_edited_cinfo(self):
        new_cinfo = self.new_edited_cinfo = comicinfo.ComicInfo()
        for cinfo_tag in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cinfo_tag)
            if widget.get() != widget.default and widget.get():
                new_cinfo.set_attr_by_name(cinfo_tag, self.widget_mngr.get_widget(cinfo_tag).get())

    def load_data(self):
        self.widget_mngr.clean_widgets()
        for cin_widget in self.widget_mngr.get_tags():
            widget = self.widget_mngr.get_widget(cin_widget)
            widget.set(cin_widget)

    # Errors handling implementations
    def on_badzipfile_error(self, exception, file_path: LoadedComicInfo):
        mb.showerror("Error loading file",
                     f"Failed to read the file '{file_path}'.\nThis can be caused by wrong file format"
                     f" or broken file.\n"
                     f"Read the logs for more information.\n"
                     f"Skipping file...")

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):
        mb.showerror("Unhandled exception",
                     "There was an exception that was not handled while writing the changes to the file."
                     "Please check the logs and raise an issue so this can be investigated")

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):
        mb.showerror("Error writing to file",
                     "There was an error writing to the file. Please check the logs.")

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):
        mb.showwarning(f"Error reading the metadata from file",
                       f"Failed to read metadata from '{loaded_info.file_path}'\n"
                       "The file data couldn't be parsed probably because of corrupted data or bad format.\n"
                       f"Recovery was attempted and failed.\nCreating new metadata object...")

if __name__ == '__main__':
    app = App()

    app.mainloop()
