from idlelib.tooltip import Hovertip
from tkinter import Frame, Label, Entry, Checkbutton, StringVar, BooleanVar

from src.MetadataManager.GUI.widgets import ComboBoxWidget
from src.Settings import SettingControl, SettingSection


class FormBundleWidget(Frame):
    label: Label
    input_widget: ComboBoxWidget | Checkbutton | Entry
    input_var: StringVar | BooleanVar
    # This is the frame that holds the bundle
    row: Frame
    control: SettingControl
    section: SettingSection
    validation_error: StringVar
    # Reference held so UI can render it
    validation_label: Label
    validation_row: Frame
    mapper_fn = None

    def __init__(self, master, mapper_fn, *_, **kwargs):
        super(FormBundleWidget, self).__init__(master, **kwargs)

        self.mapper_fn = mapper_fn

        self.row = Frame(master)
        self.row.pack(expand=True, fill="x")

        self.validation_row = Frame(master)
        self.validation_row.pack(expand=True, fill="x")

        self.pack(expand=True, fill='both', side='top')

    def with_label(self, title, tooltip=""):
        self.label = Label(master=self.row, text=title, width=30, justify="right", anchor="e")
        if tooltip:
            self.label.tooltip = Hovertip(self.label, tooltip, 20)

        self.label.pack(side="left")
        return self

    def with_input(self, control: SettingControl, section: SettingSection):
        entry, string_var = self.mapper_fn(self.row, control, section)
        self.control = control
        self.section = section
        self.input_widget = entry
        self.input_var = string_var

        return self

    def build(self):
        self.validation_error = StringVar()
        self.validation_error.set("")
        self.validation_label = Label(master=self.validation_row, width=30, justify="right", anchor="e",
                                      textvariable=self.validation_error, fg='red')

        self.validation_label.pack(side="left")
        self.validation_label.pack_forget()
        return self

    def validate(self):
        if self.control.validate is None:
            return True
        error = self.control.validate(self.control.key, str(self.input_var.get()))
        self.validation_error.set(error)

        has_error = error != ""

        if has_error:
            self.validation_label.pack()
        else:
            self.validation_label.pack_forget()

        return not has_error

    def format_output(self):
        if self.control.format_value is None:
            return str(self.input_var.get())
        return self.control.format_value(self.input_var.get())
