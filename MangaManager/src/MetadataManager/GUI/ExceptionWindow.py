import logging
import traceback
from tkinter import Frame
from tkinter.font import Font
from tkinter.ttk import Treeview, Style
logger = logging.getLogger()
import sys  # hack for logging in unit tests
class ExceptionHandler(logging.Handler):
    def __init__(self, tree_widget):
        logging.Handler.__init__(self)
        self.tree_widget = tree_widget

    def emit(self, record):
        ei = record.exc_info
        parent_id = self.tree_widget.insert("", 'end', text=f"{record.levelname:12s} {record.msg}")
        self.tree_widget.dict[parent_id] = record
        if ei:
            exc_type, exc_value, exc_traceback = ei
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            for string in tb_str.split("\n"):
                self.tree_widget.insert(parent_id, 'end', text=string)


class ExceptionFrame(Frame):
    def __init__(self, master=None, **kwargs):
        Frame.__init__(self, master, **kwargs)
        ter_font = Font(family="Consolas", size=6)
        style = Style()
        style.configure('Terminal.Treeview', font=ter_font)
        self.tree = Treeview(self, style='Terminal.Treeview', show="tree")
        self.tree.style = style
        self.tree.dict = dict()
        self.tree.pack(expand=True, fill='both')
        self.tree["columns"] = ("#0")
        self.tree.column("#0", width=200, anchor='w')
        # self.tree.heading("traceback", text="Traceback")
        handler = self.handler = ExceptionHandler(self.tree)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.WARNING)

        if 'unittest' not in sys.modules.keys():  # hack for logging in unit tests
            logger.addHandler(handler)

    def __del__(self):
        logger.removeHandler(self.handler)
