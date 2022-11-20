from __future__ import annotations

import os.path
import re
import tkinter
from idlelib.tooltip import Hovertip
from os.path import basename
from tkinter import OptionMenu, Frame, Label
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox

from PIL import UnidentifiedImageError

from MangaManager_ThePromidius import settings_class
from .models import LongText
from .scrolledframe import ScrolledFrame
from ...MetadataManager.cbz_handler import LoadedComicInfo

INT_PATTERN = re.compile("^-?\d+(?:,?\d+|\.?\d+)?$")


def validate_int(value):
    ilegal_chars = [character for character in str(value) if not INT_PATTERN.match(character)]
    # print(f"Ilegal chars: {ilegal_chars}")
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
            widget.set(widget.default)
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = []

    def get_tags(self):
        return [tag for tag in self.__dict__]


class Widget(Frame):
    validation: str | None = None
    widget_slave = None
    widget: Combobox | LongText | OptionMenu
    name: str

    def __init__(self, master):
        super(Widget, self).__init__(master)

    def set(self, value):
        if not value:
            return
        if not self.validation:
            self.widget.set(value)
            return
        if validate_int(value):
            if self.validation == "rating" and float(value) < 0 or float(value) > 10:
                return
            self.widget.set(value)

    def get(self):
        return self.widget.get()

    def pack(self) -> Widget:
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).pack(fill='both', side='top')
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
    def __init__(self, master, cinfo_name, label_text=None, default=None, *values):
        if not label_text:
            label_text = cinfo_name
        super(OptionMenuWidget, self).__init__(master)
        if not label_text:
            label_text = cinfo_name
        self.default = default
        self.name = cinfo_name
        # Label:
        self.set_label(label_text)
        # Input:
        # noinspection PyTypeChecker
        self.widget = tkinter.StringVar(name=cinfo_name, value=default)
        self.widget_slave: OptionMenu = OptionMenu(self, self.widget, *values)


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


class ListboxWidget(tkinter.Listbox):
    def __init__(self, *args, **kwargs):
        self.content = {}
        super(ListboxWidget, self).__init__(*args, **kwargs)
        self.bind('<<ListboxSelect>>', self.on_select)

    def insert(self, loadedcinfo: LoadedComicInfo, *args, **kwargs) -> None:
        index = self.content.__len__()
        super(ListboxWidget, self).insert(index, os.path.basename(loadedcinfo.file_path))
        self.content[index] = loadedcinfo

        self.update_cover_image(loadedcinfo)

    def on_select(self, event: tkinter.Event):
        if not event.widget.curselection():
            return
        index = int(event.widget.curselection()[0])
        loadedcinfo: LoadedComicInfo = self.content.get(index)
        print('You selected item %d: "%s"' % (index, loadedcinfo.file_path))
        self.update_cover_image(loadedcinfo)

    def update_cover_image(self, loadedcomicinfo: LoadedComicInfo):
        ...


class CoverFrame(tkinter.LabelFrame):
    canvas_image = None

    def __init__(self, master):
        super(CoverFrame, self).__init__(master)
        self.configure(pady=5)
        canvas_frame = self
        # canvas_frame.pack(expand=False)
        self.cover_subtitle = tkinter.Label(canvas_frame)
        self.cover_subtitle.configure(text='No file selected', width=25, compound="right", justify="left")
        # self.cover_subtitle.pack(expand=False)
        self.cover_subtitle.grid(row=0, sticky="w")
        self.canvas = tkinter.Canvas(canvas_frame)
        self.canvas.configure(background='#878787', height='260', width='190')
        self.canvas.grid(column=0, row=1)

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
        self.create_canvas_image()
        self.update_cover_button.grid_remove()
        return

    def update_cover_image(self, loadedcomicinfo: LoadedComicInfo):
        if not loadedcomicinfo.cached_image:
            self.clear()
        else:
            self.update_cover_button.grid(column=0, row=1)
        self.canvas.itemconfig(self.canvas_image, image=loadedcomicinfo.cached_image)
        self.cover_subtitle.configure(text=basename(loadedcomicinfo.file_path))
        # , image = loadedcomicinfo.cached_image

    def create_canvas_image(self):
        # self.update_cover_button.grid_remove() - Change to update button text to change cover
        try:
            self.canvas_image = self.canvas.create_image(0, 0, anchor=tkinter.NW)
        except UnidentifiedImageError as e:
            ...
            # mb.showerror("File is not a valid image", f"The file {image_path} is not a valid image file",
            #              parent=self.master)
            # logger.error(f"UnidentifiedImageError - Image file: '{image_path}'")

            # self.update_cover_button.configure(text="Select covers", state="normal")
            # self.update_cover_button.grid()

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


class SettingsWidgetManager:
    def __init__(self, parent):
        settings_window = tkinter.Toplevel(parent, pady=30, padx=30)
        settings_window.title("Settings")
        self.widgets_frame = tkinter.Frame(settings_window, pady=30, padx=30)
        self.widgets_frame.pack()
        control_frame = tkinter.Frame(settings_window)
        control_frame.pack()
        ButtonWidget(master=control_frame, text="Save", tooltip="Saves the settings to the config file",
                     command=self.save).pack()
        # for setting_section in settings_class.__dict__.sort(key=):
        self.settings_widget = {}
        for settings_section in sorted(settings_class.__dict__, key=lambda k: settings_class.__dict__[k].name.lower()):
            frame = tkinter.LabelFrame(master=self.widgets_frame, text=settings_section)
            frame.pack(expand=True, fill="both", ipady=15)
            settings_section_class = settings_class.get_setion(settings_section)
            self.settings_widget[settings_section] = {}
            for i, setting in enumerate(settings_section_class.__dict__):
                row = tkinter.Frame(frame)
                row.pack(expand=True, fill="x")
                tkinter.Label(master=row, text=setting, width=20, justify="right", anchor="e").pack(side="left")
                entry = tkinter.Entry(master=row, width=80)
                entry.setting_section = settings_section
                entry.setting_name = setting
                self.settings_widget[settings_section][setting] = entry
                entry.pack(side="right", expand=True, fill="x", padx=(5, 30))
                entry.insert(0, settings_section_class.get_value(setting))
        center(settings_window)

    def save(self):
        for setting_section in self.settings_widget:
            set_class = settings_class.get_setion(setting_section)
            for config in self.settings_widget.get(setting_section):
                entry_data = self.settings_widget.get(setting_section).get(config).get()
                set_class.set_value(config,entry_data)
        settings_class.write()

