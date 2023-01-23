import logging

from Extensions.Interface import IExtensionApp
from src import settings_class

settings = settings_class.get_setting("main")
logger = logging.getLogger()


class ExtensionTemplate(IExtensionApp):
    name = "Webp Converter"

    def serve_gui(self):
        if not self.master:
            return Exception("Tried to initialize ui with no master window")