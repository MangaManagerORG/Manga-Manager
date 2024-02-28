from tkinter.ttk import Combobox

from MangaManager.MetadataManager.GUI.utils import validate_int
from .MMWidget import MMWidget


class ComboBoxWidget(MMWidget):
    def __init__(self, master, cinfo_name:str, label_text=None, default_values=None, width=None, default="",
                 validation=None, tooltip: str = None):

        super(ComboBoxWidget, self).__init__(master=master,name=cinfo_name.lower())

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
