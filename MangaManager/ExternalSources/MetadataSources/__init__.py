from .MangaUpdates import MangaUpdates
from .AniList import AniList
from .MetadataSourceFactory import ScraperFactory

providers = [ScraperFactory().get_scraper("MangaUpdates"), ScraperFactory().get_scraper("AniList")]