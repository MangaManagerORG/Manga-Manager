import copy
import logging
import platform
import tkinter
from os.path import abspath
from tkinter import Frame, CENTER, Button, NW
from tkinter import messagebox as mb
from tkinter.filedialog import askopenfile
from tkinter.ttk import Treeview

from PIL import Image, ImageTk
from pkg_resources import resource_filename

from src.Common.loadedcomicinfo import LoadedComicInfo, CoverActions
from src.MetadataManager.GUI.CoverWidget import CoverFrame, CanvasCoverWidget
from src.MetadataManager.GUI.scrolledframe import ScrolledFrame
from src.MetadataManager.GUI.widgets import ButtonWidget
from src.MetadataManager.MetadataManagerGUI import GUIApp
from src.Settings import default_settings

action_template = abspath(resource_filename(__name__, '../../../res/cover_action_template.png'))


def on_button_click(_, loaded_cinfo: LoadedComicInfo, front_or_back):
    print("Clicked button.")
    print(f"Is: {front_or_back}")
    print(f"Path: {loaded_cinfo.file_path}")


settings = default_settings["main"]
logger = logging.getLogger()

class ComicFrame(CoverFrame):
    def __init__(self, master, loaded_cinfo: LoadedComicInfo):
        super(CoverFrame, self).__init__(master, highlightbackground="black")
        self.loaded_cinfo: LoadedComicInfo = loaded_cinfo
        self.configure(highlightthickness=2, highlightcolor="grey", highlightbackground="grey", padx=20, pady=20)

        overlay_image = Image.open(action_template)
        overlay_image = overlay_image.resize((190, 260), Image.ANTIALIAS)

        # COVER
        self.cover_frame = Frame(self)
        self.cover_frame.pack(side="left")

        self.cover_canvas = CanvasCoverWidget(self.cover_frame)
        self.cover_canvas.configure(background='#878787', height='260', width='190', highlightthickness=8)
        self.cover_canvas.pack(side="top", expand=False, anchor=CENTER)

        self.cover_canvas.overlay_image = ImageTk.PhotoImage(overlay_image, master=self.cover_canvas)
        self.cover_canvas.overlay_id = self.cover_canvas.create_image(150, 150, image=self.cover_canvas.overlay_image,
                                                                      state="hidden")
        self.cover_canvas.action_id = self.cover_canvas.create_text(150, 285, text="", justify="center", fill="yellow",
                                                                    font=('Helvetica 15 bold'))
        self.cover_canvas.no_image_warning_id = self.cover_canvas.create_text(150, 120,
                                                                              text="No Cover!\nNo image\ncould be\nloaded",
                                                                              justify="center", fill="red",
                                                                              state="hidden",
                                                                              font=('Helvetica 28 bold'))
        self.cover_canvas.image_id = self.cover_canvas.create_image(0, 0, anchor=NW)
        self.cover_canvas.scale("all", -1, 1, 0.63, 0.87)
        self.cover_canvas.tag_lower(self.cover_canvas.image_id)
        btn_frame = Frame(self.cover_frame)
        btn_frame.pack(side="bottom", anchor=CENTER, fill="x")
        btn = Button(btn_frame, text="✎", command=lambda:
        self.cover_action(self.loaded_cinfo, action=CoverActions.REPLACE, parent=self))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="🗑", command=lambda:
        self.cover_action(self.loaded_cinfo, action=CoverActions.DELETE))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="➕", command=lambda:
        self.cover_action(self.loaded_cinfo, action=CoverActions.APPEND, parent=self))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="Reset", command=lambda:
        self.cover_action(self.loaded_cinfo, action=CoverActions.RESET))
        btn.pack(side="left", fill="x", expand=True)
        self.cover_action(self.loaded_cinfo, auto_trigger=True,proc_update=False)

        # BACK COVER
        self.backcover_frame = Frame(self)
        self.backcover_frame.pack(side="left")

        self.backcover_canvas = CanvasCoverWidget(self.backcover_frame)
        self.backcover_canvas.configure(background='#878787', height='260', width='190', highlightthickness=8)
        self.backcover_canvas.pack(side="top", expand=False, anchor=CENTER)

        self.backcover_canvas.overlay_image = ImageTk.PhotoImage(overlay_image, master=self.backcover_canvas)
        self.backcover_canvas.overlay_id = self.backcover_canvas.create_image(150, 150,
                                                                              image=self.backcover_canvas.overlay_image,
                                                                              state="hidden")
        self.backcover_canvas.action_id = self.backcover_canvas.create_text(150, 285, text="", justify="center",
                                                                            fill="yellow",
                                                                            font=('Helvetica 15 bold'))
        self.backcover_canvas.no_image_warning_id = self.backcover_canvas.create_text(150, 120,
                                                                                      text="No Cover!\nNo image\ncould be\nloaded",
                                                                                      justify="center", fill="red",
                                                                                      state="hidden",
                                                                                      font=('Helvetica 28 bold'))
        self.backcover_canvas.image_id = self.backcover_canvas.create_image(0, 0, anchor=NW)
        self.backcover_canvas.scale("all", -1, 1, 0.63, 0.87)
        self.backcover_canvas.tag_lower(self.backcover_canvas.image_id)
        btn_frame = Frame(self.backcover_frame)
        btn_frame.pack(side="bottom", anchor=CENTER, fill="x")
        btn = Button(btn_frame, text="✎", command=lambda:
        self.backcover_action(self.loaded_cinfo, action=CoverActions.REPLACE, parent=self))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="🗑", command=lambda:
        self.backcover_action(self.loaded_cinfo, action=CoverActions.DELETE))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="➕", command=lambda:
        self.backcover_action(self.loaded_cinfo, action=CoverActions.APPEND, parent=self))
        btn.pack(side="left", fill="x", expand=True)

        btn = Button(btn_frame, text="Reset", command=lambda:
        self.backcover_action(self.loaded_cinfo, action=CoverActions.RESET))
        btn.pack(side="left", fill="x", expand=True)

        # Load backcover
        self.backcover_action(self.loaded_cinfo, auto_trigger=True,proc_update=False)


class CoverManager(tkinter.Toplevel):
    name = "CoverManager"

    scrolled_widget: Frame
    top_level: tkinter.Toplevel = tkinter.Toplevel

    def __init__(self, master, super_: GUIApp = None, **kwargs):
        """
        Initializes the toplevel window but hides the window.
        """
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(f"Error initializing the {self.__class__.__name__} Extension. The 'name' attribute must be set in the ExtensionApp class.")
        # if self.embedded_ui:
        super().__init__(master=master,**kwargs)
        self.title(self.__class__.name)
        if super_ is not None:
            self._super = super_

        self.serve_gui()
        self.bind("<Configure>", self.redraw)

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

        num_widgets = width // 414
        try:
            logger.trace(f"Number of widgets per row: {num_widgets}")
            logger.trace(f"Number of rows: {len(self.scrolled_widget.winfo_children())/num_widgets}")
        except ZeroDivisionError:
            pass
        # redraw the widgets
        widgets_to_redraw = list(reversed(copy.copy(self.scrolled_widget.winfo_children())))  # self.scrolled_widget.grid_slaves()
        i = 0
        j = 0
        while widgets_to_redraw:
            if j >= num_widgets:
                i += 1
                j = 0
            widgets_to_redraw.pop().grid(row=i, column=j)
            j += 1

    def exit_btn(self):
        self._super.show_not_saved_indicator()
        self.destroy()
        self.update()

    def serve_gui(self):
        """
        This function creates and serves the GUI for the application.
        """
        if platform.system() == "Linux":
            self.attributes('-zoomed', True)
        elif platform.system() == "Windows":
            self.state('zoomed')
        side_panel_control = Frame(self)
        side_panel_control.pack(side="right", expand=False, fill="y")
        #
        ctr_btn = Frame(self)
        ctr_btn.pack()
        #
        #
        tree = self.tree = Treeview(side_panel_control, columns=("Filename", "type"), show="headings", height=8)
        tree.column("#1")
        tree.heading("#1", text="Filename")
        tree.column("#2", anchor=CENTER, width=80)
        tree.heading("#2", text="Type")
        tree.pack(expand=True, fill="y", pady=(80,0), padx=30, side="top")
        action_buttons = Frame(side_panel_control)
        action_buttons.pack(ipadx=20,ipady=20,pady=(0,80), fill="x", padx=30)

        ButtonWidget(master=action_buttons, text="Delete Selected",
                     tooltip="Deletes the image for the selected cover/backcovers",
                     command=lambda: self.run_bulk_action(CoverActions.DELETE)).pack(side="top", fill="x")
        ButtonWidget(master=action_buttons, text="Append to Selected",
                     tooltip="Appends the image for the selected cover/backcovers",
                     command=lambda: self.run_bulk_action(CoverActions.APPEND)).pack( side="top", fill="x")
        ButtonWidget(master=action_buttons, text="Replace Selected",
                     tooltip="Replaces the image for the selected cover/backcovers",
                     command=lambda: self.run_bulk_action(CoverActions.REPLACE)).pack(side="top", fill="x")
        ButtonWidget(master=action_buttons, text="Clear Selection",
                     command=self.clear_selection).pack(fill="x")
        ButtonWidget(master=action_buttons, text="Close window",
                     command=self.exit_btn).pack(fill="x",ipady=10)

        content_frame = Frame(self)
        content_frame.pack(fill="both", side="left", expand=True)

        frame = ScrolledFrame(master=content_frame, scrolltype="vertical", usemousewheel=True)
        frame.pack(fill="both", expand=True)
        self.scrolled_widget = frame.innerframe


        self.tree_dict = {}
        self.prev_width = 0
        self.last_folder = ""
        self.selected_frames: list[tuple[ComicFrame, str]] = []
        # bind the redraw function to the <Configure> event
        # so that it will be called whenever the window is resized

        if not self._super.loaded_cinfo_list:
            mb.showwarning("No files selected", "No files were selected so none will be displayed in cover manager", parent=self)
            # self.deiconify()
            self.destroy()
            return

        # self.redraw(None)
        for i, cinfo in enumerate(self._super.loaded_cinfo_list):
            # create a ComicFrame for each LoadedComicInfo object
            comic_frame = ComicFrame(self.scrolled_widget, cinfo)

            comic_frame.cover_canvas.bind("<Button-1>",
                                          lambda event, frame_=comic_frame: self.select_frame(event, frame_, "front"))
            comic_frame.backcover_canvas.bind("<Button-1>",
                                              lambda event, frame_=comic_frame: self.select_frame(event, frame_,
                                                                                                  "back"))
            comic_frame.grid()
        self.redraw(None)

    def select_frame(self, _, frame: ComicFrame, pos):
        print(pos)
        if (frame, pos) in self.selected_frames:
            for children in self.tree.get_children():
                if self.tree_dict[children]["cinfo"] == frame.loaded_cinfo and self.tree_dict[children]["type"] == pos:
                    self.selected_frames.remove((frame, pos))
                    self.tree.delete(children)
                    del self.tree_dict[children]
            print("green" if frame in self.selected_frames else "gray")
            if pos == "front":

                frame.cover_canvas.configure(highlightbackground="#f0f0f0", highlightcolor="white")
            else:
                frame.backcover_canvas.configure(highlightbackground="#f0f0f0", highlightcolor="white")

        else:
            node = self.tree.insert('', 'end', text="1", values=(frame.loaded_cinfo.file_name, pos))
            self.tree_dict[node] = {"cinfo": frame.loaded_cinfo, "type": pos}
            self.selected_frames.append((frame, pos))
            if pos == "front":
                frame.cover_canvas.configure(highlightbackground="green", highlightcolor="green")
            else:
                frame.backcover_canvas.configure(highlightbackground="green", highlightcolor="green")

    def run_bulk_action(self, action: CoverActions):
        new_cover_file = None
        cover = None
        if action == CoverActions.APPEND or action == CoverActions.REPLACE:
            new_cover_file = askopenfile(parent=self,initialdir=settings.get_control('covers_folder_path')).name

        for frame, type_ in self.selected_frames:
            # create a ComicFrame for each LoadedComicInfo object
            frame: ComicFrame
            loaded_cinfo = frame.loaded_cinfo
            canva: CanvasCoverWidget = frame.cover_canvas if type_ == "front" else frame.backcover_canvas
            if action is not None:
                # If reset, undo action changes. Forget about the new cover.
                if type_ == "front":
                    loaded_cinfo.cover_action = action
                else:
                    loaded_cinfo.backcover_action = action
            if loaded_cinfo.new_backcover_cache:
                cover = loaded_cinfo.new_backcover_cache
            else:
                cover = loaded_cinfo.backcover_cache

            if not cover:
                canva.itemconfig(canva.overlay_id, image=canva.overlay_image, state="hidden")
                canva.itemconfig(canva.no_image_warning_id, state="normal")
                canva.itemconfig(canva.action_id, text="")
                canva.itemconfig(canva.image_id, state="hidden")
            else:
                # A cover exists. Hide warning
                canva.itemconfig(canva.no_image_warning_id, state="hidden")
            canva.itemconfig(canva.overlay_id, image=canva.overlay_image, state="normal")
            canva.itemconfig(canva.image_id, image=cover, state="normal")
            match action:
                case CoverActions.APPEND | CoverActions.REPLACE:
                    loaded_cinfo.new_cover_path = new_cover_file
                    cover = loaded_cinfo.new_cover_cache
                    # Show the Action label
                    canva.itemconfig(canva.action_id,
                                     text="Append" if
                                     action == CoverActions.APPEND else "Replace", state="normal")
                case CoverActions.DELETE:
                    canva.itemconfig(canva.action_id, text="Delete", state="normal")
                case _:
                    canva.itemconfig(canva.overlay_id, state="hidden")
                    canva.itemconfig(canva.action_id, text="", state="normal")

            # Update the displayed cover
            canva.itemconfig(canva.image_id, image=cover, state="normal")

    def clear_selection(self):
        while self.selected_frames:
            frame, pos = self.selected_frames.pop()
            frame.cover_canvas.configure(highlightbackground="#f0f0f0", highlightcolor="white")
            frame.backcover_canvas.configure(highlightbackground="#f0f0f0", highlightcolor="white")

        for children in self.tree.get_children():
            self.tree.delete(children)
            del self.tree_dict[children]
