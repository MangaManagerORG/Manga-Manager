import logging

from src import settings as settings_class
from src.Layouts import layout_factory

main_settings = settings_class.get_setting("main")
logger = logging.getLogger()


def execute_gui():
    layout_name = main_settings.selected_layout.value
    if layout_name not in layout_factory:
        layout_name = "default"
    logger.info(f"Initializing '{layout_name}' layout")
    app = layout_factory.get(layout_name)()

    app.mainloop()
