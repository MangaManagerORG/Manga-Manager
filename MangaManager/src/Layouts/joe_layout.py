import json
import tkinter
from tkinter import Frame, ttk
from tkinter.ttk import Notebook

from common.models import Formats, AgeRating
from src.Common import ResourceLoader
from src.MetadataManager.CoverManager.CoverManager import CoverManager
from src.MetadataManager.GUI.ExceptionWindow import ExceptionFrame
from src.MetadataManager.GUI.widgets import ScrolledFrameWidget, ButtonWidget, FileMultiSelectWidget, ProgressBarWidget, \
    ComboBoxWidget, LongTextWidget, OptionMenuWidget
from src.MetadataManager.GUI.widgets.CanvasCoverWidget import CoverFrame
from src.MetadataManager.MetadataManagerGUI import GUIApp

f = open(ResourceLoader.get('languages.json'), 'r')
data = json.loads(f.read())
languages = [l["isoCode"] for l in data]
f.close()


class Layout(GUIApp):
    name = "joe"

    def __init__(self):
        super().__init__()
        self.title("Manga Manager: Joe Layout")

    #########################################################
    # GUI Display Methods
    ############

        # Overview LAYOUT
        self.control_frame_top = Frame(self.main_frame)
        self.control_frame_top.pack(fill="x", side="top",padx=30,pady=3)
        self.display_control_frame()
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill="x")

        mid_content_frame = Frame(self.main_frame)
        mid_content_frame.pack(fill="both", expand=True)
        self.file_selection_frame_left = Frame(mid_content_frame)
        self.file_selection_frame_left.pack(side="left", padx=30, expand=False, fill="both")
        self.display_side_bar()

        self.main_content_frame_right = Frame(mid_content_frame,pady=10)
        self.main_content_frame_right.pack(fill="both", side="right", expand=True, padx=(0, 20))
        self.init_main_content_frame()
        self.display_main_content_widgets()

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill="x")
        self.selection_progress_frame_bottom = Frame(self.main_frame)
        self.selection_progress_frame_bottom.pack(fill="x", side="bottom", pady=(5, 2))
        self.display_bottom_frame()

    def display_side_bar(self) -> None:
        ################
        # Sidebar actions and covers
        ################
        self.side_info_frame = self.file_selection_frame_left

        # Show Selected Files - ListBox
        self.files_selected_frame = tkinter.LabelFrame(self.side_info_frame)

        self.files_selected_frame.selected_files_label = tkinter.Label(self.files_selected_frame, text="Opened Files:")
        self.files_selected_frame.selected_files_label.pack(expand=False, fill="x")
        self.selected_files_treeview = FileMultiSelectWidget
        self.selected_files_treeview.open_in_explorer = self._treeview_open_explorer
        self.selected_files_treeview.reset_loadedcinfo_changes = self._treview_reset
        self.selected_files_treeview = self.selected_files_treeview(self.files_selected_frame)#, padding=[-15, 0, 0, 0])  # padding -15 to remove the left indent
        self.selected_files_treeview.pack(expand=True, fill="both")
        # Selected Covers
        self.image_cover_frame = CoverFrame(self.side_info_frame)

        self.selected_files_treeview.add_hook_item_selected(self.on_file_selection_preview)

        # self.selected_files_treview.update_cover_image = self.image_cover_frame.update_cover_image TODO:this is commented check if needed. Levaing it as it is in merge
        self.image_cover_frame.pack(expand=False, fill='x')
        self.files_selected_frame.pack(expand=True, fill="both", pady=(20, 0))

    def display_control_frame(self) -> None:
        # Action Buttons
        control_frame = self.control_frame_top

        btn = ButtonWidget(master=control_frame, text="Open Files",
                           tooltip="Load the metadata and cover to edit them (Ctrl+O)")
        try:
            icon_path = ResourceLoader.get('open_file.png')
            btn.img_ref = tkinter.PhotoImage(name="open_file_icon", master=btn, file=icon_path)
            btn.configure(image=btn.img_ref)
        except: # Fixme linux throws resource not found
            self.log.exception("Exception loading the open_file icon")
        btn.configure(compound="left")
        btn.configure(command=self.select_files)
        btn.pack(side="left", fill="y", padx=(0,5))
        self.control_mngr.append(btn)

        btn = ButtonWidget(master=control_frame, text="Open Folder")
        try:
            icon_path = ResourceLoader.get('open_folder.png')
            btn.img_ref = tkinter.PhotoImage(name="open_folder_icon", master=btn, file=icon_path)
            btn.configure(image=btn.img_ref)
        except:
            self.log.exception("Exception loading the open_file icon")
        btn.configure(compound="left")
        btn.configure(command=self.select_folder)
        btn.pack(side="left", fill="y", padx=5)
        self.control_mngr.append(btn)

        btn = ButtonWidget(master=control_frame, text="Clear", tooltip="Clean the metadata from the current view")
        btn.configure(command=self.widget_mngr.clean_widgets)
        btn.configure(image=self.clear_icon)
        btn.configure(compound="left", padx=5)

        btn.pack(side="left", fill="y")
        self.control_mngr.append(btn)

        btn = ButtonWidget(master=control_frame, text="  Fetch\n  Online")
        btn.configure(image=self.fetch_online_icon)
        btn.configure(compound="left")
        btn.configure(command=self.process_fetch_online)
        btn.pack(side="left", fill="y", padx=5)
        self.control_mngr.append(btn)

        btn = ButtonWidget(master=control_frame, text="Process", tooltip="Save the metadata and cover changes (Ctrl+S)")
        btn.configure(command=self.pre_process)
        btn.configure(image=self.save_icon)
        btn.configure(compound="left")
        btn.pack(side="left",fill="y", padx=5)
        self.control_mngr.append(btn)

        btn = ButtonWidget(master=control_frame, text="Cover Manager", tooltip="Opens covermanager for the loaded files")
        btn.configure(command=lambda: CoverManager(self, self))
        btn.pack(side="left", fill="y",padx=(20,0))
        self.control_mngr.append(btn)

    def init_main_content_frame(self) -> None:
        self.notebook = Notebook(self.main_content_frame_right)
        self.notebook.pack(expand=True, fill="both")

        tab_1 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.basic_info_frame = tab_1.create_frame()

        self.notebook.add(tab_1, text="Basic Info")

        tab_2 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.people_info_frame = tab_2.create_frame()
        # self.people_info_frame.configure(padx=20)
        self.notebook.add(tab_2, text="People Info")

        tab_3 = ScrolledFrameWidget(self.notebook, scrolltype="vertical")
        self.numbering_info_frame = tab_3.create_frame()
        # self.numbering_info_frame.configure(padx=20)
        self.notebook.add(tab_3, text="Extended")

        extension_tab = ScrolledFrameWidget(self.notebook, scrolltype="Vertical")
        self.extensions_tab_frame = extension_tab.create_frame()
        self.notebook.add(extension_tab, text="Extensions")

        errors_tab = ScrolledFrameWidget(self.notebook, scrolltype="Vertical")
        errors_tab.pack(fill="both",expand=True)
        errors_tab.paned_window.pack(fill="both",expand=True)
        self.errors_tab_frame = errors_tab.create_frame(fill="both",expand=True)
        self.notebook.add(errors_tab, text="Errors")
        ExceptionFrame(master=self.errors_tab_frame,is_test=self.is_test).pack(fill="both",expand=True)

        self.display_extensions(self.extensions_tab_frame)



        self.changes_saved = tkinter.Label(master=self, text="Changes are not saved", font=('Arial', 10))
        self.focus()
        self.log.warning("warn test")
        self.log.error("error test")

    def display_main_content_widgets(self) -> None:

        #################
        # Basic info - first column
        #################
        parent_frame = Frame(self.basic_info_frame, padx=20)
        parent_frame.pack(side="right", expand=True, fill="both")
        frame = Frame(parent_frame)
        frame.pack(fill="both", side="top")
        label = tkinter.Label(frame,text="Series")
        label.pack(fill="x",expand=False,side="top")
        self.widget_mngr.Series = ComboBoxWidget(frame, cinfo_name="Series", label_text="",
                                                 tooltip="The name of the series").pack(side="left", expand=True,
                                                                                        fill="x")
        self.widget_mngr.Series.label = label
        btn = ButtonWidget(master=frame, text="⋯", tooltip="If one file selected, load the filename",
                     command=self._fill_filename)
        btn.pack(side="right")
        self.control_mngr.append(btn)
        btn = ButtonWidget(master=frame, text="⋯F", tooltip="If one file selected, load the FOLDER name",
                     command=self._fill_foldername)
        btn.pack(side="right")
        self.control_mngr.append(btn)
        self.widget_mngr.LocalizedSeries = ComboBoxWidget(parent_frame, cinfo_name="LocalizedSeries",
                                                          label_text="LocalizedSeries",
                                                          tooltip="The translated series name").pack()
        self.widget_mngr.SeriesSort = ComboBoxWidget(parent_frame, cinfo_name="SeriesSort",
                                                     label_text="Series Sort").pack()

        self.widget_mngr.Title = ComboBoxWidget(parent_frame, cinfo_name="Title",
                                                tooltip="The title of the chapter").pack()

        # Summary and Review widget
        long_text_notebook = Notebook(parent_frame, height=95)
        long_text_notebook.pack(fill="x", expand=False, pady=(14, 5))

        tab = ScrolledFrameWidget(long_text_notebook, scrolltype="vertical")
        summary_frame = tab.create_frame(fill="both", expand=True)
        long_text_notebook.add(tab, text="Summary")
        self.widget_mngr.Summary = LongTextWidget(summary_frame, cinfo_name="Summary", label_text="").pack(fill="both",
                                                                                                           expand="True")

        tab = ScrolledFrameWidget(long_text_notebook, scrolltype="vertical",)
        review_frame = tab.create_frame(fill="both",expand=True)
        long_text_notebook.add(tab, text="Review")
        self.widget_mngr.Review = LongTextWidget(review_frame, cinfo_name="Review", label_text="").pack(fill="both",
                                                                                                        expand="True")

        self.widget_mngr.Genre = ComboBoxWidget(parent_frame, cinfo_name="Genre").pack()
        self.widget_mngr.Tags = ComboBoxWidget(parent_frame, cinfo_name="Tags").pack()
        self.widget_mngr.Web = ComboBoxWidget(parent_frame, cinfo_name="Web").pack()

        COMBO_WIDTH = 17
        numbering = Frame(parent_frame)
        numbering.columnconfigure("all", weight=0)
        numbering.pack(fill="both", expand=True)

        self.widget_mngr.Number = ComboBoxWidget(numbering, "Number", width=COMBO_WIDTH,
                                                 tooltip="The chapter absolute number").grid(0, 0)
        self.widget_mngr.Volume = ComboBoxWidget(numbering, "Volume", width=COMBO_WIDTH,
                                                 validation="int", default="-1").grid(0, 1)

        self.widget_mngr.Count = ComboBoxWidget(numbering, "Count", width=COMBO_WIDTH,
                                                validation="int", default="-1").grid(0, 2)
        self.widget_mngr.Format = OptionMenuWidget(numbering, "Format", "Format", COMBO_WIDTH, 18, "",
                                                   Formats).grid(0, 3)
        self.widget_mngr.Manga = OptionMenuWidget(numbering, "Manga", "Manga", COMBO_WIDTH, 18,
                                                  "Unknown", ("Unknown", "Yes", "No", "YesAndRightToLeft")).grid(0,4)

        self.widget_mngr.Year = ComboBoxWidget(numbering, "Year", width=COMBO_WIDTH,
                                               validation="int", default="-1").grid(1, 0)
        self.widget_mngr.Month = ComboBoxWidget(numbering, "Month", width=COMBO_WIDTH,
                                                validation="int", default="-1").grid(1, 1)
        self.widget_mngr.Day = ComboBoxWidget(numbering, "Day", width=COMBO_WIDTH,
                                              validation="int", default="-1").grid(1, 2)
        self.widget_mngr.AgeRating = OptionMenuWidget(numbering, "AgeRating", "Age Rating", COMBO_WIDTH, 18,
                                                      "Unknown", AgeRating.list()).grid(1, 3)

        self.widget_mngr.LanguageISO = ComboBoxWidget(numbering, "LanguageISO", label_text="Language ISO",
                                                      width=8, default="", default_values=languages).grid(1, 4)

        self.widget_mngr.Notes = ComboBoxWidget(parent_frame, cinfo_name="Notes").pack()

        #################
        # People column
        #################
        parent_frame = Frame(self.people_info_frame, padx=20)
        parent_frame.pack(side="right", expand=True, fill="both")
        self.widget_mngr.Writer = ComboBoxWidget(parent_frame, "Writer").pack()
        self.widget_mngr.Penciller = ComboBoxWidget(parent_frame, "Penciller").pack()
        self.widget_mngr.Inker = ComboBoxWidget(parent_frame, "Inker").pack()
        self.widget_mngr.Colorist = ComboBoxWidget(parent_frame, "Colorist").pack()
        self.widget_mngr.Letterer = ComboBoxWidget(parent_frame, "Letterer").pack()
        self.widget_mngr.CoverArtist = ComboBoxWidget(parent_frame, "CoverArtist", label_text="Cover Artist").pack()
        self.widget_mngr.Editor = ComboBoxWidget(parent_frame, "Editor").pack()
        self.widget_mngr.Translator = ComboBoxWidget(parent_frame, "Translator").pack()
        self.widget_mngr.Publisher = ComboBoxWidget(parent_frame, "Publisher").pack()
        self.widget_mngr.Imprint = ComboBoxWidget(parent_frame, "Imprint").pack()
        self.widget_mngr.Characters = ComboBoxWidget(parent_frame, "Characters").pack()
        self.widget_mngr.Teams = ComboBoxWidget(parent_frame, "Teams").pack()
        self.widget_mngr.Locations = ComboBoxWidget(parent_frame, "Locations").pack()
        self.widget_mngr.MainCharacterOrTeam = ComboBoxWidget(parent_frame, "MainCharacterOrTeam",
                                                              label_text="Main Character Or Team").pack()
        self.widget_mngr.Other = ComboBoxWidget(parent_frame, "Other").pack()

        #################
        # Numbering column
        # #################
        # parent_frame = Frame(self.numbering_info_frame, padx=20)
        # parent_frame.pack(side="right", expand=False, fill="both")
        parent_frame = Frame(self.numbering_info_frame,padx=20)
        parent_frame.pack(side="right", expand=True, fill="both")

        self.widget_mngr.SeriesGroup = ComboBoxWidget(parent_frame, cinfo_name="SeriesGroup",
                                                      label_text="Series Group").pack()

        self.widget_mngr.AlternateSeries = ComboBoxWidget(parent_frame, cinfo_name="AlternateSeries",
                                                          label_text="Alternate Series").pack()
        self.widget_mngr.StoryArc = ComboBoxWidget(parent_frame, "StoryArc", label_text="Story Arc").pack()

        numbering = Frame(parent_frame)
        numbering.pack(fill="x")
        self.widget_mngr.AlternateCount = ComboBoxWidget(numbering, "AlternateCount",
                                                         label_text="Alt Count", tooltip="Alternate Count",
                                                         width=COMBO_WIDTH,
                                                         validation="int", default="-1").pack(side="left",expand=False,fill="x")
        self.widget_mngr.AlternateNumber = ComboBoxWidget(numbering, "AlternateNumber", width=COMBO_WIDTH,
                                                          label_text="Alt Number", tooltip="Alternate Number",
                                                          validation="int").pack(side="left",expand=False,fill="x", padx=10)

        self.widget_mngr.StoryArcNumber = ComboBoxWidget(numbering, "StoryArcNumber", width=COMBO_WIDTH,
                                                         label_text="Story Arc Number").pack(side="left",expand=False,fill="x")

        self.widget_mngr.CommunityRating = ComboBoxWidget(numbering, cinfo_name="CommunityRating",
                                                          label_text="Community Rating",
                                                          width=COMBO_WIDTH,
                                                          validation="rating").pack(side="left",expand=False,fill="x")
        self.widget_mngr.BlackAndWhite = OptionMenuWidget(numbering, "BlackAndWhite", "Black And White", COMBO_WIDTH, 18,
                                                          "Unknown", ("Unknown", "Yes", "No")).pack(side="left", expand=False,fill="x")

        self.widget_mngr.PageCount = ComboBoxWidget(parent_frame, "PageCount", label_text="Page Count",
                                                    width=COMBO_WIDTH,
                                                    validation="int", default="0")
        self.widget_mngr.ScanInformation = ComboBoxWidget(parent_frame, cinfo_name="ScanInformation",
                                                          label_text="Scan Information").pack()

    def display_bottom_frame(self):

        frame = self.selection_progress_frame_bottom
        # frame.configure(highlightbackground="black",highlightthickness=1)
        tkinter.Label(frame, text="No files selected", textvariable=self.image_cover_frame.selected_file_path_var).pack(side="left")

        progress_bar_frame = tkinter.Frame(frame)
        pb = self.pb = ProgressBarWidget(progress_bar_frame)
        pb.progress_bar.configure(length=200)
        pb.set_template(f"""Processed: {pb.PROCESSED_TAG}/{pb.TOTAL_TAG} - {pb.ERRORS_TAG} errors""")
        progress_bar_frame.pack(expand=False, fill="both", side="right")
        self.pb.pb_label.pack(side="right")
        self.pb.progress_bar.pack(side="right", fill="x", expand=True)

    # Implementations
    def on_file_selection_preview(self, *args):
        """
        Method called when the users selects one or more files to previe the metadata
        Called dinamically
        :return:
        """
        new_selection, old_selection = args

        if not self.inserting_files:
            self.process_gui_update(old_selection, new_selection)
        self.image_cover_frame.update_cover_image(new_selection)

