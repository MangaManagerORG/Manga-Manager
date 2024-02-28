import logging

from Extensions.IExtensionApp import IExtensionApp

logger = logging.getLogger()


class ExtensionTemplate(IExtensionApp):
    name = "Webp Converter"

    def serve_gui(self):
        if not self.master:
            return Exception("Tried to initialize ui with no master window")