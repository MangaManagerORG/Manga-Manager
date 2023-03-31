from tkinter.scrolledtext import ScrolledText
from tkinter import Text, INSERT, END

from .MMWidget import MMWidget


class LongTextWidget(MMWidget):
    def __init__(self, master, cinfo_name, label_text=None, width: int = None):
        super(LongTextWidget, self).__init__(master)
        if label_text is None:
            label_text = cinfo_name
        self.set_label(label_text)
        self.default = ""
        self.name = cinfo_name
        # Input
        self.widget_slave = ScrolledText(self)
        self.widget_slave.configure(height='5', width=width)
        self.widget_slave.pack(fill='both', side='top')

        self.widget = _LongText(name=cinfo_name)
        self.widget.linked_text_field = self.widget_slave


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