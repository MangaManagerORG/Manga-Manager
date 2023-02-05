import logging
from os.path import abspath

from pkg_resources import resource_filename

from src import sources_factory
from src.Layouts import layout_factory
from src.Settings import Settings, SettingHeading

logger = logging.getLogger()

icon_path = abspath(resource_filename(__name__, '../../res/icon.ico'))


def execute_gui():
    # Populate settings with dynamically loaded classes
    if not Settings().get(SettingHeading.ExternalSources, 'default_metadata_source') in list([source.name for source in sources_factory.get("MetadataSources")]):
        Settings().set(SettingHeading.ExternalSources, 'default_metadata_source', 'AniList')

    if not Settings().get(SettingHeading.ExternalSources, 'default_cover_source') in list([source.name for source in sources_factory.get("CoverSources")]):
        Settings().set(SettingHeading.ExternalSources, 'default_cover_source', 'MangaDex')

    if not Settings().get(SettingHeading.Main, 'selected_layout') in list(layout_factory):
        Settings().set(SettingHeading.Main, 'selected_layout', 'default')
    layout_name = Settings().get(SettingHeading.Main, 'selected_layout')

    logger.info(f"Initializing '{layout_name}' layout")
    app = layout_factory.get(layout_name)()
    try:
        app.iconbitmap(icon_path)
    except:
        logger.exception("Exception loading icon")

    app.mainloop()


