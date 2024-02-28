from __future__ import annotations

import glob
import logging
import os
import pathlib
import threading
import tkinter
import tkinter.ttk as ttk
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tkinter import filedialog

from Extensions.IExtensionApp import IExtensionApp
from MangaManager.Common.utils import ShowPathTreeAsDict
from MangaManager.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from MangaManager.MetadataManager.GUI.widgets import ScrolledFrameWidget, ProgressBarWidget


logger = logging.getLogger()


def start_processing(_selected_files, _progress_bar):
    processing_thread = threading.Thread(target=_run_process, args=(_selected_files, _progress_bar))
    processing_thread.start()


def _run_process(list_of_files, progress_bar: ProgressBarWidget):
    for file in list_of_files:

        logger.info(f"[Extension][WebpConvert] Processing file",
                    extra={"processed_filename": file})
        try:
            # time.sleep(20)
            LoadedComicInfo(file, load_default_metadata=False).convert_to_webp()
            progress_bar.increase_processed()
        except Exception:
            logger.exception(f"Failed to convert to webp '{file}'")
            progress_bar.increase_failed()
    progress_bar.running = False


class WebpConverter(IExtensionApp):
    name = "Webp Converter"
    embedded_ui = True

    base_path: str = ""
    glob: str = "**/*.cbz"
    _selected_files: list[str | pathlib.Path] = []
    treeview_frame: ScrolledFrameWidget = None
    nodes: dict
    _progress_bar: ProgressBarWidget

    def pb_update(self):
        if self._progress_bar.running:
            self._progress_bar._update()
            self.after(20, self.pb_update)

    @property
    def selected_files(self):
        self._set_input()
        return self._selected_files

    def process(self):
        if not self._selected_files:
            return
        self._progress_bar.start(len(self._selected_files))
        self._progress_bar.running = True
        self.pb_update()
        self.after(0, self.pb_update)
        start_processing(self._selected_files, self._progress_bar)

    def done_callback(self,future):
        try:
            result = future.result()
            if result:
                self._progress_bar.increase_processed()
            else:
                self._progress_bar.increase_failed()
        except Exception:
            logger.exception("Exception converting file")
            self._progress_bar.increase_failed()


    def select_base(self):
        self.base_path = filedialog.askdirectory(parent=self)  # select directory
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
        logger.debug(f"Looking up files for glob: '{self.glob}'")
        self._selected_files = [
            pathlib.Path(self.base_path, globbed_file) for globbed_file in glob.glob(self.glob, recursive=True)]
        logger.debug(f"Found {len(self._selected_files)} files")

    def preview(self):
        if not self.base_path:
            return
        self._clear()
        self._set_input()
        abspath = os.path.abspath(self.base_path)
        node = self.tree.insert("", 'end', abspath, text=self.base_path, open=True)
        self.nodes[abspath] = node
        treeview = ShowPathTreeAsDict
        treeview.on_file = self._on_file
        treeview.on_subfolder = self._on_folder
        self.treeview_files = treeview(base_path=self.base_path, paths=self.selected_files).get()

    def serve_gui(self):
        self.geometry("300x400")

        frame = tkinter.Frame(self.master)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        from MangaManager.Settings.Settings import Settings
        default_base_setting = Settings().get('Webp Converter', 'default_base_path')
        self.selected_base_path = tkinter.StringVar(None, value=default_base_setting)
        self.base_path = default_base_setting
        tkinter.Button(frame, text="Select Base Directory", command=self.select_base, width=50).pack()
        self.base_path_entry = tkinter.Entry(frame, state="readonly", textvariable=self.selected_base_path, width=50)
        self.base_path_entry.pack()
        tkinter.Label(frame, text="Glob to apply:", width=50).pack(side="top")
        self.path_glob = tkinter.Entry(frame, width=50)
        self.path_glob.pack()
        #
        tkinter.Button(frame, text="Preview selected files", pady=6, command=self.preview, width=50).pack(side="top", pady=10)
        tkinter.Button(frame, text="Process", command=self.process, pady=6, width=50).pack(side="top", pady=10)
        pb_frame = tkinter.Frame(frame, pady=10, width=60)
        pb_frame.pack()
        self._progress_bar = ProgressBarWidget(pb_frame)

        self.tree = ttk.Treeview(frame)
        self.tree.heading('#0', text='Project tree', anchor='n')

        self.tree.pack(expand=True, fill="both", side="top")
