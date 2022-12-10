from __future__ import annotations

import copy
import logging
import os.path
import re
import tkinter
from idlelib.tooltip import Hovertip
from os.path import basename
from tkinter import Frame, Label
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox, OptionMenu, Progressbar

from PIL import UnidentifiedImageError

from src import settings as settings_class
from src.Common.GUI.models import LongText
from src.Common.GUI.progressbar import ProgressBar
from src.Common.GUI.scrolledframe import ScrolledFrame
from src.Common.loadedcomicinfo import LoadedComicInfo
from src.Common.settings import SettingItem
from src.Common.utils import open_settings_folder
from src.MetadataManager import comicinfo

INT_PATTERN = re.compile("^-*\d*(?:,?\d+|\.?\d+)?$")
MULTIPLE_FILES_SELECTED = "Multiple Files Selected"
logger = logging.getLogger()
window_width, window_height = 0, 0

settings = settings_class.get_setting("main")


def validate_int(value):
    ilegal_chars = [character for character in str(value) if not INT_PATTERN.match(character)]
    return not ilegal_chars


class ButtonWidget(tkinter.Button):
    def __init__(self, tooltip=None, *args, **kwargs):

        super(ButtonWidget, self).__init__(*args, **kwargs)

        if tooltip:
            self.configure(text=self.cget('text') + '  ⁱ')
            self.tooltip = Hovertip(self, tooltip, 20)


class WidgetManager:
    cinfo_tags: list[str] = list()

    def get_widget(self, name) -> ComboBoxWidget | LongTextWidget | OptionMenuWidget:
        return getattr(self, name)

    def add_widget(self, name, widget_frame: ComboBoxWidget | LongTextWidget | OptionMenuWidget):
        self.cinfo_tags.append(name)
        setattr(self, name, widget_frame)

    def clean_widgets(self):
        for widget_name in self.__dict__:
            widget = self.get_widget(widget_name)
            widget.set_default()
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = widget.default_vals or []

    def get_tags(self):
        return [tag for tag in self.__dict__]


class Widget(Frame):
    validation: str | None = None
    widget_slave = None
    widget: Combobox | LongText | OptionMenu
    name: str
    NONE = "~~# None ##~~"

    def __init__(self, master):
        super(Widget, self).__init__(master)

    def set(self, value):
        if value is None:
            return
        if not self.validation:
            self.widget.set(value)
            return

        if value and validate_int(value):
            if self.validation == "rating" and float(value) < 0 or float(value) > 10:
                return
            self.widget.set(value)

    def set_default(self):
        self.widget.set("")

    def get(self):
        return self.widget.get()

    def pack(self, **kwargs) -> Widget:
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).pack(kwargs or {"fill": "both", "side": "top"})
        return self

    def grid(self, row=None, column=None, **kwargs) -> Widget:
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).grid(row=row, column=column, sticky="ew", **kwargs)
        return self

    def set_label(self, text, tooltip=None):
        self.label = Label(self, text=text)
        self.label.pack(side="top")
        if tooltip:
            self.label.configure(text=self.label.cget('text') + '  ⁱ')
            self.label.tooltip = Hovertip(self.label, tooltip, 20)


class ComboBoxWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None, default="",
                 validation=None, tooltip: str = None):
        super(ComboBoxWidget, self).__init__(master)
        # super(Widget, self).__init__()
        if not label_text:
            label_text = cinfo_name
        self.name = cinfo_name
        self.default = default
        self.default_vals = default_values
        # Label:
        self.set_label(label_text, tooltip)

        # Input:
        self.validation = validation
        vcmd = (self.register(validate_int), '%S')
        if validation == "int":
            self.widget: Combobox = Combobox(self, name=cinfo_name.lower(), values=default_values,
                                             validate='key', validatecommand=vcmd)
        else:
            self.widget: Combobox = Combobox(self, name=cinfo_name.lower(), values=default_values)

        if width is not None:
            self.widget.configure(width=width)


class OptionMenuWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, max_width=None, default=None, *values):

        if not label_text:
            label_text = cinfo_name
        super(OptionMenuWidget, self).__init__(master)
        if not label_text:
            label_text = cinfo_name
        self.default = default
        self.name = cinfo_name
        self.set_label(label_text)
        # noinspection PyTypeChecker
        self.widget = tkinter.StringVar(self, name=cinfo_name, value=default)
        self.widget_slave: OptionMenu = OptionMenu(self, self.widget, *values)
        # noinspection PyUnresolvedReferences
        if max_width:
            self.widget_slave.configure(width=max_width)

    def update_listed_values(self, default_selected, values) -> None:
        self.widget_slave.set_menu(default_selected, *values)

    def get_options(self) -> list[str]:
        values_list = []
        match self.name:
            case "AgeRating":
                values_list = comicinfo.AgeRating.list()
            case "Format":
                values_list = comicinfo.format_list
            case "BlackAndWhite":
                values_list = comicinfo.YesNo.list()
            case "Manga":
                values_list = comicinfo.Manga.list()
            case _:
                logger.error(f"Unhandled error. '{self.name}' is not a registered widget whom you can extract options from")
        return values_list

    def append_first(self, value: str):
        self.update_listed_values(value, [value] + self.get_options())

    def remove_first(self):
        self.update_listed_values(self.get_options())


class LongTextWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, width: int = None):
        super(LongTextWidget, self).__init__(master)
        if not label_text:
            label_text = cinfo_name
        self.set_label(label_text)
        self.default = ""
        self.name = cinfo_name
        # Input
        self.widget_slave = ScrolledText(self)
        self.widget_slave.configure(height='5', width=width)
        self.widget_slave.pack(fill='both', side='top')

        self.widget = LongText(name=cinfo_name)
        self.widget.linked_text_field = self.widget_slave


class ScrolledFrameWidget(ScrolledFrame):
    def __init__(self, master, *args, **kwargs):
        super(ScrolledFrameWidget, self).__init__(master, **kwargs)
        self.configure(usemousewheel=True)
        self.paned_window = tkinter.PanedWindow(self.innerframe)
        self.paned_window.pack(fill="both", expand=True)
        self.pack(expand=True, fill='both', side='top')

    def create_frame(self):
        """Creates a subframe and packs it"""
        frame = Frame(self.paned_window)
        frame.pack()
        self.paned_window.add(frame)
        return frame


class CoverFrame(tkinter.Frame):
    canvas_image = None
    canvas_image_last = None

    def rezized(self, event: tkinter.Event):

        global window_width, window_height
        if (window_width != event.width):  # or (window_height != event.height)
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
        master.master.bind("<Configure>", self.rezized)

        # canvas_frame.pack(expand=False)
        self.cover_subtitle = tkinter.Label(canvas_frame, background="violet")
        self.cover_subtitle.configure(text='No file selected', width=25, compound="right", justify="left")
        self.tooltip = Hovertip(self, "No file selected", 20)
        self.cover_subtitle.grid(row=0, sticky="nsew")
        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)
        images_frame = Frame(canvas_frame)

        images_frame.grid(column=0, row=1, sticky="nsew")

        self.canvas = tkinter.Canvas(images_frame)
        self.canvas.configure(background='#878787', height='260', width='190')
        self.canvas.pack(side="left")
        self.canvas_back = tkinter.Canvas(images_frame)
        self.canvas_back.configure(background='#878227', height='260', width='190')
        self.canvas_back.pack(side="right")
        if settings.cache_cover_images:
            self.hide_back_image()
        # self.canvas.grid(column=0, row=1,sticky="nsew")

        self.update_cover_button = ButtonWidget(master=canvas_frame, text='Replace Cover',
                                                tooltip="Click to REPLACE this cover image",
                                                command=self.opencovers
                                                )
        # self.update_cover_button.grid(column=0, row=1)
        self.create_canvas_image()

    def clear(self):
        # self.update_cover_button.configure(text="Select covers", state="normal")
        # self.update_cover_button.grid()
        self.canvas.delete('all')
        self.canvas_back.delete('all')
        self.create_canvas_image()
        self.create_canvas_back_image()
        self.update_cover_button.grid_remove()
        return

    def update_cover_image(self, loadedcomicinfo_list: list[LoadedComicInfo], multiple=False):
        if len(loadedcomicinfo_list) > 1:
            self.clear()
            self.cover_subtitle.configure(text=MULTIPLE_FILES_SELECTED)
            self.tooltip.text = "\n".join(
                [os.path.basename(loadedcomicinfo.file_path) for loadedcomicinfo in loadedcomicinfo_list])
            return
        if not loadedcomicinfo_list:
            # raise NoFilesSelected()
            return
        loadedcomicinfo = loadedcomicinfo_list[0]
        if not loadedcomicinfo.cached_image and not loadedcomicinfo.cached_image_last:
            self.clear()
        else:
            self.update_cover_button.grid(column=0, row=1)
        self.tooltip.text = os.path.basename(loadedcomicinfo.file_path)
        self.canvas.itemconfig(self.canvas_image, image=loadedcomicinfo.cached_image)
        self.canvas_back.itemconfig(self.canvas_image_last, image=loadedcomicinfo.cached_image_last)
        self.cover_subtitle.configure(text=basename(loadedcomicinfo.file_path))

    def create_canvas_image(self):
        try:
            self.canvas_image = self.canvas.create_image(0, 0, anchor=tkinter.NW)
        except UnidentifiedImageError as e:
            ...

    def create_canvas_back_image(self):
        try:
            self.canvas_image_last = self.canvas_back.create_image(0, 0, anchor=tkinter.NW)
        except UnidentifiedImageError as e:
            ...

    def hide_back_image(self):
        self.canvas_back.pack_forget()
        self.canvas.pack(side="top")

    def show_back_image(self):
        self.canvas_back.pack(side="right")
        self.canvas.pack(side="left")

    def opencovers(self):
        ...

    def display_next_cover(self, event):
        ...


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


class SettingStringVar(tkinter.StringVar):

    def __init__(self, *args, **kwargs):
        super(SettingStringVar, self).__init__(*args, **kwargs)
        self.linked_setting: SettingItem = None


class SettingBolVar(tkinter.BooleanVar):

    def __init__(self, *args, **kwargs):
        super(SettingBolVar, self).__init__(*args, **kwargs)
        self.linked_setting: SettingItem = None
    # def set(self, value: str) -> None:
    #     self.linked_setting.value = value
    #     super(SettingStringVar, self).set(value)


class SettingsWidgetManager:
    def parse_ui_settings_process(self):
        for stringvar in self.strings_vars:
            if isinstance(stringvar, tkinter.BooleanVar):
                stringvar.linked_setting.value = str(stringvar.get())
            else:
                stringvar.linked_setting.value = str(stringvar.get())
        settings_class.save_settings()

    def __init__(self, parent):
        self.strings_vars: list[tkinter.Variable] = []
        settings_window = tkinter.Toplevel(parent, pady=30, padx=30)
        settings_window.geometry("900x420")
        settings_window.title("Settings")

        main_frame = ScrolledFrameWidget(settings_window, scrolltype="vertical").create_frame()
        self.widgets_frame = tkinter.Frame(main_frame, pady=30, padx=30)
        self.widgets_frame.pack()
        control_frame = tkinter.Frame(settings_window)
        control_frame.pack()
        ButtonWidget(master=control_frame, text="Save", tooltip="Saves the settings to the config file",
                     command=self.parse_ui_settings_process).pack()
        ButtonWidget(master=control_frame, text="Open Settings Folder",
                     tooltip="Opens the folder where Manga Manager stores it's files",
                     command=open_settings_folder).pack()
        # for setting_section in settings_class.__dict__.sort(key=):
        self.settings_widget = {}
        for settings_section in settings_class.factory:
            section_class = settings_class.get_setting(settings_section)

            frame = tkinter.LabelFrame(master=self.widgets_frame, text=settings_section)
            frame.pack(expand=True, fill="both")

            self.settings_widget[settings_section] = {}
            self.print_setting_entry(frame, section_class)
            center(settings_window)

    def print_setting_entry(self, parent_frame, section_class):
        for i, setting in enumerate(section_class.settings):

            row = tkinter.Frame(parent_frame)
            row.pack(expand=True, fill="x")
            label = tkinter.Label(master=row, text=setting.name, width=30, justify="right", anchor="e")
            label.pack(side="left")
            if setting.tooltip:
                label.configure(text=label.cget('text') + '  ⁱ')
                label.tooltip = Hovertip(label, setting.tooltip, 20)

            if setting.type_ == "bool":
                value = True if setting.value else False
                string_var = SettingBolVar(value=value, name=f"{setting.section}.{setting.key}")
                string_var.linked_setting = setting
                entry = tkinter.Checkbutton(row, variable=string_var, onvalue=1, offvalue=0)
                entry.pack(side="left")
                self.strings_vars.append(string_var)
            else:
                string_var = SettingStringVar(value=setting.value, name=f"{setting.section}.{setting.key}")
                string_var.linked_setting = setting
                self.strings_vars.append(string_var)
                entry = tkinter.Entry(master=row, width=80, textvariable=string_var)
                entry.pack(side="right", expand=True, fill="x", padx=(5, 30))
            entry.setting_section = section_class._section_name
            entry.setting_name = setting
            self.settings_widget[section_class._section_name][setting] = entry
            if setting.type_ == "bool":
                string_var.set(bool(setting))
            # else:
            # entry.insert(0, setting.value)

    # def save(self):
    #     for setting_section in self.settings_widget:
    #         set_class = settings_class.get_setion(setting_section)
    #         for config in self.settings_widget.get(setting_section):
    #             entry_data = self.settings_widget.get(setting_section).get(config).get()
    #             set_class.set_value(config,entry_data)


def _run_hook(source: list[callable], *args):
    for hook_function in source:
        try:
            hook_function(*args)
        except:
            logger.exception("Error calling hook")


class TreeviewWidget(tkinter.ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super(TreeviewWidget, self).__init__(padding=[-20, 0, 0, 0], *args, **kwargs)
        self.heading('#0', text='Click to select all files', anchor='n', command=self.select_all)
        # self.pack(expand=True, side="top")
        self.bind('<<TreeviewSelect>>', self._on_select)
        self._hook_items_inserted: list[callable] = []
        self._hook_items_selected: list[callable] = []
        self.content = {}
        self.prev_selection = None

    def clear(self):
        self.delete(*self.get_children())

    def select_all(self, event=None):
        for item in self.get_children():
            self.selection_add(item)

    def get_selected(self) -> list[LoadedComicInfo]:
        return [self.content.get(item) for item in self.selection()]

    def insert(self, loaded_cinfo: LoadedComicInfo, *args, **kwargs):
        a = super(TreeviewWidget, self).insert("", 'end', loaded_cinfo.file_path, text=loaded_cinfo.file_name, *args,
                                               **kwargs)
        self.content[loaded_cinfo.file_path] = loaded_cinfo
        # self._call_hook_item_inserted(loaded_cinfo)
        self.select_all()

    def _on_select(self, *args):
        prev_selection = copy.copy(self.prev_selection)
        selected = [self.content.get(item) for item in self.selection()]
        self.prev_selection = selected
        if not selected:
            return
        self._call_hook_item_selected(selected, prev_selection)

    ##################
    # Hook Stuff
    ##################
    def add_hook_item_selected(self, function: callable):
        self._hook_items_selected.append(function)

    def add_hook_item_inserted(self, function: callable):
        self._hook_items_inserted.append(function)

    def _call_hook_item_selected(self, loaded_cinfo_list: list[LoadedComicInfo], prev_selection):
        _run_hook(self._hook_items_selected, loaded_cinfo_list, prev_selection)

    def _call_hook_item_inserted(self, loaded_comicinfo: LoadedComicInfo):
        _run_hook(self._hook_items_inserted, [loaded_comicinfo])


class ProgressBarWidget(ProgressBar):
    def __init__(self, parent):

        pb_frame = Frame(parent)
        # pb_frame =parent
        pb_frame.pack(expand=True, fill="x")
        super().__init__()
        bar_frame = Frame(pb_frame)
        bar_frame.pack(fill="x", side="top")
        bar_frame.columnconfigure(0, weight=1)
        self.progress_bar = Progressbar(bar_frame, length=300, mode="determinate")  # create progress bar
        self.progress_bar.grid(row=0, column=0, sticky="we")
        self.progress_label = tkinter.StringVar(value="0 %")
        self.label = Label(bar_frame, textvariable=self.progress_label)
        self.label.grid(row=0, column=0)
        # self.progress_bar.pack(expand=False, fill="x",side="top")
        self.pb_label_variable = tkinter.StringVar(value=self.label_text)
        self.pb_label = tkinter.Label(pb_frame, justify="right", textvariable=self.pb_label_variable)
        self.pb_label.pack(expand=False, fill="x", side="right")
        # self.pb_label.columnconfigure(0, weight=1)
        # self.pb_label.grid(row=1, column=0, sticky="e")
        logger.info("Initialized progress bar")

    def _update(self):

        if not self.timer:
            return
        if self.processed >= self.total:
            self.timer.stop()
        self.pb_label_variable.set(self.label_text)
        self.progress_label.set(f"{round(self.percentage, 2)}")

        self.progress_bar['value'] = self.percentage
        self.progress_bar.update()
