import os
import tkinter
from tkinter import Frame
from tkinter.ttk import Notebook

from src.MetadataManager.GUI.widgets import ComboBoxWidget, LongTextWidget, OptionMenuWidget
from src.MetadataManager.GUI.widgets import ScrolledFrameWidget, ButtonWidget, TreeviewWidget, CoverFrame, ProgressBarWidget
from src.Common.utils import open_folder
from src.MetadataManager import comicinfo
from src.MetadataManager.MetadataManagerGUI import GUIApp


class Layout(GUIApp):
    name = "default"

    def __init__(self):
        super().__init__()
        self._initialize_frames()
        self.display_side_bar()
        self.display_widgets()
        self.display_extensions(self.extensions_tab_frame)

    #########################################################
    # GUI Display Methods
    ############

    def _initialize_frames(self) -> None:
        # MENU

        self.notebook = Notebook(self.main_frame)
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
        self.changes_saved = tkinter.Label(master=self, text="Changes are not saved", font=('Arial', 10))
        self.focus()

    def display_side_bar(self) -> None:
        ################
        # Sidebar actions and covers
        ################
        self.side_info_frame = Frame(self.main_frame)
        self.side_info_frame.pack(side="left", padx=30, expand=False, fill="both")

        # Action Buttons
        control_frame = Frame(self.side_info_frame)
        control_frame.pack(side="top", fill="both", expand=False, pady=(0, 20))
        btn = ButtonWidget(master=control_frame, text="Open Files",
                           tooltip="Load the metadata and cover to edit them")
        btn.configure(command=self.select_files)
        btn.pack(fill="both", expand=True)
        self.control_widgets.append(btn)
        btn = ButtonWidget(master=control_frame, text="Process", tooltip="Save the metadata and cover changes")
        btn.configure(command=self.pre_process)
        btn.pack(fill="both", expand=True)
        self.control_widgets.append(btn)

        # Show Selected Files - ListBox
        self.files_selected_frame = tkinter.LabelFrame(self.side_info_frame)

        self.files_selected_frame.selected_files_label = tkinter.Label(self.files_selected_frame, text="Opened Files:")
        self.files_selected_frame.selected_files_label.pack(expand=False, fill="x")
        # self.selected_files_treeview = ListboxWidget(self.files_selected_frame, selectmode="multiple")
        self.selected_files_treeview = TreeviewWidget
        self.selected_files_treeview.open_in_explorer = self._treeview_open_explorer
        self.selected_files_treeview.reset_loadedcinfo_changes = self._treview_reset
        self.selected_files_treeview = self.selected_files_treeview(self.files_selected_frame)
        self.selected_files_treeview.pack(expand=True, fill="both")
        # Selected Covers
        self.image_cover_frame = CoverFrame(self.side_info_frame)

        self.selected_files_treeview.add_hook_item_selected(self.on_file_selection_preview)

        # self.selected_files_treview.update_cover_image = self.image_cover_frame.update_cover_image TODO:this is commented check if needed. Levaing it as it is in merge
        self.image_cover_frame.pack(expand=False, fill='x')
        self.files_selected_frame.pack(expand=True, fill="both", pady=(20, 0))

        progress_bar_frame = tkinter.Frame(self.side_info_frame)
        self.pb = ProgressBarWidget(progress_bar_frame)
        progress_bar_frame.pack(expand=False, fill="both", side="bottom")

    def _treeview_open_explorer(self, file):
        open_folder(os.path.dirname(file), file)
        ...

    def _treview_reset(self, event=None):
        ...

    def display_widgets(self) -> None:

        #################
        # Basic info - first column
        #################
        parent_frame = Frame(self.basic_info_frame, padx=20)
        parent_frame.pack(side="right", expand=True, fill="both")

        frame = Frame(parent_frame)
        frame.pack(fill="both", side="top")
        self.widget_mngr.Series = ComboBoxWidget(frame, cinfo_name="Series",
                                                 tooltip="The name of the series").pack(side="left", expand=True,
                                                                                        fill="x")
        frame = Frame(frame)
        frame.pack(side="right")
        tkinter.Label(frame).pack(side="top")  # Dummy label so button is centered
        ButtonWidget(master=frame, text="⋯", tooltip="If one file selected, load the filename",
                     command=self._fill_filename).pack(side="bottom")

        self.widget_mngr.LocalizedSeries = ComboBoxWidget(parent_frame, cinfo_name="LocalizedSeries",
                                                          label_text="LocalizedSeries",
                                                          tooltip="The translated series name").pack()
        self.widget_mngr.SeriesSort = ComboBoxWidget(parent_frame, cinfo_name="SeriesSort",
                                                     label_text="Series Sort").pack()
        self.widget_mngr.SeriesGroup = ComboBoxWidget(parent_frame, cinfo_name="SeriesGroup",
                                                      label_text="Series Group").pack()

        self.widget_mngr.Title = ComboBoxWidget(parent_frame, cinfo_name="Title",
                                                tooltip="The title of the chapter").pack()

        long_text_notebook = Notebook(parent_frame, height=100)
        long_text_notebook.pack(fill="x",expand=False)

        tab = ScrolledFrameWidget(long_text_notebook, scrolltype="vertical")
        summary_frame = tab.create_frame(fill="both",expand=True)
        long_text_notebook.add(tab, text="Summary")
        self.widget_mngr.Summary = LongTextWidget(summary_frame, cinfo_name="Summary",label_text="").pack()

        tab = ScrolledFrameWidget(long_text_notebook, scrolltype="vertical")
        review_frame = tab.create_frame()
        long_text_notebook.add(tab, text="Review")
        self.widget_mngr.Review = LongTextWidget(review_frame, cinfo_name="Review", label_text="").pack()

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
                                                      "Unknown", comicinfo.AgeRating.list()).pack(expand=True,
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
        self.widget_mngr.MainCharacterOrTeam = ComboBoxWidget(parent_frame, "MainCharacterOrTeam",
                                                              label_text="Main Character Or Team").pack()


        #################
        # Numbering column
        # #################
        parent_frame = self.numbering_info_frame
        combo_width = 10
        self.widget_mngr.Number = ComboBoxWidget(parent_frame, "Number", width=combo_width,
                                                 tooltip="The chapter absolute number").grid(0, 0)
        self.widget_mngr.AlternateNumber = ComboBoxWidget(parent_frame, "AlternateNumber", width=combo_width,
                                                          label_text="Alternate Number", validation="int").grid(0,
                                                                                                                1)
        self.widget_mngr.Count = ComboBoxWidget(parent_frame, "Count", width=combo_width,
                                                validation="int", default="-1").grid(1, 0)
        self.widget_mngr.AlternateCount = ComboBoxWidget(parent_frame, "AlternateCount",
                                                         label_text="Alternate Count",
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

        self.widget_mngr.Format = OptionMenuWidget(parent_frame, "Format", "Format", 18, "",
                                                   comicinfo.format_list).grid(5, 1)

        self.widget_mngr.BlackAndWhite = OptionMenuWidget(parent_frame, "BlackAndWhite", "Black And White", 18,
                                                          "Unknown", ("Unknown", "Yes", "No")).grid(6, 0)
        self.widget_mngr.Manga = OptionMenuWidget(parent_frame, "Manga", "Manga", 18,
                                                  "Unknown", ("Unknown", "Yes", "No", "YesAndRightToLeft")).grid(6,
                                                                                                                  1)

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
