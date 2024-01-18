import logging
import tkinter
from tkinter.ttk import Combobox
from ComicInfo.models import AgeRating, Formats, YesNo, Manga
from .MMWidget import MMWidget

logger = logging.getLogger()


class OptionMenuWidget(MMWidget):
    def __init__(self, master: tkinter.Frame, cinfo_name, label_text=None, width=None, max_width=None, default=None, values=None):
        super(OptionMenuWidget, self).__init__(master=master,name=cinfo_name.lower())
        if values is None:
            values = []
        if label_text is None:
            label_text = cinfo_name
        self.default = default
        self.name = cinfo_name
        self.set_label(label_text)
        # noinspection PyTypeChecker
        self.widget = tkinter.StringVar(self, name=cinfo_name, value=default)
        self.widget_slave: Combobox = Combobox(self, textvariable=self.widget)
        self.widget_slave.configure(state="readonly")
        if width:
            self.widget_slave.configure(width=width)
        self.update_listed_values(self.default, list(values))
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
                values_list = AgeRating.list()
            case "Format":
                values_list = list(Formats)
            case "BlackAndWhite":
                values_list = YesNo.list()
            case "Manga":
                values_list = Manga.list()
            case _:
                logger.error(f"Unhandled error. '{self.name}' is not a registered widget which can extract options from")
        return values_list

    def append_first(self, value: str):
        self.update_listed_values(value, [value] + self.get_options())

    def remove_first(self):
        self.update_listed_values("", self.get_options())
