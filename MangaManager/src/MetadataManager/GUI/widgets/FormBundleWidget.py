from idlelib.tooltip import Hovertip
from tkinter import Frame, Label, Entry, Checkbutton, StringVar, BooleanVar

from src.MetadataManager.GUI.SettingWidgetConverter import setting_control_to_widget
from src.MetadataManager.GUI.widgets import ComboBoxWidget
from src.Settings import SettingControl, SettingSection


class FormBundleWidget(Frame):
    label: Label
    input_widget: ComboBoxWidget | Checkbutton | Entry
    input_var: StringVar | BooleanVar
    # This is the frame that holds the bundle
    row: Frame

    def __init__(self, master, *_, **kwargs):
        super(FormBundleWidget, self).__init__(master, **kwargs)

        self.row = Frame(master)
        self.row.pack(expand=True, fill="x")

        self.pack(expand=True, fill='both', side='top')

    def with_label(self, title, tooltip=""):
        self.label = Label(master=self.row, text=title, width=30, justify="right", anchor="e")
        if tooltip:
            self.label.tooltip = Hovertip(self.label, tooltip, 20)

        self.label.pack(side="left")
        return self

    def with_input(self, control: SettingControl, section: SettingSection):
        entry, string_var = setting_control_to_widget(self.row, control, section)
        self.input_widget = entry
        self.input_var = string_var
        return self

    def build(self):
        #self.pack(expand=False, fill='both', side='top')
        return self
