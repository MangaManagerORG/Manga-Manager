from __future__ import annotations

import copy
import logging
import re
import tkinter
from idlelib.tooltip import Hovertip
# from tkinter import Label
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox, OptionMenu, Progressbar, Treeview, Style, Frame, Label, LabelFrame

import _tkinter

from src import settings_class, MM_PATH
from src.Common.loadedcomicinfo import LoadedComicInfo
from src.Common.progressbar import ProgressBar
from src.Common.utils import open_folder
from src.MetadataManager import comicinfo
from src.MetadataManager.GUI.longtext import LongText
from src.MetadataManager.GUI.scrolledframe import ScrolledFrame
from src.settings import SettingItem

INT_PATTERN = re.compile("^-*\d*(?:,?\d+|\.?\d+)?$")
MULTIPLE_FILES_SELECTED = "Multiple Files Selected"
logger = logging.getLogger()


settings = settings_class.get_setting("main")


def validate_int(value) -> bool:
    """
    Validates if all the values in the string matches the int pattern
    :param value:
    :return: true if matches
    """
    ilegal_chars = [character for character in str(value) if not INT_PATTERN.match(character)]
    return not ilegal_chars


class ButtonWidget(tkinter.Button):
    def __init__(self, tooltip=None,image=None, *args, **kwargs):
        super(ButtonWidget, self).__init__(image=image, *args, **kwargs)

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

    def __setattr__(self, key, value):
        self.cinfo_tags.append(key)
        object.__setattr__(self, key, value)

    def clean_widgets(self):
        for widget_name in self.__dict__:
            widget = self.get_widget(widget_name)
            widget.set_default()
            if isinstance(widget, ComboBoxWidget):
                widget.widget['values'] = widget.default_vals or []

    def toggle_widgets(self,enabled=True):
        for widget_name in self.__dict__:
            widget = self.get_widget(widget_name)
            if isinstance(widget, OptionMenuWidget):
                widget.widget_slave.configure(state="normal" if enabled else "disabled")
            elif isinstance(widget, LongTextWidget):
                # widget.widget_slave.configure(state="normal" if enabled else "readonly")
                pass
            else:
                widget.widget.configure(state="normal" if enabled else "disabled")

    def get_tags(self):
        return [tag for tag in self.cinfo_tags]


class ControlManager:
    """
    """
    control_button_set = set()
    control_hooks = []  # Callables to call when it should lock or unlock

    def add(self, widget: tkinter.Widget):
        self.control_button_set.add(widget)

    def append(self, widget: tkinter.Widget):
        self.control_button_set.add(widget)

    def toggle(self, enabled=True):
        for widget in self.control_button_set:
            try:
                widget.configure(state="normal" if enabled else "disabled")
            except _tkinter.TclError as e:
                logger.exception("Unhandled exception")

    def lock(self):
        self.toggle(False)

    def unlock(self):
        self.toggle(True)


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
            if self.validation == "rating" and (float(value) < 0 or float(value) > 10):
                return
            self.widget.set(str(int(value)))

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
        if text:
            self.label.pack(side="top")
        if tooltip:
            self.label.configure(text=self.label.cget('text') + '  ⁱ')
            self.label.tooltip = Hovertip(self.label, tooltip, 20)


class ComboBoxWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None, default="",
                 validation=None, tooltip: str = None):
        super(ComboBoxWidget, self).__init__(master)
        # super(Widget, self).__init__()
        if label_text is None:
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


class AutocompleteComboboxWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None, force_validation_from_list = True, tooltip:str = None):
        super().__init__(master=master)
        self.name = cinfo_name
        self.default = ""
        self.set_label(label_text, tooltip)
        self.widget = Combobox(self, name=cinfo_name.lower(), values=default_values, style="Custom.TCombobox")
        if width is not None:
            self.widget.configure(width=width)

        self._completion_list = default_values or []
        self._hits = []
        self._hit_index = 0
        self.position = 0

        self.bind('<KeyRelease>', self.handle_keyrelease)
        self.widget['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.widget.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.widget.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.widget.delete(0, tkinter.END)
            self.widget.insert(0, self._hits[self._hit_index])
            self.widget.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.widget.delete(self.widget.index(tkinter.INSERT), tkinter.END)
            self.position = self.widget.index(tkinter.END)
        if event.keysym == "Left":
            if self.position < self.widget.index(tkinter.END):  # delete the selection
                self.widget.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.widget.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.widget.index(tkinter.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


class OptionMenuWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, max_width=None, default=None, values=None):

        if values is None:
            values = []
        if label_text is None:
            label_text = cinfo_name
        super(OptionMenuWidget, self).__init__(master)
        self.default = default
        self.name = cinfo_name
        self.set_label(label_text)
        # noinspection PyTypeChecker
        self.widget = tkinter.StringVar(self, name=cinfo_name, value=default)
        self.widget_slave: Combobox = Combobox(self, textvariable=self.widget)
        self.widget_slave.configure(state="readonly")
        self.update_listed_values(self.default,list(values))
        # noinspection PyUnresolvedReferences
        if max_width:
            self.widget_slave.configure(width=max_width)

    def update_listed_values(self, default_selected, values) -> None:
        self.widget_slave["values"] = list(values)
        self.widget_slave.set(default_selected)

    def get_options(self) -> list[str]:
        values_list = []
        match self.name:
            case "AgeRating":
                values_list = comicinfo.AgeRating.list()
            case "Format":
                values_list = list(comicinfo.format_list)
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
        self.update_listed_values("", self.get_options())


class LongTextWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, width: int = None):
        super(LongTextWidget, self).__init__(master)
        if label_text is None:
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
    def __init__(self, master, *_, **kwargs):
        super(ScrolledFrameWidget, self).__init__(master, **kwargs)
        self.configure(usemousewheel=True)
        self.paned_window = tkinter.PanedWindow(self.innerframe)
        self.paned_window.pack(fill="both", expand=True)
        self.pack(expand=True, fill='both', side='top')

    def create_frame(self,**kwargs):
        """Creates a subframe and packs it"""
        frame = Frame(self.paned_window)
        frame.pack(kwargs or {})
        # frame.pack()
        self.paned_window.add(frame)
        return frame




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


class SettingsWidgetManager:
    def parse_ui_settings_process(self):
        for stringvar in self.strings_vars:
            stringvar.linked_setting.value = str(stringvar.get())
        settings_class.save_settings()

    def __init__(self, parent):
        self.strings_vars: list[tkinter.Variable] = []
        settings_window = self.settings_window = tkinter.Toplevel(parent, pady=30, padx=30)
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
                     command=lambda x=None: open_folder(folder_path=MM_PATH)).pack()
        # for setting_section in settings_class.__dict__.sort(key=):
        self.settings_widget = {}
        for settings_section in settings_class.factory:
            section_class = settings_class.get_setting(settings_section)

            frame = LabelFrame(master=self.widgets_frame, text=settings_section)
            frame.pack(expand=True, fill="both")

            self.settings_widget[settings_section] = {}
            self.print_setting_entry(frame, section_class)
            center(settings_window)

    def print_setting_entry(self, parent_frame, section_class):
        for i, setting in enumerate(section_class.settings):

            row = tkinter.Frame(parent_frame)
            row.pack(expand=True, fill="x")
            label = Label(master=row, text=setting.name, width=30, justify="right", anchor="e")
            label.pack(side="left")
            if setting.tooltip:
                label.configure(text=label.cget('text') + '  ⁱ')
                label.tooltip = Hovertip(label, setting.tooltip, 20)

            if setting.type_ == "bool":
                value = True if setting.value else False
                string_var = SettingBolVar(value=value, name=f"{setting.section}.{setting.key}")
                entry = tkinter.Checkbutton(row, variable=string_var, onvalue=1, offvalue=0)
                entry.pack(side="left")
            elif setting.type_ == "optionmenu":
                string_var = SettingStringVar(value="default", name=f"{setting.section}.{setting.key}")
                entry = Combobox(master=row, textvariable=string_var, width=30, state="readonly")
                entry["values"] = setting.values
                entry.set(str(setting.value))
                entry.pack(side="left", expand=False, fill="x", padx=(5, 30))
                entry.set(setting.value)
                # entry.configure(state="readonly")

                ...
            else:
                string_var = SettingStringVar(value=setting.value, name=f"{setting.section}.{setting.key}")


                entry = tkinter.Entry(master=row, width=80, textvariable=string_var)
                entry.pack(side="right", expand=True, fill="x", padx=(5, 30))
            self.strings_vars.append(string_var)
            string_var.linked_setting = setting
            entry.setting_section = section_class._section_name
            entry.setting_name = setting
            self.settings_widget[section_class._section_name][setting] = entry
            match setting.type_:
                case "bool":
                    string_var.set(bool(setting))
                # case "optionmenu":
                    # string_var.set(setting.value)


def _run_hook(source: list[callable], *args):
    for hook_function in source:
        try:
            hook_function(*args)
        except:
            logger.exception("Error calling hook")


class TreeviewWidget(Treeview):
    def __init__(self, *args, **kwargs):
        super(TreeviewWidget, self).__init__(*args, **kwargs)
        self.heading('#0', text='Click to select all files', command=self.select_all)
        # self.pack(expand=True, side="top")
        self.bind('<<TreeviewSelect>>', self._on_select)
        self._hook_items_inserted: list[callable] = []
        self._hook_items_selected: list[callable] = []
        self.content = {}
        self.prev_selection = None
        self.bind("<Button-3>", self.popup)
        self.ctx_menu = tkinter.Menu(self, tearoff=0)
        self.ctx_menu.add_command(label="{clicked_file}", state="disabled")
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Open in Explorer", command=self.open_in_explorer)
        self.ctx_menu.add_command(label="Reset changes", command=self.reset_loadedcinfo_changes,state="disabled")


    def clear(self):
        self.delete(*self.get_children())

    def select_all(self, *_):
        for item in self.get_children():
            self.selection_add(item)

    def get_selected(self) -> list[LoadedComicInfo]:
        return [self.content.get(item) for item in self.selection()]

    def insert(self, loaded_cinfo: LoadedComicInfo, *args, **kwargs):
        super(TreeviewWidget, self).insert("", 'end', loaded_cinfo.file_path, text=loaded_cinfo.file_name, tags=("darkmode", "important" ),*args,
                                               **kwargs)
        self.content[loaded_cinfo.file_path] = loaded_cinfo
        # self._call_hook_item_inserted(loaded_cinfo)
        self.select_all()

    def _on_select(self, *_):
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

    def popup(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        iid = self.identify_row(event.y)
        if iid:
            # mouse pointer over item
            self.selection_set(iid)
            self.ctx_menu.entryconfigure(0, label=iid)
            self.ctx_menu.entryconfigure(2,command=lambda x=iid: self.open_in_explorer(x))
            self.ctx_menu.post(event.x_root, event.y_root)
        else:
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
            pass

    def open_in_explorer(self, event=None):
        raise NotImplementedError()

    def reset_loadedcinfo_changes(self, event=None):
        raise NotImplementedError()


class ProgressBarWidget(ProgressBar):
    def __init__(self, parent):
        pb_frame = Frame(parent)
        pb_frame.pack(expand=False, fill="x")
        super().__init__()

        self.style = Style(pb_frame)
        self.style.layout('text.Horizontal.TProgressbar',
                          [
                              ('Horizontal.Progressbar.trough',
                               {
                                   'children': [
                                       ('Horizontal.Progressbar.pbar',
                                        {
                                            'side': 'left',
                                            'sticky': 'ns'
                                        }
                                        )
                                   ],
                                   'sticky': 'nswe'
                               }
                               ),
                              ('Horizontal.Progressbar.label',
                               {
                                   'sticky': 'nswe'
                               }
                               )
                          ]
                          )
        self.style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')

        self.progress_bar = Progressbar(pb_frame, length=10, style='text.Horizontal.TProgressbar',
                                            mode="determinate")  # create progress bar
        self.progress_bar.pack(expand=False, fill="x",side="top")
        self.pb_label_variable = tkinter.StringVar(value=self.label_text)
        self.pb_label = Label(pb_frame, justify="right", textvariable=self.pb_label_variable)
        self.pb_label.pack(expand=False, fill="x", side="right")
        logger.info("Initialized progress bar")

    def update_progress_label(self):
        self.pb_label_variable.set(self.label_text)

    def _update(self):

        if not self.timer:
            return
        if self.processed >= self.total:
            self.timer.stop()
        self.update_progress_label()
        self.style.configure('text.Horizontal.TProgressbar',
                             text='{:g} %'.format(round(self.percentage, 2)))  # update label
        self.progress_bar['value'] = self.percentage
        self.progress_bar.update()
