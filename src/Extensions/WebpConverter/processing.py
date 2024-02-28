import logging

from MangaManager.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo

logger = logging.getLogger()

def convert(file):
    try:
        LoadedComicInfo(file, load_default_metadata=False).convert_to_webp()
        return True
    except:
        logger.exception("Exception converting")
        return False

