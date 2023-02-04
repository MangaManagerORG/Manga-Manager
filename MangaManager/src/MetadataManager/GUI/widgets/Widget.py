from idlelib.tooltip import Hovertip
from tkinter.ttk import Combobox, OptionMenu, Frame, Widget, Label

from src.MetadataManager.GUI.longtext import LongText
from src.MetadataManager.GUI.utils import validate_int


class Widget(Frame):
    validation: str | None = None
    widget_slave = None
    widget: Combobox | LongText | OptionMenu
    name: str
    NONE = "~~# None ##~~"

    def __init__(self, master):
        super(Widget, self).__init__(master)

    def set(self, value):
        if value is None:
            return
        if not self.validation:
            self.widget.set(value)
            return

        if value and validate_int(value):
            if self.validation == "rating" and (float(value) < 0 or float(value) > 10):
                return
            self.widget.set(str(int(value)))

    def set_default(self):
        self.widget.set("")

    def get(self):
        return self.widget.get()

    def pack(self, **kwargs) -> Widget:
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).pack(kwargs or {"fill": "both", "side": "top"})
        return self

    def grid(self, row=None, column=None, **kwargs) -> Widget:
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).grid(row=row, column=column, sticky="we", **kwargs)
        return self

    def set_label(self, text, tooltip=None):
        self.label = Label(self, text=text)
        if text:
            self.label.pack(side="top")
        if tooltip:
            self.label.configure(text=self.label.cget('text') + '  ⁱ')
            self.label.tooltip = Hovertip(self.label, tooltip, 20)