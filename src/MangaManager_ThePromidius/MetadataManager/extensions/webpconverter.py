import fnmatch
import os
import tkinter
# encoding: utf-8
import tkinter.ttk as ttk
from tkinter import filedialog

from MangaManager_ThePromidius.Common.GUI.widgets import ScrolledFrameWidget
from MangaManager_ThePromidius.Common.Templates.extension import Extension
from MangaManager_ThePromidius.MetadataManager import comicinfo


def has_cbz(abspath, glob):
    for root, dirs, files in os.walk(abspath):
        for filename in files:
            if fnmatch.fnmatch(filename, glob):
                return True


class ExtensionApp(Extension):
    name = "Webp Converter"
    treeview_frame: ScrolledFrameWidget = None
    glob: str
    nodes = dict()
    path: str = None
    path_has_cbz = None
    def process(self) -> comicinfo.ComicInfo:
        pass

    def select_base(self):
        self.base_path = filedialog.askdirectory()  # select directory
        self.selected_base_path.set(str(self.base_path))

    def preview(self):
        # TODO: clear tree and insert in it
        self.path = self.selected_base_path.get()
        abspath = os.path.abspath(self.path)
        self.tree.delete(*self.tree.get_children())
        self._insert_node('', abspath, abspath,isInitial=True)
        # self._open_node()


        # App(self.treeview_frame, self.base_path or os.getcwd(), self.path_glob.get().get() or '*.cbz')
    # def preview_selected(self):
    #     for root, dirnames, filenames in os.walk(self.selected_base_path):
    #         for filename in fnmatch.filter(filenames, self.path_glob.get().get()):

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

        if not self.nodes:
            self.tree.heading('#0', text="No cbz files found in nested subfolders.")
        self.tree.bind('<<TreeviewOpen>>', self._open_node)




    def _insert_node(self, parent, text, abspath,isInitial=False):
        glob = self.path_glob.get() or '*.cbz'
        if isInitial:
            self.path_has_cbz = has_cbz(abspath, glob)
        if fnmatch.fnmatch(abspath, glob):
            node = self.tree.insert(parent, 'end', text=text, open=False)

        if os.path.isdir(abspath):
            if not self.path_has_cbz or not has_cbz(abspath, glob):
                return
            node = self.tree.insert(parent, 'end', text=text, open=False)
            self.nodes[node] = abspath
            self.tree.insert(node, 'end')

    def _open_node(self, event):
        node = self.tree.focus()
        abspath = self.nodes.pop(node, None)
        if abspath:
            self.tree.delete(*self.tree.get_children(node))
            for p in os.listdir(abspath):
                self._insert_node(node, p, os.path.join(abspath, p))


if __name__ == '__main__':
    root = tkinter.Tk()
    app = ExtensionApp()
    app.serve_gui(root)
    root.mainloop()
