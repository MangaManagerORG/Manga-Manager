import glob
import importlib
import logging
import os
import tkinter
from tkinter import ttk

from src.MangaManager_ThePromidius.Common.Templates.extension import Extension
from src.MangaManager_ThePromidius.MetadataManager.extensions.webpconverter import ExtensionAppGUI

logger = logging.getLogger(__name__)

class ExtensionController:
    """
    Reads and parses the extensions in the package. Display buttons in the main app to open the extension
    """
    extension_window = None
    extension_window_exists = False
    extensions_tab_frame: tkinter.Frame
    master: tkinter.Tk
    loaded_extensions: list[Extension] = []
    path_to_extensions = os.path.dirname(__file__)

    def __init__(self):
        self.load_extensions()

    def load_extensions(self):
        logger.debug(f"Loading extensions. CWD:'{os.getcwd()}")
        modules = glob.glob(os.path.join(self.path_to_extensions, "*.py"))
        logger.debug(f"Found modules: [{', '.join(modules)}]")
        extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
        logger.debug(f"Found extensions: [{', '.join(extensions)}]")
        for ext in extensions:
            self.loaded_extensions.append(importlib.import_module(f'.extensions.{ext}',
                                                                  package="src.MangaManager_ThePromidius"
                                                                          ".MetadataManager").ExtensionAppGUI())

    def load_settings(self):
        modules = glob.glob(os.path.join(self.path_to_extensions, "*.py"))
        extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
        for ext in extensions:
            self.loaded_extensions.append(importlib.import_module(f'.extensions.{ext}',
                                                                  package="MangaManager_ThePromidius").ExtensionSettings())

    # def _close_ext_window(self):
    #     for child in self.p.winfo_children():
    #         child.destroy()
    #
    #     self.check = False
    #     self.extension_window.destroy()
    # #
    # def _create_ext_window(self, extension_app):
    #     if self.extension_window_exists:
    #         self._close_ext_window()
    #     self.extension_window_exists = True
    #     # noinspection PyTypeChecker
    #     self.extension_window = tkinter.Toplevel(self)
    #
    #     self.extension_window.protocol('WM_DELETE_WINDOW', self._close_ext_window)
    #     self.extension_window.title(f'Extension: {extension_app.name}')
    #
    #     # frame = tkinter.Frame(self.extension_window)
    #     # frame.pack(expand=True, fill="both")
    #     # top_level_frame = ScrolledFrameWidget(frame, scrolltype="vertical", expand=True, fill="both")
    #     # self.extension_window.top_level_frame = top_level_frame.create_frame(expand=False,fill="none")
    #     extension_app.serve_gui(self.extension_window)


class GUIExtensionManager(ExtensionController):

    def display_extensions(self, parent_frame):
        self.load_extensions()
        self.extension_active_frame = ttk.Labelframe(parent_frame)
        self.extension_active_frame.pack(fill="both", expand=True, side="bottom")

        for loaded_extension in self.loaded_extensions:
            tkinter.Button(parent_frame, text=loaded_extension.name, command=lambda:
            self.run_extension(loaded_extension)).pack(side="top")

    def run_extension(self, extension: ExtensionAppGUI):
        for child in self.extension_active_frame.winfo_children():
            child.destroy()
        self.extension_active_frame.configure(text=extension.name)
        extension.serve_gui(self.extension_active_frame)
