import copy
import logging
import tkinter
from tkinter.ttk import Treeview

from src.Common.loadedcomicinfo import LoadedComicInfo

logger = logging.getLogger()


class TreeviewWidget(Treeview):
    def __init__(self, *args, **kwargs):
        super(TreeviewWidget, self).__init__(*args, **kwargs)
        self.heading('#0', text='Click to select all files', command=self.select_all)
        # self.pack(expand=True, side="top")
        self.bind('<<TreeviewSelect>>', self._on_select)
        self._hook_items_inserted: list[callable] = []
        self._hook_items_selected: list[callable] = []
        self.content = {}
        self.prev_selection = None
        self.bind("<Button-3>", self.popup)
        self.ctx_menu = tkinter.Menu(self, tearoff=0)
        self.ctx_menu.add_command(label="{clicked_file}", state="disabled")
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="Open in Explorer", command=self.open_in_explorer)
        self.ctx_menu.add_command(label="Reset changes", command=self.reset_loadedcinfo_changes,state="disabled")


    def clear(self):
        self.delete(*self.get_children())

    def select_all(self, *_):
        for item in self.get_children():
            self.selection_add(item)

    def get_selected(self) -> list[LoadedComicInfo]:
        return [self.content.get(item) for item in self.selection()]

    def insert(self, loaded_cinfo: LoadedComicInfo, *args, **kwargs):
        super(TreeviewWidget, self).insert("", 'end', loaded_cinfo.file_path, text=loaded_cinfo.file_name, tags=("darkmode", "important" ),*args,
                                               **kwargs)
        self.content[loaded_cinfo.file_path] = loaded_cinfo
        # self._call_hook_item_inserted(loaded_cinfo)
        self.select_all()

    def _on_select(self, *_):
        prev_selection = copy.copy(self.prev_selection)
        selected = [self.content.get(item) for item in self.selection()]
        self.prev_selection = selected
        if not selected:
            return
        self._call_hook_item_selected(selected, prev_selection)

    ##################
    # Hook Stuff
    ##################
    def add_hook_item_selected(self, function: callable):
        self._hook_items_selected.append(function)

    def add_hook_item_inserted(self, function: callable):
        self._hook_items_inserted.append(function)

    def _call_hook_item_selected(self, loaded_cinfo_list: list[LoadedComicInfo], prev_selection):
        self._run_hook(self._hook_items_selected, loaded_cinfo_list, prev_selection)

    def _call_hook_item_inserted(self, loaded_comicinfo: LoadedComicInfo):
        self._run_hook(self._hook_items_inserted, [loaded_comicinfo])

    def popup(self, event):
        """action in event of button 3 on tree view"""
        # select row under mouse
        iid = self.identify_row(event.y)
        if iid:
            # mouse pointer over item
            self.selection_set(iid)
            self.ctx_menu.entryconfigure(0, label=iid)
            self.ctx_menu.entryconfigure(2,command=lambda x=iid: self.open_in_explorer(x))
            self.ctx_menu.post(event.x_root, event.y_root)
        else:
            # mouse pointer not over item
            # occurs when items do not fill frame
            # no action required
            pass

    def open_in_explorer(self, event=None):
        raise NotImplementedError()

    def reset_loadedcinfo_changes(self, event=None):
        raise NotImplementedError()

    def _run_hook(source: list[callable], *args):
        for hook_function in source:
            try:
                hook_function(*args)
            except:
                logger.exception("Error calling hook")

