import tkinter
from tkinter.ttk import Combobox

from src.Settings import SettingControl, SettingControlType, SettingSection


def setting_control_to_widget(parent_frame: tkinter.Frame, control: SettingControl, section: SettingSection):
    match control.control_type:
        case SettingControlType.Text:
            string_var = tkinter.StringVar(value=control.value, name=f"{section.pretty_name}.{control.key}")
            entry = tkinter.Entry(master=parent_frame, width=80, textvariable=string_var)
            entry.pack(side="right", expand=True, fill="x", padx=(5, 30))
        case SettingControlType.Bool:
            value = control.value == 'True'
            string_var = tkinter.BooleanVar(value=value, name=f"{section.pretty_name}.{control.key}")
            entry = tkinter.Checkbutton(parent_frame, variable=string_var, onvalue=1, offvalue=0)
            entry.pack(side="left")
        case SettingControlType.Options:
            string_var = tkinter.StringVar(value="default", name=f"{section.pretty_name}.{control.key}")
            entry = Combobox(master=parent_frame, textvariable=string_var, width=30, state="readonly")
            entry["values"] = control.values
            entry.set(str(control.value))
            entry.pack(side="left", expand=False, fill="x", padx=(5, 30))
            entry.set(control.value)

    return entry, string_var
