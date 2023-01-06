import pathlib
from idlelib.tooltip import Hovertip
from os.path import basename, abspath
from tkinter import Frame, Label, StringVar, Event, Canvas, NW, CENTER, Button
from tkinter.filedialog import askopenfile

from PIL import Image, ImageTk
from pkg_resources import resource_filename

from src import settings_class
from src.Common.loadedcomicinfo import LoadedComicInfo, CoverActions
from src.MetadataManager.GUI.widgets import MULTIPLE_FILES_SELECTED

settings = settings_class.get_setting("main")
window_width, window_height = 0, 0
action_template = abspath(resource_filename(__name__, '../../../res/cover_action_template.png'))

class ComicFrame(Frame):
    def __init__(self, parent, loaded_cinfo):
        super().__init__(parent)
        self.loaded_cinfo: LoadedComicInfo = loaded_cinfo
        self.configure(highlightthickness=1, highlightcolor="grey", highlightbackground="grey")
        # create the first canvas
        frame = self.canvas1_frame = Frame(self, background="grey", highlightcolor="grey", highlightthickness=6)
        frame.pack(side="left")
        canvas1 = self.canvas1 = Canvas(frame)
        canvas1.configure(height='260', width='190')
        canvas1.pack(side="top", expand=False, anchor=CENTER)
        # print the image in the first canvas
        canvas1.create_image(0, 0, image=loaded_cinfo.cached_image, anchor="nw")
        self.print_canvas(frame, loaded_cinfo, "front")

        # create the second canvas
        frame = self.canvas2_frame = Frame(self, background="grey", highlightcolor="grey", highlightthickness=6)
        frame.pack(side="right")
        canvas2 = self.canvas2 = Canvas(frame)
        canvas2.configure(height='260', width='190')
        canvas2.pack(side="top", expand=False, anchor=CENTER)
        # print the image in the second canvas
        canvas2.create_image(0, 0, image=loaded_cinfo.cached_image_last, anchor="nw")
        self.print_canvas(frame, loaded_cinfo, "back")

        # bind the click event to the on_clicked_canvas method

    def print_canvas(self, frame, _, front_or_back):
        if front_or_back not in ("front", "back"):
            return
        frame_buttons = self.frame_buttons = Frame(frame)
        frame_buttons.pack(side="bottom", anchor=CENTER, fill="x")


class CanvasCoverWidget(Canvas):
    overlay_id = None
    overlay_image = None
    no_image_warning_id = None

    action_id = None
    image_id = None


class CoverFrame(Frame):
    canvas_cover_image_id = None
    canvas_backcover_image_id = None
    action_buttons = []

    displayed_cinfo: LoadedComicInfo | None = None

    cover_frame = None
    backcover_frame = None

    def get_canvas(self, cover_else_backcover: bool = True) -> CanvasCoverWidget:
        if cover_else_backcover:
            return self.cover_canvas
        else:
            return self.backcover_canvas

    def get_cinfo_cover_data(self):
        ...

    def resized(self, event: Event):

        global window_width, window_height
        if window_width != event.width:
            if 1000 >= event.width:
                self.hide_back_image()
                window_width, window_height = event.width, event.height

            elif 1000 < event.width and window_width + 400 < event.width:
                if not settings.cache_cover_images:
                    return
                self.show_back_image()
                window_width, window_height = event.width, event.height

    def __init__(self, master):
        super(CoverFrame, self).__init__(master, highlightbackground="black", highlightthickness=2)
        self.configure(pady=5)
        canvas_frame = self
        master.master.bind("<Configure>", self.resized)
        self.selected_file_path_var = StringVar(canvas_frame, value="No file selected")
        self.selected_file_var = StringVar(canvas_frame, value="No file selected")
        self.cover_subtitle = Label(canvas_frame, background="violet", textvariable=self.selected_file_var)
        self.cover_subtitle.configure(width=25, compound="right", justify="left")
        self.selected_file_var.set('No file selected')
        self.tooltip_filename = Hovertip(self, "No file selected", 20)
        self.cover_subtitle.grid(row=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        images_frame = Frame(canvas_frame)

        images_frame.grid(column=0, row=1, sticky="nsew")

        overlay_image = Image.open(action_template)
        overlay_image = overlay_image.resize((190, 260), Image.ANTIALIAS)

        # COVER
        self.cover_frame = Frame(images_frame)
        self.cover_frame.pack(side="left")

        self.cover_canvas = CanvasCoverWidget(self.cover_frame)
        self.cover_canvas.configure(background='#878787', height='260', width='190')
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
                     self.cover_action(action=CoverActions.REPLACE))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="🗑", command=lambda:
                     self.cover_action(action=CoverActions.DELETE))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="➕", command=lambda:
                     self.cover_action(action=CoverActions.APPEND))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="Reset", command=lambda:
                     self.cover_action(action=CoverActions.RESET))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        # BACK COVER
        self.backcover_frame = Frame(images_frame)
        self.backcover_frame.pack(side="left")
        self.backcover_canvas = CanvasCoverWidget(self.backcover_frame)
        self.backcover_canvas.configure(background='#878227', height='260', width='190')
        self.backcover_canvas.pack(side="top", expand=False, anchor=CENTER)

        self.backcover_canvas.overlay_image = ImageTk.PhotoImage(overlay_image, master=self.backcover_canvas)
        self.backcover_canvas.overlay_id = self.backcover_canvas.create_image(150, 150,
                                                                              image=self.backcover_canvas.overlay_image,
                                                                              state="hidden")
        self.backcover_canvas.action_id = self.backcover_canvas.create_text(150, 285, text="", justify="center",
                                                                            state="hidden",
                                                                            fill="yellow", font=('Helvetica 15 bold'))
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

        btn = Button(btn_frame, text="✎", command=lambda: self.backcover_action(action=CoverActions.REPLACE))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="🗑", command=lambda: self.backcover_action(action=CoverActions.DELETE))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="➕", command=lambda: self.backcover_action(action=CoverActions.APPEND))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        btn = Button(btn_frame, text="Reset", command=lambda: self.backcover_action(action=CoverActions.RESET))
        btn.pack(side="bottom", fill="x", expand=True)
        self.action_buttons.append(btn)

    def cover_action(self, loaded_cinfo: LoadedComicInfo = None, auto_trigger=False, action=None):
        if loaded_cinfo is None:
            loaded_cinfo = self.displayed_cinfo
        front_canva: CanvasCoverWidget = self.cover_canvas
        if action is not None:
            loaded_cinfo.cover_action = action
        lcinfo_action = loaded_cinfo.cover_action

        # If the file has a new cover selected, display the new cover and show "edit overlay"
        if loaded_cinfo.new_cover_path:
            cover = loaded_cinfo.new_cover_cache
        else:
            cover = loaded_cinfo.cover_cache
        if not cover:
            front_canva.itemconfig(front_canva.overlay_id, image=front_canva.overlay_image, state="hidden")
            front_canva.itemconfig(front_canva.no_image_warning_id, state="normal")
            front_canva.itemconfig(front_canva.action_id, text="")
            front_canva.itemconfig(front_canva.image_id, state="hidden")
            self.update()
            return
        # A cover exists. Hide warning
        front_canva.itemconfig(front_canva.no_image_warning_id, state="hidden")

        self.update()

        front_canva.itemconfig(front_canva.overlay_id, image=front_canva.overlay_image, state="normal")
        front_canva.itemconfig(front_canva.image_id, image=cover, state="normal")
        match lcinfo_action:
            case CoverActions.APPEND | CoverActions.REPLACE:
                # If the function was manually called, ask the user to select the new cover
                if not auto_trigger:
                    new_cover_file = askopenfile(initialdir=settings.covers_folder_path).name
                    loaded_cinfo.new_cover_path = new_cover_file
                    cover = loaded_cinfo.new_cover_cache
                # Show the Action label
                front_canva.itemconfig(front_canva.action_id,
                                       text="Append" if
                                       lcinfo_action == CoverActions.APPEND else "Replace", state="normal")
            case CoverActions.DELETE:
                front_canva.itemconfig(front_canva.action_id, text="Delete", state="normal")
            case _:
                front_canva.itemconfig(front_canva.overlay_id, state="hidden")
                front_canva.itemconfig(front_canva.action_id, text="", state="normal")
        # Update the displayed cover
        front_canva.itemconfig(front_canva.image_id, image=cover, state="normal")
        self.update()

    def backcover_action(self, loaded_cinfo: LoadedComicInfo = None, auto_trigger=False, action=None):
        if loaded_cinfo is None:
            loaded_cinfo = self.displayed_cinfo
        back_canva: CanvasCoverWidget = self.backcover_canvas
        if action is not None:
            # If reset, undo action changes. Forget about the new cover.
            loaded_cinfo.backcover_action = action
        lcinfo_action = loaded_cinfo.backcover_action

        # If the file has a new cover selected, display the new cover and show "edit overlay"
        if loaded_cinfo.new_backcover_cache:
            cover = loaded_cinfo.new_backcover_cache
        else:
            cover = loaded_cinfo.backcover_cache
        if not cover:
            back_canva.itemconfig(back_canva.overlay_id, image=back_canva.overlay_image, state="hidden")
            back_canva.itemconfig(back_canva.no_image_warning_id, state="normal")
            back_canva.itemconfig(back_canva.action_id, text="")
            back_canva.itemconfig(back_canva.image_id, state="hidden")

            self.update()
            return
        # A cover exists. Hide warning
        back_canva.itemconfig(back_canva.no_image_warning_id, state="hidden")
        self.update()


        back_canva.itemconfig(back_canva.overlay_id, image=back_canva.overlay_image, state="normal")
        back_canva.itemconfig(back_canva.image_id, image=cover, state="normal")
        match lcinfo_action:
            case CoverActions.APPEND | CoverActions.REPLACE:
                # If the function was manually called, ask the user to select the new cover
                if not auto_trigger:
                    new_cover_file = askopenfile(initialdir=settings.covers_folder_path).name
                    loaded_cinfo.new_backcover_path = new_cover_file
                    cover = loaded_cinfo.new_backcover_cache
                # Show the Action label
                back_canva.itemconfig(back_canva.action_id,
                                      text="Append" if
                                      lcinfo_action == CoverActions.APPEND else "Replace",state="normal")
            case CoverActions.DELETE:
                back_canva.itemconfig(back_canva.action_id, text="Delete", state="normal")
            case _:
                back_canva.itemconfig(back_canva.overlay_id, state="hidden")
                back_canva.itemconfig(back_canva.action_id, text="", state="normal")
        # Update the displayed cover
        back_canva.itemconfig(back_canva.image_id, image=cover, state="normal")
        self.update()

    def clear(self):
        self.cover_canvas.itemconfig(self.cover_canvas.image_id, state="hidden")
        self.backcover_canvas.itemconfig(self.backcover_canvas.image_id, state="hidden")
        self.hide_actions()

    def update_cover_image(self, loadedcomicinfo_list: list[LoadedComicInfo], **__):
        if len(loadedcomicinfo_list) > 1:
            self.clear()
            # self.cover_subtitle.configure(text=MULTIPLE_FILES_SELECTED)
            self.selected_file_var.set(MULTIPLE_FILES_SELECTED)
            self.selected_file_path_var.set(MULTIPLE_FILES_SELECTED)
            self.tooltip_filename.text = "\n".join(
                [basename(loadedcomicinfo.file_path) for loadedcomicinfo in loadedcomicinfo_list])
            # self.update()
            return

        if not loadedcomicinfo_list:
            # raise NoFilesSelected()
            return
        loadedcomicinfo = loadedcomicinfo_list[0]
        self.displayed_cinfo = loadedcomicinfo
        if not loadedcomicinfo.cover_cache and not loadedcomicinfo.backcover_cache:
            self.clear()
        else:
            # self.update_cover_button.grid(column=0, row=1)
            ...
        self.tooltip_filename.text = basename(loadedcomicinfo.file_path)
        self.selected_file_var.set(basename(loadedcomicinfo.file_path))
        self.selected_file_path_var.set(loadedcomicinfo.file_path)

        # Checks to display actions:
        self.cover_action(loadedcomicinfo, auto_trigger=True)
        # Update backcover
        self.backcover_action(loadedcomicinfo, auto_trigger=True)

    def hide_actions(self):
        self.cover_canvas.itemconfig(self.cover_canvas.overlay_id, state="hidden")
        self.cover_canvas.itemconfig(self.cover_canvas.action_id, state="hidden")

        self.backcover_canvas.itemconfig(self.backcover_canvas.overlay_id, state="hidden")
        self.backcover_canvas.itemconfig(self.backcover_canvas.action_id, state="hidden")

    def display_action(self, _: str = None):

        image = Image.open(
            pathlib.Path(action_template))
        image = image.resize((190, 260), Image.ANTIALIAS)
        self.watermark = ImageTk.PhotoImage(image, master=self.cover_canvas)
        self._watermark_image_id = self.cover_canvas.create_image(150, 150, image=self.watermark)
        self.cover_canvas.tag_lower(self._image_id)
        self._text_id = self.cover_canvas.create_text(150, 285, text="", justify="center", fill="yellow",
                                                      font=('Helvetica 15 bold'))

        self.cover_canvas.scale("all", -1, 1, 0.63, 0.87)

        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Replace")
        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Delete")
        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Append")
        self.update()

    def hide_back_image(self):
        self.backcover_frame.pack_forget()
        self.cover_frame.pack(side="top")

    def show_back_image(self):
        self.cover_frame.pack(side="left")
        self.backcover_frame.pack(side="right")

    def opencovers(self):
        ...

    def display_next_cover(self, event):
        ...
