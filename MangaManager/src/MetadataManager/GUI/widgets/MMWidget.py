from idlelib.tooltip import Hovertip
from tkinter.ttk import Combobox, OptionMenu, Frame, Label
from tkinter import Text, INSERT, END

from src.MetadataManager.GUI.utils import validate_int

# This class is used for LongTextWidget but it itself isn't technically a widget.
# We have it here as MM needs it but LongTextWidget needs MMWidget
class _LongText:
    """
    Helper class to have a multi line summary input
    """

    linked_text_field: Text | None = None
    name: str
    _value: str = ""

    def __init__(self, name=None):
        if name:
            self.name = name

    def set(self, value: str):
        """
        Sets the text to be displayed in the input field
        :param value: The text to be displayed
        :return:
        """
        if not self.linked_text_field:  # If it's not defined then UI is not being use. Store value in class variable.
            self._value = value
            return  # self._value
        self.linked_text_field.delete(1.0, END)
        self.linked_text_field.insert(INSERT, value)

    def clear(self):
        """
        Clears the input text and sets it to empty string
        :return:
        """
        if not self.linked_text_field:
            self._value = ""
            return
        self.linked_text_field.delete(1.0, END)

    def get(self) -> str:
        """
        Returns the value in the input field
        :return:
        """
        if not self.linked_text_field:  # If it's not defined then UI is not being use. Store value in class variable.
            return self._value

        return self.linked_text_field.get(index1="1.0", index2='end-1c')

    def __str__(self):
        return self.name

class MMWidget(Frame):
    validation: str | None = None
    widget_slave = None
    widget: Combobox | _LongText | OptionMenu
    name: str
    NONE = "~~# None ##~~"

    def __init__(self, master,name):
        super(MMWidget, self).__init__(master,name=name)

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

    def pack(self, **kwargs):
        widget = self.widget_slave or self.widget
        widget.pack(fill="both", side="top")

        super(Frame, self).pack(kwargs or {"fill": "both", "side": "top"})
        return self

    def grid(self, row=None, column=None, **kwargs):
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