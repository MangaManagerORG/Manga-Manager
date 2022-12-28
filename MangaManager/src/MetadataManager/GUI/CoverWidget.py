import pathlib
from idlelib.tooltip import Hovertip
from os.path import basename
from tkinter import Frame, Label, StringVar, Event, Canvas, NW, CENTER, Button
from tkinter.filedialog import askopenfile

from PIL import Image, ImageTk

from src import settings_class
from src.Common.loadedcomicinfo import LoadedComicInfo, CoverActions
from src.MetadataManager.GUI.widgets import MULTIPLE_FILES_SELECTED

settings = settings_class.get_setting("main")
window_width, window_height = 0, 0


class ComicFrame(Frame):
    def __init__(self, parent, loaded_cinfo):
        super().__init__(parent)
        # frame = Frame(self)
        # frame.pack()
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

    def print_canvas(self, frame, loaded_cinfo, front_or_back):
        if front_or_back not in ("front", "back"):
            return
        frame_buttons = self.frame_buttons = Frame(frame)
        frame_buttons.pack(side="bottom", anchor=CENTER, fill="x")



class CanvasCoverWidget(Canvas):
    overlay_id = None
    overlay_image = None

    action_id = None
    image_id = None
class CoverFrame(Frame):
    canvas_cover_image_id = None
    canvas_backcover_image_id = None
    action_buttons = []

    displayed_cinfo:LoadedComicInfo|None = None

    cover_frame = None
    backcover_frame = None


    def get_canvas(self,cover_else_backcover:bool = True) -> CanvasCoverWidget:
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
        # canvas_frame.pack(expand=False)
        self.cover_subtitle = Label(canvas_frame, background="violet", textvariable=self.selected_file_var)
        self.cover_subtitle.configure(width=25, compound="right", justify="left")
        self.selected_file_var.set('No file selected')
        self.tooltip_filename = Hovertip(self, "No file selected", 20)
        self.cover_subtitle.grid(row=0, sticky="nsew")
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        images_frame = Frame(canvas_frame)

        images_frame.grid(column=0, row=1, sticky="nsew")

        overlay_image = Image.open(pathlib.Path(
            r"I:\Mi unidad\Programacion\Python\MangaManagerV2\MangaManager\res\cover_action_template.png"))
        overlay_image = overlay_image.resize((190, 260), Image.ANTIALIAS)


        # COVER
        self.cover_frame = Frame(images_frame)
        self.cover_frame.pack(side="left")

        self.cover_canvas = CanvasCoverWidget(self.cover_frame)
        self.cover_canvas.configure(background='#878787', height='260', width='190')
        self.cover_canvas.pack(side="top", expand=False, anchor=CENTER)

        self.cover_canvas.overlay_image = ImageTk.PhotoImage(overlay_image, master=self.cover_canvas)
        self.cover_canvas.overlay_id = self.cover_canvas.create_image(150, 150, image=self.cover_canvas.overlay_image, state="hidden")
        self.cover_canvas.action_id = self.cover_canvas.create_text(150, 285, text="", justify="center", fill="yellow",font=('Helvetica 15 bold'))
        self.cover_canvas.image_id = self.cover_canvas.create_image(0, 0, anchor=NW)
        self.cover_canvas.scale("all", -1, 1, 0.63, 0.87)
        self.cover_canvas.tag_lower(self.cover_canvas.image_id)
        buttons_frame = Frame(self.cover_frame)
        buttons_frame.pack(side="bottom", anchor=CENTER, fill="x")

        btn = Button(buttons_frame, text="✎", command=lambda: self.action(CoverActions.REPLACE, True))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)
        btn = Button(buttons_frame, text="🗑", command=lambda: self.action(CoverActions.DELETE, True))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)
        btn = Button(buttons_frame, text="➕", command=lambda: self.action(CoverActions.APPEND, True))
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)



        # BACK COVER
        self.backcover_frame = Frame(images_frame)
        self.backcover_frame.pack(side="left")
        self.backcover_canvas = CanvasCoverWidget(self.backcover_frame)
        self.backcover_canvas.configure(background='#878227', height='260', width='190')
        self.backcover_canvas.pack(side="top", expand=False, anchor=CENTER)

        self.backcover_canvas.overlay_image = ImageTk.PhotoImage(overlay_image, master=self.backcover_canvas)
        self.backcover_canvas.overlay_id = self.backcover_canvas.create_image(150, 150, image=self.backcover_canvas.overlay_image, state="hidden")
        self.backcover_canvas.action_id = self.backcover_canvas.create_text(150, 285, text="", justify="center",
                                                                        fill="yellow", font=('Helvetica 15 bold'))
        self.backcover_canvas.image_id = self.backcover_canvas.create_image(0, 0, anchor=NW)
        self.backcover_canvas.scale("all", -1, 1, 0.63, 0.87)
        self.backcover_canvas.tag_lower(self.cover_canvas.image_id)

        buttons_frame = Frame(self.backcover_frame)
        buttons_frame.pack(side="bottom", anchor=CENTER, fill="x")

        btn = Button(buttons_frame, text="✎",)
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)
        btn = Button(buttons_frame, text="🗑",)
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)
        btn = Button(buttons_frame, text="➕",)
        btn.pack(side="left", fill="x", expand=True)
        self.action_buttons.append(btn)

        # self.cover_canvas.itemconfig(self.cover_canvas.image_id, state="hidden")
        # self.backcover_canvas.itemconfig(self.backcover_canvas.image_id, state="hidden")

        # if settings.cache_cover_images:
        #     self.hide_back_image()
        # self.cover_canvas.grid(column=0, row=1,sticky="nsew")

        # self.update_cover_button = ButtonWidget(master=canvas_frame, text='Replace Cover',
        #                                         tooltip="Click to REPLACE this cover image",
        #                                         command=lambda: self.opencovers()
        #                                         )
        # self.update_cover_button = ButtonWidget(master=canvas_frame, text='Replace Cover',
        #                                         tooltip="Click to REPLACE this cover image",
        #                                         command=lambda: self.opencovers
        #                                         )
        # self.update_cover_button.grid(column=0, row=1)
        # self.create_canvas_image()

    def action(self, action_to_do: CoverActions, is_cover_else_backcover: bool, auto_trigger=False):
        """

        :param action:
        :param is_cover_else_backcover:
        :param auto_trigger: Code recycling. When loading the images this fucntions i called. This avoids triggering user-specific actions like selectign a new file
        :return:
        """
        loaded_cinfo = self.displayed_cinfo
        canva: CanvasCoverWidget = self.get_canvas(is_cover_else_backcover)
        if is_cover_else_backcover:
            loaded_cinfo.cover_action = action_to_do

        else:
            loaded_cinfo.backcover_action = action_to_do
        action = action_to_do
        if loaded_cinfo.new_cover_cache:
            cover = loaded_cinfo.new_cover_cache if is_cover_else_backcover else loaded_cinfo.new_backcover_cache
        else:
            cover = loaded_cinfo.cover_cache if is_cover_else_backcover else loaded_cinfo.backcover_cache

        canva.itemconfig(canva.overlay_id, image=canva.overlay_image, state="normal")

        match action:
            case CoverActions.APPEND | CoverActions.REPLACE:
                if not auto_trigger:
                    if is_cover_else_backcover:
                        self.displayed_cinfo.new_cover_path = askopenfile(initialdir=settings.covers_folder_path).name
                        canva.itemconfig(canva.image_id, image=loaded_cinfo.new_cover_cache)
                    else:
                        self.displayed_cinfo.new_backcover_path = askopenfile(initialdir=settings.covers_folder_path).name
                        canva.itemconfig(canva.image_id, image=loaded_cinfo.new_backcover_cache)
                else:
                    if is_cover_else_backcover:
                        canva.itemconfig(canva.image_id, image=loaded_cinfo.new_cover_cache)
                    else:
                        canva.itemconfig(canva.image_id, image=loaded_cinfo.new_backcover_cache)

                canva.itemconfig(canva.action_id, text="Append" if action == CoverActions.APPEND else "Replace", state="normal")
            case CoverActions.DELETE:
                item_config = canva.itemconfig(canva.image_id)
                image = item_config['image']
                if str(loaded_cinfo.cover_cache if is_cover_else_backcover else loaded_cinfo.backcover_cache) != image[4]:
                    canva.itemconfig(canva.image_id, image=cover)
                canva.itemconfig(canva.action_id, text="Delete", state="normal")
            case _:
                canva.itemconfig(canva.overlay_id, state="hidden")
                canva.itemconfig(canva.action_id, text="", state="normal")
                canva.itemconfig(canva.image_id, image=cover, state="normal")
        self.update()
    def clear(self):
        # self.update_cover_button.configure(text="Select covers", state="normal")
        # self.update_cover_button.grid()
        self.cover_canvas.itemconfig(self.cover_canvas.image_id, state="hidden")
        self.backcover_canvas.itemconfig(self.backcover_canvas.image_id, state="hidden")
        self.hide_actions()
        return

    def update_cover_image(self, loadedcomicinfo_list: list[LoadedComicInfo], **__):
        if len(loadedcomicinfo_list) > 1:
            self.clear()
            # self.cover_subtitle.configure(text=MULTIPLE_FILES_SELECTED)
            self.selected_file_var.set(MULTIPLE_FILES_SELECTED)
            self.selected_file_path_var.set(MULTIPLE_FILES_SELECTED)
            self.tooltip_filename.text = "\n".join(
                [basename(loadedcomicinfo.file_path) for loadedcomicinfo in loadedcomicinfo_list])
            self.update()
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
        self.action(loadedcomicinfo.cover_action,True,auto_trigger=True)
        self.action(loadedcomicinfo.cover_action, False,auto_trigger=True)

    def hide_actions(self):
        self.cover_canvas.itemconfig(self.cover_canvas.overlay_id, state="hidden")
        self.cover_canvas.itemconfig(self.cover_canvas.action_id, state="hidden")

        self.backcover_canvas.itemconfig(self.backcover_canvas.overlay_id, state="hidden")
        self.backcover_canvas.itemconfig(self.backcover_canvas.action_id, state="hidden")
    def display_action(self, action: str = None):

        image = Image.open(
            pathlib.Path(r"I:\Mi unidad\Programacion\Python\MangaManagerV2\MangaManager\res\cover_action_template.png"))
        image = image.resize((190, 260), Image.ANTIALIAS)
        self.watermark = ImageTk.PhotoImage(image, master=self.cover_canvas)
        self._watermark_image_id = self.cover_canvas.create_image(150, 150, image=self.watermark)
        self.cover_canvas.tag_lower(self._image_id)
        self._text_id = self.cover_canvas.create_text(150, 285, text="", justify="center", fill="yellow",
                                                      font=('Helvetica 15 bold'))
        # match action:
        #     case "replace":
        #
        #     case "delete":
        #         self.cover_canvas.create_text(150, 285, text="<<Delete>>", justify="center", fill="yellow",
        #                         font=('Helvetica 15 bold'))
        #     case "append":
        #         self.cover_canvas.create_text(150, 285, text="<<Append>>", justify="center", fill="yellow",
        #                         font=('Helvetica 15 bold'))
        self.cover_canvas.scale("all", -1, 1, 0.63, 0.87)

        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Replace")
        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Delete")
        self.update()
        self.cover_canvas.itemconfig(self._text_id, text="Append")
        self.update()
    # def create_canvas_image(self):
        # try:
        #     self.canvas_cover_image_id = self.cover_canvas.create_image(0, 0, anchor=NW)
        # except UnidentifiedImageError:
        #     ...

    # def create_canvas_back_image(self):
    #     try:
    #         self.canvas_backcover_image_id = self.backcover_canvas.create_image(0, 0, anchor=NW)
    #     except UnidentifiedImageError:
    #         ...

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
