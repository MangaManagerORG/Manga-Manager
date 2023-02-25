# Import all the scrapers here to ensure globals() has the key in it for dynamic instantiation
import logging

from src.DynamicLibController.models.IMetadataSource import IMetadataSource

logger = logging.getLogger()

# NOTE: This is a stopgap solution until dynamic loader is implemented
class ScraperFactory:
    """ Singleton Factory of metadata providers. Pass in the name defined in the provider .name() and an instance will be returned. """
    __instance = None
    providers = {}

    def __new__(cls):
        if ScraperFactory.__instance is None:
            ScraperFactory.__instance = object.__new__(cls)

        return ScraperFactory.__instance

    def __init__(self):
        pass

    def get_scraper(self, setting_name) -> IMetadataSource:
        if setting_name not in self.providers:
            try:
                cls = globals()[setting_name]
            except KeyError:
                logger.exception(f"Failed to load setting name '{setting_name}'")
                return
            self.providers[setting_name] = cls()
        return self.providers[setting_name]
