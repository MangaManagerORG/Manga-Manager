import logging
from os.path import abspath

from pkg_resources import resource_filename

from src import settings_class as settings_class
from src import sources_factory
from src.Layouts import layout_factory

main_settings = settings_class.get_setting("main")
source_settings = settings_class.get_setting("ExternalSources")

logger = logging.getLogger()

icon_path = abspath(resource_filename(__name__, '../../res/icon.ico'))

def execute_gui():
    layout_name = main_settings.selected_layout.value
    # Populate settings with dynamically loaded classes
    main_settings.selected_layout.values = list(layout_factory)
    source_settings.default_metadata_source.values = list([source.name for source in sources_factory.get("MetadataSources")])
    if not source_settings.default_metadata_source.value:
        source_settings.default_metadata_source.value = "AniList"
    source_settings.default_cover_source.values = list([source.name for source in sources_factory.get("CoverSources")])
    if not source_settings.default_cover_source.value:
        source_settings.default_cover_source.value = "MangaDex"



    if layout_name not in layout_factory:
        layout_name = "default"
    logger.info(f"Initializing '{layout_name}' layout")
    app = layout_factory.get(layout_name)()
    try:
        app.iconbitmap(icon_path)
    except:
        logger.exception("Exception loading icon")

    app.mainloop()


