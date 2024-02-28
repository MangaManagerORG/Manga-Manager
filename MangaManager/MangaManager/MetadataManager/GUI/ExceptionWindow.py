import logging
import tkinter
import traceback
from tkinter import Frame
from tkinter.font import Font
from tkinter.ttk import Treeview, Style

from MangaManager.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo

logger = logging.getLogger()


class ExceptionHandler(logging.Handler):
    def __init__(self, tree_widget):
        logging.Handler.__init__(self)
        self.tree_widget = tree_widget

    def emit(self, record):
        ei = record.exc_info
        parent_id = self.tree_widget.insert("", 'end', text=f"{record.levelname:12s} {record.msg}")
        self.tree_widget.dict[parent_id] = record
        if "processed_filename" in record.__dict__:
            self.tree_widget.insert(parent_id, 'end', text=f"Filename: '{record.processed_filename}'")
        if "lcinfo" in record.__dict__:
            lcinfo: LoadedComicInfo = record.__dict__["lcinfo"]
            self.tree_widget.insert(parent_id, 'end', text=f"Filename: '{lcinfo.file_name}'")
        if ei:
            stack_tab = self.tree_widget.insert(parent_id, 'end', text="Stack Trace info", open=False)
            exc_type, exc_value, exc_traceback = ei
            tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            for string in tb_str.split("\n"):
                self.tree_widget.insert(stack_tab, 'end', text=string)


class ExceptionFrame(Frame):
    def __init__(self, master=None, is_test=False, **kwargs):
        Frame.__init__(self, master, **kwargs)
        ter_font = Font(family="Consolas", size=6)
        style = Style()
        style.configure('Terminal.Treeview', font=ter_font)
        self.tree = Treeview(self, style='Terminal.Treeview', show="tree")
        self.tree.style = style
        self.tree.dict = dict()
        self.tree.pack(expand=True, fill='both')
        self.selected_logging_level = tkinter.StringVar(self)
        self.selected_logging_level.set("WARNING")
        self.input_type = tkinter.OptionMenu(self,self.selected_logging_level,*("WARNING", "ERROR", "INFO", "DEBUG","TRACE"))
        self.input_type.pack(side="left", fill="y")

        tkinter.Button(self,text="Clear logs",command=self.clear_treeview).pack(side="left", fill="y")

        self.selected_logging_level.trace("w", self.update_handler_level)
        handler = self.handler = ExceptionHandler(self.tree)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        handler.setLevel(logging.WARNING)

        if not is_test:
            logger.addHandler(handler)
        # Pump logging events not loaded with the ui
            logger.debug("Removing unpumped handler")
            logger.removeHandler(logging.umpumped_handler)
            while logging.umpumped_events:
                record = logging.umpumped_events.pop()
                handler.emit(record)

    def update_handler_level(self,*args):
        self.handler.setLevel(logging.getLevelName(self.selected_logging_level.get()))
        logger.info(f"Selected '{self.selected_logging_level.get()}' as UI logging level",extra={"ui":True})

    def clear_treeview(self):
        # Delete all items in the Treeview
        self.tree.delete(*self.tree.get_children())

    def __del__(self):
        logger.removeHandler(self.handler)
