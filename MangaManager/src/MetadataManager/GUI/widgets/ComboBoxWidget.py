from tkinter import Widget
from tkinter.ttk import Combobox

from src.MetadataManager.GUI.utils import validate_int


class ComboBoxWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None, default="",
                 validation=None, tooltip: str = None):
        super(ComboBoxWidget, self).__init__(master)
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