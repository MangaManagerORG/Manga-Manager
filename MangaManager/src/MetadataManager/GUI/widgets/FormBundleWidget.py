from idlelib.tooltip import Hovertip
from tkinter import Frame, Label, Entry, Checkbutton

from src.MetadataManager.GUI.widgets import ComboBoxWidget


class FormBundleWidget(Frame):
    label: Label
    input_widget: ComboBoxWidget | Checkbutton | Entry
    # This is the frame that holds the bundle
    row: Frame


    def __init__(self, master, *_, **kwargs):
        super(FormBundleWidget, self).__init__(master, **kwargs)

        self.row = Frame(master)
        self.row.pack(expand=True, fill="x")

        self.pack(expand=False, fill='both', side='top')

    def with_label(self, title, tooltip=""):
        self.label = Label(master=self.row, text=title, width=30, justify="right", anchor="e")
        if tooltip:
            self.label.tooltip = Hovertip(self.label, tooltip, 20)

        self.label.pack(side="left")
        return self

    def with_input(self, control: ComboBoxWidget | Checkbutton | Entry, validation_method):

        return self

    def pack(self):
        return self.pack(expand=False, fill='both', side='top')