from __future__ import annotations

import re
import tkinter
from tkinter import OptionMenu, Frame, Label
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox

from .models import LongText
from .scrolledframe import ScrolledFrame


def _place_label(frame, text):
    setattr(frame, "label", Label(frame, text=text))
    getattr(frame, "label").pack(side="top")


INT_PATTERN = re.compile("^-?\d+(?:,?\d+|\.?\d+)?$")


def validate_int(value):
    ilegal_chars = [character for character in str(value) if not INT_PATTERN.match(character)]
    # print(f"Ilegal chars: {ilegal_chars}")
    return not ilegal_chars


class WidgetManager:
    cinfo_tags:list[str] = list()

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


class ComboBoxWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None, default="",
                 validation=None):
        super(ComboBoxWidget, self).__init__(master)
        # super(Widget, self).__init__()
        if not label_text:
            label_text = cinfo_name
        self.name = cinfo_name
        self.default = default
        # Label:
        _place_label(self, label_text)

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
        _place_label(self, label_text)
        # Input:
        # noinspection PyTypeChecker
        self.widget = tkinter.StringVar(name=cinfo_name, value=default)
        self.widget_slave: OptionMenu = OptionMenu(self, self.widget, *values)


class LongTextWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, width: int = None):
        super(LongTextWidget, self).__init__(master)
        if not label_text:
            label_text = cinfo_name
        _place_label(self, label_text)
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
        self.pack(expand=1, fill='both', side='top')

    def create_frame(self):
        frame = Frame(self.paned_window)
        frame.pack()
        self.paned_window.add(frame)
        return frame
