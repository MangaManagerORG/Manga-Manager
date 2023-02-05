from .MangaUpdates import MangaUpdates
from .AniList import AniList
from .MetadataSourceFactory import ScraperFactory

# TODO: Load dynamically loaded extensions (this will be moved in another PR)
providers = [ScraperFactory().get_scraper("MangaUpdates"), ScraperFactory().get_scraper("AniList")]