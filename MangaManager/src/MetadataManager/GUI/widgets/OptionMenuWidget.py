from tkinter import Widget


class OptionMenuWidget(Widget):
    def __init__(self, master, cinfo_name, label_text=None,width=None, max_width=None, default=None, values=None):
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
        if width:
            self.widget_slave.configure(width=width)
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
