import copy
import logging
import os
import tkinter
from tkinter import Frame, Button, CENTER
from tkinter.ttk import Treeview

from src.Common.errors import BadZipFile
from src.Common.loadedcomicinfo import LoadedComicInfo
from src.Common.utils import get_platform
from src.MetadataManager.GUI.widgets import ScrolledFrameWidget

if get_platform() == "linux":
    from src.MetadataManager.GUI.FileChooserWindow import askopenfiles
else:
    from tkinter.filedialog import askopenfiles
selected_frames = []

from src import settings_class

main_settings = settings_class.get_setting("main")

logger = logging.getLogger()
def calculate_widgets_per_row(window_width, widget_width):
    """Calculates how many widgets of x width be placed in y space"""
    return window_width // widget_width


def on_button_click(mode, loaded_cinfo: LoadedComicInfo, front_or_back):
    print("Clicked button.")
    print(f"Is: {front_or_back}")
    print(f"Path: {loaded_cinfo.file_path}")

def calculate_widgets_per_row(window_width, widget_width):
    """Calculates how many widgets of x width be placed in y space"""
    return window_width // widget_width


def on_button_click(mode, loaded_cinfo: LoadedComicInfo, front_or_back):
    print("Clicked button.")
    print(f"Is: {front_or_back}")
    print(f"Path: {loaded_cinfo.file_path}")

def calculate_widgets_per_row(window_width, widget_width):
    """Calculates how many widgets of x width be placed in y space"""
    return window_width // widget_width


def on_button_click(mode, loaded_cinfo: LoadedComicInfo, front_or_back):
    print("Clicked button.")
    print(f"Is: {front_or_back}")
    print(f"Path: {loaded_cinfo.file_path}")




class ExtensionAppGUI(tkinter.Toplevel, Frame):
    """

    """
    scrolled_widget: Frame
    top_level: tkinter.Toplevel = tkinter.Toplevel

    def serve_gui(self, master_frame_):
        """
        This function creates and serves the GUI for the application.
        """
        super().__init__()
        # self = tkinter.Toplevel(master_frame_)
        self.title("Cover Manager")

        side_panel_control = Frame(self)
        side_panel_control.pack(side="right", expand=False, fill="y")

        ctr_btn = Frame(side_panel_control)
        ctr_btn.pack()

        Button(ctr_btn, text="Open Files", command=self.open_files).pack()
        Button(ctr_btn, text="Open Folder", command=self.open_folder).pack()

        tree = self.tree = Treeview(side_panel_control, columns=("Filename", "type"), show="headings", height=8)
        tree.column("#1")
        tree.heading("#1", text="Filename")
        tree.column("#2", anchor=CENTER, width=80)
        tree.heading("#2", text="Type")
        tree.pack(expand=True, fill="y", pady=80, padx=30)

        frame = ScrolledFrameWidget(self)
        frame.pack(fill="both", expand=True)
        scrolled_widget = self.scrolled_widget = frame.create_frame()
        # scrolled_widget.pack(expand=False,fill="both")

        # iterate over the LoadedComicInfo objects in loaded_cinfo_list

        self.tree_dict = {}
        self.prev_width = 0
        self.last_folder = ""
        self.selected_frames = []
        # comic_frame.pack()
        # bind the redraw function to the <Configure> event
        # so that it will be called whenever the window is resized
        self.bind("<Configure>", self.redraw)

    def select_frame(self, event, frame: ComicFrame, pos):
        print(pos)
        if (frame, pos) in self.selected_frames:
            # self.tree.get_children()
            # self.tree.delete(selected_item)
            for children in self.tree.get_children():
                if self.tree_dict[children]["cinfo"] == frame.loaded_cinfo and self.tree_dict[children]["type"] == pos:
                    self.selected_frames.remove((frame, pos))
                    self.tree.delete(children)
                    del self.tree_dict[children]
            print("green" if frame in self.selected_frames else "gray")
            if pos == "front":

                frame.canvas1_frame.configure(highlightbackground="#f0f0f0", highlightcolor="white")
            else:
                frame.canvas2_frame.configure(highlightbackground="#f0f0f0", highlightcolor="white")

            # frame.configure(highlightbackground="green", highlightcolor="green")
            frame.frame_buttons.configure(background="green")
        else:
            node = self.tree.insert('', 'end', text="1", values=(frame.loaded_cinfo.file_name, pos))
            self.tree_dict[node] = {"cinfo": frame.loaded_cinfo, "type": pos}
            self.selected_frames.append((frame, pos))
            if pos == "front":
                frame.canvas1_frame.configure(highlightbackground="green", highlightcolor="green")
            else:
                frame.canvas2_frame.configure(highlightbackground="green", highlightcolor="green")

    def __init__(self):
        ...
        # super().__init__()
        # self.geometry("800x400")

        # self.clean()

    # calculate the number of widgets that can be placed in one row
    # based on the window size

    def redraw(self, event):
        """
        Redraws the widgets in the scrolled widget based on the current size of the window.

        The function is triggered by an event (e.g. window resize) and only redraws the widgets if
        the window dimensions have changed since the last redraw. The widgets are laid out in a grid
        with a number of columns equal to the number of widgets that fit in the current width of the
        window, minus 300 pixels.

        :param: event: The event that triggered to redraw (e.g. a window resize event).

        """
        width = self.winfo_width()
        height = self.winfo_height()
        if not event:
            return
        if not (width != event.width or height != event.height):
            return

        width = self.winfo_width() - 300
        if width == self.prev_width:
            return
        childrens = self.scrolled_widget.winfo_children()
        for child in childrens:
            child.grid_forget()
        if not self.scrolled_widget.winfo_children():
            return
        num_widgets = calculate_widgets_per_row(width, 414)
        #
        # redraw the widgets
        widgets_to_redraw = copy.copy(self.scrolled_widget.winfo_children())  # self.scrolled_widget.grid_slaves()
        i = 0
        j = 0
        while widgets_to_redraw:
            if j >= num_widgets:
                i += 1
                j = 0
            widgets_to_redraw.pop().grid(row=i, column=j)
            j += 1

    def initialize_variables(self):
        self.loaded_cinfo_list: list[LoadedComicInfo] = []
        self.selected_frames: list[Frame] = []
        self.tree_dict = {}

    def clean(self):
        # Initialize Variables
        childrens = self.scrolled_widget.winfo_children()
        for child in childrens:
            child.destroy()

        self.tree.delete(*self.tree.get_children())
        self.initialize_variables()

    def open_folder(self):
        ...

    def open_files(self):

        if not self.last_folder:
            initial_dir = main_settings.library_path.value
        else:
            initial_dir = self.last_folder

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

        logger.debug(f"Selected files [{', '.join(self.selected_files_path)}]")
        self.open_cinfo_list()

        for i, cinfo in enumerate(self.loaded_cinfo_list):
            # create a ComicFrame for each LoadedComicInfo object
            comic_frame = ComicFrame(self.scrolled_widget, cinfo)

            comic_frame.canvas1.bind("<Button-1>",
                                     lambda event, frame_=comic_frame: self.select_frame(event, frame_, "front"))
            comic_frame.canvas2.bind("<Button-1>",
                                     lambda event, frame_=comic_frame: self.select_frame(event, frame_, "back"))
            comic_frame.grid()
        self.redraw(None)

    def open_cinfo_list(self) -> None:
        """
        Creates a list of comicinfo with the comicinfo metadata from the selected files.

        :raises CorruptedComicInfo: If the data inside ComicInfo.xml could not be read after trying to fix te data
        :raises BadZipFile: If the provided zip is not a valid zip or is broken
        """

        # lo.debug("Loading files")
        self.loaded_cinfo_list: list[LoadedComicInfo] = list()
        for file_path in self.selected_files_path:
            try:
                loaded_cinfo = LoadedComicInfo(path=file_path, load_default_metadata=False)
                loaded_cinfo.load_cover_info()
            except BadZipFile as e:
                logger.error("Bad zip file. Either the format is not correct or the file is broken", exc_info=False)
                # self.on_badzipfile_error(e, file_path=file_path)
                continue
            self.loaded_cinfo_list.append(loaded_cinfo)
            # self.on_item_loaded(loaded_cinfo)

        for i, cinfo in enumerate(self.loaded_cinfo_list):
            # create a ComicFrame for each LoadedComicInfo object
            comic_frame = ComicFrame(self.scrolled_widget, cinfo)

            comic_frame.canvas1.bind("<Button-1>",
                                     lambda event, frame_=comic_frame: self.select_frame(event, frame_, "front"))
            comic_frame.canvas2.bind("<Button-1>",
                                     lambda event, frame_=comic_frame: self.select_frame(event, frame_, "back"))
        self.redraw(None)
        logger.debug("Files selected")