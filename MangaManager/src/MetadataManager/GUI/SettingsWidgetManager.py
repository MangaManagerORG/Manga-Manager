from __future__ import annotations

import tkinter
from idlelib.tooltip import Hovertip
from tkinter.ttk import LabelFrame, Label, Combobox

from main import providers
from src import MM_PATH
from src.Common.utils import open_folder
from src.MetadataManager.GUI.widgets import ButtonWidget, center
from src.Settings import default_settings
from src.Settings.DefaultSettings import SettingHeading
from src.Settings.SettingControlType import SettingControlType
from src.Settings.Settings import Settings


class SettingsWidgetManager:
    def save_settings(self):
        """
        Saves the settings from the GUI to Setting provider and extensions that dynamically loaded their settings
        """
        for setting_value in self.strings_vars:
            if setting_value.linked_setting:
                Settings().set(setting_value.linked_section.key, setting_value.linked_setting.key, str(setting_value.get()))

        # Save Extensions
        for provider in providers:
            provider.save_settings([lambda: (setting.linked_setting, setting.get()) for setting in self.strings_vars])

        Settings().save()

    def __init__(self, parent):
        self.strings_vars: list[tkinter.Variable] = []
        settings_window = self.settings_window = tkinter.Toplevel(parent, pady=30, padx=30)
        settings_window.geometry("900x420")
        settings_window.title("Settings")

        main_frame = tkinter.Frame(settings_window)
        main_frame.pack(fill="both")
        self.widgets_frame = tkinter.Frame(main_frame, pady=30, padx=30)
        self.widgets_frame.pack(fill="y", expand=True)
        control_frame = tkinter.Frame(settings_window)
        control_frame.pack()
        ButtonWidget(master=control_frame, text="Save", tooltip="Saves the settings to the config file",
                     command=self.save_settings).pack()
        ButtonWidget(master=control_frame, text="Open Settings Folder",
                     tooltip="Opens the folder where Manga Manager stores it's files",
                     command=lambda x=None: open_folder(folder_path=MM_PATH)).pack()

        # TODO: Refactor this into a FrameBuilder
        self.settings_widget = {}
        for setting_section in default_settings:
            section = default_settings[setting_section]

            print('Setting up settings for ' + section.pretty_name)
            frame = LabelFrame(master=self.widgets_frame, text=section.pretty_name)
            frame.pack(expand=True, fill="both")

            self.settings_widget[section.pretty_name] = {}
            self.build_setting_entries(frame, section.values, section)

        for provider in providers:
            settings = provider.settings
            for section in settings:
                print('Setting up settings for ' + provider.name)
                frame = LabelFrame(master=self.widgets_frame, text=section.pretty_name)
                frame.pack(expand=True, fill="both")


                self.settings_widget[default_settings[SettingHeading.ExternalSources].pretty_name][section.pretty_name] = {}
                self.build_setting_entries(frame, section.values, section)

        center(settings_window)
        frame = Label(master=control_frame, text="\nNote: Fields marked with * need a restart to take effect")
        frame.pack(expand=True, fill="both")

    def build_setting_entry(self, parent_frame, control, section):
        row = tkinter.Frame(parent_frame)
        row.pack(expand=True, fill="x")
        label = Label(master=row, text=control.name, width=30, justify="right", anchor="e")
        label.pack(side="left")
        if control.tooltip:
            label.configure(text=label.cget('text') + '  ⁱ')
            label.tooltip = Hovertip(label, control.tooltip, 20)

        control_type = control.type_
        if control_type == SettingControlType.Bool:
            value = True if control.value else False
            string_var = tkinter.BooleanVar(value=value, name=f"{section.pretty_name}.{control.key}")
            entry = tkinter.Checkbutton(row, variable=string_var, onvalue=1, offvalue=0)
            entry.pack(side="left")
        elif control_type == SettingControlType.Options:
            string_var = tkinter.StringVar(value="default", name=f"{section.pretty_name}.{control.key}")
            entry = Combobox(master=row, textvariable=string_var, width=30, state="readonly")
            entry["values"] = control.value
            entry.set(str(control.value))
            entry.pack(side="left", expand=False, fill="x", padx=(5, 30))
            entry.set(control.value)
        else:
            string_var = tkinter.StringVar(value=control.value, name=f"{section.pretty_name}.{control.key}")
            entry = tkinter.Entry(master=row, width=80, textvariable=string_var)
            entry.pack(side="right", expand=True, fill="x", padx=(5, 30))

        entry.setting_section = section.pretty_name
        string_var.linked_setting = control
        string_var.linked_section = section
        self.strings_vars.append(string_var)

    def build_setting_entries(self, parent_frame, settings, section):
        for i, setting in enumerate(settings):
            self.build_setting_entry(parent_frame, setting, section)
