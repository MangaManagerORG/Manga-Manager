import logging
import tkinter

import MangaManager
from MangaManager.Common.TkErrorCatcher import TkErrorCatcher
from MangaManager.Common import ResourceLoader
from MangaManager.MetadataManager.GUI.windows.MainWindow import MainWindow
from MangaManager.MetadataManager.GUI.OneTimeMessageBox import OneTimeMessageBox
from MangaManager.MetadataManager.GUI.widgets.MessageBoxWidget import MessageBoxButton
from MangaManager.Settings import Settings, SettingHeading

logger = logging.getLogger()

icon_path = ResourceLoader.get('icon.ico')


def load_extensions():
    from MangaManager.DynamicLibController.extension_manager import load_extensions as ld_ext
    try:
        MangaManager.loaded_extensions = ld_ext(MangaManager.EXTENSIONS_DIR)
    except Exception:
        logger.exception("Exception loading the extensions")

def execute_gui():
    # Ensure there are some settings, if not, set them as the default
    Settings().set_default(SettingHeading.ExternalSources, 'default_metadata_source', "AniList")
    Settings().set_default(SettingHeading.ExternalSources, 'default_cover_source', "MangaDex")
    load_extensions()

    # Override TK error catcher with custom
    tkinter.CallWrapper = TkErrorCatcher

    app = MainWindow()

    try:
        app.iconbitmap(icon_path)
    except:
        logger.exception("Exception loading icon")

    OneTimeMessageBox("test_welcome_to_mm"). \
        with_title("Welcome to MangaManager"). \
        with_actions([MessageBoxButton(0, "Thanks")]). \
        build().prompt()
    app.mainloop()
