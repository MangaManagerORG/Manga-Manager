import fnmatch
import glob
import os
import pathlib
import tkinter
import tkinter.ttk as ttk
from tkinter import filedialog

from MangaManager_ThePromidius.Common.utils import ShowPathTreeAsDict
from MangaManager_ThePromidius.MetadataManager.errors import NoFilesSelected
from src.MangaManager_ThePromidius.Common.GUI.widgets import ScrolledFrameWidget
from src.MangaManager_ThePromidius.Common.Templates.extension import Extension, ExtensionGUI
from src.MangaManager_ThePromidius.MetadataManager import comicinfo


def has_cbz(base_path,abspath, glob_pattern):
    for _, __, files in os.walk(abspath):
        for filename in files:
            # noinspection PyTypeChecker
            if fnmatch.fnmatch(pathlib.Path(base_path,filename), glob_pattern):
                return True
        break
    return False


class ExtensionApp(Extension):
    name = "Webp Converter"
    base_path: str
    glob: str = "**/*.cbz"
    selected_files: list[str]


    def process(self) -> comicinfo.ComicInfo:
        ...



class ExtensionAppGUI(ExtensionApp, ExtensionGUI):
    treeview_frame: ScrolledFrameWidget = None
    nodes: dict
    path: str = None
    base_path = None

    def select_base(self):
        self.base_path = filedialog.askdirectory()  # select directory
        self.selected_base_path.set(str(self.base_path))

    def _on_file(self, parent, file):
        self.tree.insert(self.nodes.get(str(parent.get("current"))), 'end', text=file, open=True)

    def _on_folder(self, parent_dic, folder):
        parent_path = str(pathlib.Path(parent_dic.get("current")))
        node = self.tree.insert(self.nodes[parent_path], 'end', text=folder, open=True)
        self.nodes[str(pathlib.Path(parent_path, folder))] = node

    def _clear(self):
        self.tree.delete(*self.tree.get_children())
        self.nodes = dict()

    def _set_input(self):
        self.glob = self.path_glob.get() or "*.cbz"
        os.chdir(self.base_path)
        self.selected_files = glob.glob(self.glob, recursive=True)

    def preview(self):
        if not self.base_path:
            raise NoFilesSelected()
        self._clear()
        self._set_input()
        abspath = os.path.abspath(self.base_path)
        node = self.tree.insert("", 'end', abspath, text=self.base_path, open=True)
        self.nodes[abspath] = node
        treeview = ShowPathTreeAsDict
        treeview.on_file = self._on_file
        treeview.on_subfolder = self._on_folder
        self.treeview_files = treeview(self.base_path, self.selected_files).get()

    def serve_gui(self, parentframe):
        frame = ScrolledFrameWidget(parentframe).create_frame()
        self.selected_base_path = tkinter.StringVar()

        tkinter.Button(frame, text="Select Base Directory", command=self.select_base).pack()
        self.base_path_entry = tkinter.Entry(frame, state="readonly", textvariable=self.selected_base_path)
        self.base_path_entry.pack()
        tkinter.Label(frame, text="Glob to apply:").pack(side="top")
        self.path_glob = tkinter.Entry(frame)
        self.path_glob.pack()

        tkinter.Button(frame, text="Preview selected files", command=self.preview).pack(side="top")

        self.tree = ttk.Treeview(frame)
        self.tree.heading('#0', text='Project tree', anchor='n')

        self.tree.pack(expand=True, fill="x", side="top")


if __name__ == '__main__':
    root = tkinter.Tk()
    app = ExtensionAppGUI()
    app.serve_gui(root)
    root.mainloop()
