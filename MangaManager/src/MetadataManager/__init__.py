import logging
from os.path import abspath

from pkg_resources import resource_filename

from src import sources_factory
from src.Layouts import layout_factory
from src.Settings import default_settings
from src.Settings.DefaultSettings import SettingHeading
from src.Settings.Settings import Settings

main_settings = default_settings[SettingHeading.Main]
source_settings = default_settings[SettingHeading.ExternalSources]

logger = logging.getLogger()

icon_path = abspath(resource_filename(__name__, '../../res/icon.ico'))

def execute_gui():
    # Populate settings with dynamically loaded classes TODO: Move this default code into Settings()
    source_settings.get_control('default_metadata_source').value = list([source.name for source in sources_factory.get("MetadataSources")])
    if not source_settings.get_control('default_metadata_source').value:
        source_settings.get_control('default_metadata_source').value = "AniList"
    source_settings.get_control('default_cover_source').values = list([source.name for source in sources_factory.get("CoverSources")])
    if not source_settings.get_control('default_cover_source').value:
        source_settings.get_control('default_cover_source').value = "MangaDex"

    layout_name = Settings().get(SettingHeading.Main, 'selected_layout')
    main_settings.get_control('selected_layout').value = list(layout_factory)
    if layout_name not in layout_factory:
        layout_name = "default"
    logger.info(f"Initializing '{layout_name}' layout")
    app = layout_factory.get(layout_name)()
    try:
        app.iconbitmap(icon_path)
    except:
        logger.exception("Exception loading icon")

    app.mainloop()


