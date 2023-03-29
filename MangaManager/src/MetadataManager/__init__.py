import logging

from src.Common import ResourceLoader
from src.MetadataManager.GUI.MainGUI import MainGUI
from src.MetadataManager.GUI.OneTimeMessageBox import OneTimeMessageBox
from src.MetadataManager.GUI.widgets.MessageBoxWidget import MessageBoxButton
from src.Settings import Settings, SettingHeading

logger = logging.getLogger()

icon_path = ResourceLoader.get('icon.ico')


def execute_gui():
    # Ensure there are some settings, if not, set them as the default
    Settings().set_default(SettingHeading.ExternalSources, 'default_metadata_source', "AniList")
    Settings().set_default(SettingHeading.ExternalSources, 'default_cover_source', "MangaDex")

    app = MainGUI()

    try:
        app.iconbitmap(icon_path)
    except:
        logger.exception("Exception loading icon")

    OneTimeMessageBox("test_welcome_to_mm"). \
        with_title("Welcome to MangaManager"). \
        with_actions([MessageBoxButton(0, "Thanks")]). \
        build().prompt()

    app.mainloop()
