import tkinter
from .MMWidget import MMWidget
from tkinter.ttk import Combobox


class AutocompleteComboboxWidget(MMWidget):
    def __init__(self, master, cinfo_name, label_text=None, default_values=None, width=None,
                 force_validation_from_list = True, tooltip:str = None):
        super(AutocompleteComboboxWidget, self).__init__(master=master)
        self.name = cinfo_name
        self.default = ""
        self.set_label(label_text, tooltip)
        self.widget = Combobox(self, name=cinfo_name.lower(), values=default_values, style="Custom.TCombobox")
        if width is not None:
            self.widget.configure(width=width)

        self._completion_list = default_values or []
        self._hits = []
        self._hit_index = 0
        self.position = 0

        self.bind('<KeyRelease>', self.handle_keyrelease)
        self.widget['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.widget.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.widget.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.widget.delete(0, tkinter.END)
            self.widget.insert(0, self._hits[self._hit_index])
            self.widget.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.widget.delete(self.widget.index(tkinter.INSERT), tkinter.END)
            self.position = self.widget.index(tkinter.END)
        if event.keysym == "Left":
            if self.position < self.widget.index(tkinter.END):  # delete the selection
                self.widget.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.widget.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.widget.index(tkinter.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion