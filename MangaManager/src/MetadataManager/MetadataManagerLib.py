from __future__ import annotations

import abc
import logging
from abc import ABC

from ExternalSources.MetadataSources import ScraperFactory
from common.models import ComicInfo
from src.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from src.Common.errors import EditedCinfoNotSet, MangaNotFoundError, MissingRarTool
from src.Common.errors import NoComicInfoLoaded, CorruptedComicInfo, BadZipFile
from src.Common.terminalcolors import TerminalColors as TerCol
from src.Settings import SettingHeading
from src.Settings.Settings import Settings

logger = logging.getLogger("MetaManager.Core")


class _IMetadataManagerLib(abc.ABC):
    def on_item_loaded(self, loaded_cinfo: LoadedComicInfo,cursor,total):
        """
        Called when a loadedcomicinfo is loaded
        :return:
        """

    @abc.abstractmethod
    def on_badzipfile_error(self, exception, file_path):
        """
        Called while loading a file, and it's not a valid zip or it's broken
        """

    @abc.abstractmethod
    def on_processed_item(self, loaded_info: LoadedComicInfo):
        """
        Called when  a file is successfully processed
        """

    @abc.abstractmethod
    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):
        """
        Called while loading a file, and it's metadata can't be read.
        """

    @abc.abstractmethod
    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):
        """
        Called while trying to save to the file.
        Posible callees (but not limited to): FailedBackup,
        """

    @abc.abstractmethod
    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):
        """
        Called when an unhandled exception occurred trying to save the file
        """

    @abc.abstractmethod
    def on_manga_not_found(self, exception, series_name):
        """
        Called when a series is not found in the api
        """
    @abc.abstractmethod
    def on_missing_rar_tools(self,exception):
        """
        Caññed whem rar tools are not available
        """

class MetadataManagerLib(_IMetadataManagerLib, ABC):
    """
    The core of metadata editor.
    It has the logic to merge all the data of each fields across multiple files.
    """
    is_cli = False
    is_test = False
    selected_files_path = None
    new_edited_cinfo: ComicInfo | None = None
    loaded_cinfo_list: list[LoadedComicInfo] = list()
    cinfo_tags: list[str] = ["Title", "Series", "LocalizedSeries", "Number", "Count", "Volume", "AlternateSeries", "AlternateNumber",
                             "AlternateCount", "Summary", "Notes", "Year", "Month", "Day", "Writer", "Penciller",
                             "Inker", "Colorist", "Letterer", "CoverArtist", "Editor", "Translator", "Publisher",
                             "Imprint", "Genre", "Tags", "Web", "PageCount", "LanguageISO", "Format", "BlackAndWhite",
                             "Manga", "Characters", "Teams", "Locations", "ScanInformation", "StoryArc",
                             "StoryArcNumber", "SeriesGroup", "AgeRating", "CommunityRating",
                             "MainCharacterOrTeam", "Other", "Review","GTIN"
    ]
    MULTIPLE_VALUES_CONFLICT = "~~## Keep Original Value ##~~"
    tags_with_multiple_values = []

    @property
    def loaded_cinfo_list_to_process(self) -> list[LoadedComicInfo]:
        return [loaded_cinfo for loaded_cinfo in self.loaded_cinfo_list if loaded_cinfo.has_changes]

    def process(self):
        """
        Iterates the list of loaded_cinfo.
        Skips cinfo that do not have modified metadata


        :return: list of loadedcinfo that failed to update :
        """
        LOG_TAG = "[Processing] "
        if not self.loaded_cinfo_list:
            self.loaded_cinfo_list_to_proces: list[LoadedComicInfo] = list()
            raise NoComicInfoLoaded()
        try:
            for loaded_cinfo in self.loaded_cinfo_list:
                if not loaded_cinfo.has_changes:
                    logger.info(LOG_TAG + f"Skipping file processing. No changes to it. File: '{loaded_cinfo.file_name}'")
                    self.on_processed_item(loaded_cinfo)
                    continue
                # noinspection PyBroadException
                self.preview_export(loaded_cinfo)
                try:
                    loaded_cinfo.write_metadata()
                    loaded_cinfo.has_changes = False
                    self.on_processed_item(loaded_cinfo)
                except PermissionError as e:
                    logger.error("Failed to write changes because of missing permissions "
                                 "or because other program has the file opened", exc_info=True)
                    self.on_writing_error(exception=e, loaded_info=loaded_cinfo)
                    # failed_processing.append(loaded_info)
                except Exception as e:
                    logger.exception("Unhandled exception saving changes")
                    self.on_writing_exception(exception=e, loaded_info=loaded_cinfo)
        finally:
            self.loaded_cinfo_list_to_proces: list[LoadedComicInfo] = list()

    def merge_changed_metadata(self, loaded_cinfo_list: list[LoadedComicInfo]) -> bool:
        """
        Merges new_edited_cinfo with each individual loaded_cinfo.
        If field is ~~Multiple...Values~~, nothing will be changed.
        Else new_cinfo value will be saved
        :return: True if any loaded_cinfo has changes
        """
        LOG_TAG = "[Merging] "
        any_has_changes = False

        if not self.new_edited_cinfo:
            raise EditedCinfoNotSet()
        if loaded_cinfo_list is None:
            return False
        for loaded_cinfo in loaded_cinfo_list:
            logger.debug(LOG_TAG + f"Merging changes to {loaded_cinfo.file_path}")
            for cinfo_tag in self.cinfo_tags:
                if cinfo_tag == "PageCount":
                    continue
                # Check if the ui has $Multiple_files_selected$
                new_value = str(self.new_edited_cinfo.get_by_tag_name(cinfo_tag))
                if new_value == self.MULTIPLE_VALUES_CONFLICT:
                    logger.trace(LOG_TAG + f"Ignoring {cinfo_tag}. Keeping old values")
                    continue

                # Check if the new value in the ui is the same as the one in the comicinfo
                old_value = str(loaded_cinfo.cinfo_object.get_by_tag_name(cinfo_tag))
                if old_value == new_value:
                    logger.trace(LOG_TAG + f"Ignoring {cinfo_tag}. Field has not changed")
                    continue

                # Nothing matches so overriding comicinfo value with whatever is in the ui
                if cinfo_tag not in loaded_cinfo.changed_tags:
                    loaded_cinfo.changed_tags.append((cinfo_tag, old_value, new_value))
                logger.debug(LOG_TAG + f"[{cinfo_tag:15s}] {TerCol.GREEN}Updating{TerCol.RESET} - Old '{TerCol.RED}{old_value}{TerCol.RESET}' vs "
                             f"New: '{TerCol.YELLOW}{new_value}{TerCol.RESET}' - Keeping {TerCol.YELLOW}new{TerCol.RESET} value")
                loaded_cinfo.cinfo_object.set_by_tag_name(cinfo_tag, new_value)
                loaded_cinfo.has_changes = True
                any_has_changes = True

            # Check if covers are modified
            if any((loaded_cinfo.cover_action is not None, loaded_cinfo.backcover_action is not None)):
                any_has_changes = True
                loaded_cinfo.has_changes = True

        self.new_edited_cinfo = None
        return any_has_changes

    def open_cinfo_list(self, abort_load_check:callable) -> bool:
        """
        Creates a list of comicinfo with the comicinfo metadata from the selected files.

        :raises CorruptedComicInfo: If the data inside ComicInfo.xml could not be read after trying to fix the data
        :raises BadZipFile: If the provided zip is not a valid zip or is broken
        """

        logger.debug("Loading files")
        self.loaded_cinfo_list: list[LoadedComicInfo] = list()
        # Skip warnings if one was already displayed
        missing_rar_tool = False
        total_files = len(self.selected_files_path)
        if total_files == 0:
            return False
        for i, file_path in enumerate(self.selected_files_path):
            if any(file_path in comic.file_path for comic in self.loaded_cinfo_list):
                logger.warning("Skipped loading file: File already loaded",extra={'processed_filename':file_path})
                continue

            if abort_load_check():
                logger.info("Abort loading")
                self.loaded_cinfo_list: list[LoadedComicInfo] = list()
                return False
            try:
                loaded_cinfo = LoadedComicInfo(path=file_path)
                if Settings().get(SettingHeading.Main, 'cache_cover_images') and not self.is_cli:
                    loaded_cinfo.load_all()
                else:
                    loaded_cinfo.load_metadata()
            except CorruptedComicInfo as e:
                # Logging is handled already in LoadedComicInfo load_metadata method
                loaded_cinfo = LoadedComicInfo(path=file_path, comicinfo=ComicInfo()).load_metadata()
                self.on_corruped_metadata_error(e, loaded_info=loaded_cinfo or file_path)
                continue
            except BadZipFile as e:
                logger.error("Bad zip file. Either the format is not correct or the file is broken", exc_info=False)
                self.on_badzipfile_error(e, file_path=file_path)
                continue
            except EOFError as e:
                logger.error("Bad zip file. The file seems to be broken", exc_info=True)
                self.on_badzipfile_error(e, file_path=file_path)
                continue
            except MissingRarTool as e:
                if not missing_rar_tool:
                    logger.exception("Error loading the metadata for some files. No rar tools available", exc_info=False)
                    self.on_missing_rar_tools(e)
                missing_rar_tool = True
                continue

            self.loaded_cinfo_list.append(loaded_cinfo)
            self.on_item_loaded(loaded_cinfo=loaded_cinfo, cursor=i, total=total_files)

            # self.on_item_loaded(loaded_cinfo)
        logger.debug("Files selected")
        return True

    def preview_export(self, loaded_cinfo):
        """
        Debug function to preview loaded_cinfo in terminal
        :param loaded_cinfo:
        :return:
        """
        ...

    def fetch_online(self, partial_comic_info):
        selected_source = ScraperFactory().get_scraper(Settings().get(SettingHeading.ExternalSources, 'default_metadata_source'))
        if not selected_source:
            raise Exception("Unhandled exception. Metadata sources are not loaded or there's a bug in it."
                            "Raise an issue if this happens.")
        try:
            return selected_source.get_cinfo(partial_comic_info)
        except MangaNotFoundError as e:
            logger.exception(str(e))
            self.on_manga_not_found(e, partial_comic_info)
            return None


