import logging
import tkinter

import _tkinter

logger = logging.getLogger()


class ControlManager:
    """
    """
    control_button_set = set()
    control_hooks = []  # Callables to call when it should lock or unlock

    def add(self, widget: tkinter.Widget):
        self.control_button_set.add(widget)

    def append(self, widget: tkinter.Widget):
        self.control_button_set.add(widget)

    def toggle(self, enabled=True):
        for widget in self.control_button_set:
            try:
                widget.configure(state="normal" if enabled else "disabled")
            except _tkinter.TclError:
                logger.exception("Unhandled exception updating widget state", exc_info=False)

    def lock(self):
        self.toggle(False)

    def unlock(self):
        self.toggle(True)








