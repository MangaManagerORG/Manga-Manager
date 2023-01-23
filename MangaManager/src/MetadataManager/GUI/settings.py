from __future__ import annotations

import tkinter
from idlelib.tooltip import Hovertip
from tkinter.ttk import LabelFrame, Label, Combobox

from src import settings_class, MM_PATH
from src.Common.utils import open_folder
from src.MetadataManager.GUI.widgets import ScrolledFrameWidget, ButtonWidget, center
from src.settings import SettingItem


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

        # main_frame = ScrolledFrameWidget(settings_window, scrolltype="vertical").create_frame(expand=True,fill="both")
        main_frame = tkinter.Frame(settings_window)
        main_frame.pack(fill="both")
        self.widgets_frame = tkinter.Frame(main_frame, pady=30, padx=30)
        self.widgets_frame.pack(fill="y",expand=True)
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
        frame = Label(master=control_frame, text="\nNote: Fields marked with * needs a restart to take effect")
        frame.pack(expand=True, fill="both")
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


class SettingBolVar(tkinter.BooleanVar):

    def __init__(self, *args, **kwargs):
        super(SettingBolVar, self).__init__(*args, **kwargs)
        self.linked_setting: SettingItem = None


class SettingStringVar(tkinter.StringVar):

    def __init__(self, *args, **kwargs):
        super(SettingStringVar, self).__init__(*args, **kwargs)
        self.linked_setting: SettingItem = None
