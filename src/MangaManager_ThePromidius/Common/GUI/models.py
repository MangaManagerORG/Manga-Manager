from tkinter import Text, INSERT, END


class LongText:
    """
    Helper class to have a multi line summary input
    """

    linked_text_field: Text = None
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
