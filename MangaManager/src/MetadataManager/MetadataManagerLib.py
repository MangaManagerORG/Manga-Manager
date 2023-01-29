from __future__ import annotations

import abc
import logging
from abc import ABC

from src import settings_class, sources_factory
from src.Common.errors import EditedCinfoNotSet, MangaNotFoundError
from src.Common.errors import NoComicInfoLoaded, CorruptedComicInfo, BadZipFile
from src.Common.loadedcomicinfo import LoadedComicInfo
from src.Common.terminalcolors import TerminalColors as TerCol
from src.MetadataManager import comicinfo
from src.MetadataManager.comicinfo import ComicInfo

AniList = [source for source in sources_factory.get("MetadataSources") if source.name == "AniList"]

logger = logging.getLogger("MetaManager.Core")
settings = settings_class.get_setting("main")
source_settings = settings_class.get_setting("ExternalSources")


class _IMetadataManagerLib(abc.ABC):
    def on_item_loaded(self, loaded_cinfo: LoadedComicInfo):
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
    cinfo_tags: list[str] = ["Title", "Series", "Number", "Count", "Volume", "AlternateSeries", "AlternateNumber",
                             "AlternateCount", "Summary", "Notes", "Year", "Month", "Day", "Writer", "Penciller",
                             "Inker", "Colorist", "Letterer", "CoverArtist", "Editor", "Translator", "Publisher",
                             "Imprint", "Genre", "Tags", "Web", "PageCount", "LanguageISO", "Format", "BlackAndWhite",
                             "Manga", "Characters", "Teams", "Locations", "ScanInformation", "StoryArc",
                             "StoryArcNumber", "SeriesGroup", "AgeRating", "CommunityRating",
                             "MainCharacterOrTeam","Other", "Review",
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
        for loaded_cinfo in loaded_cinfo_list:
            logger.debug(LOG_TAG + f"Merging changes to {loaded_cinfo.file_path}")
            for cinfo_tag in self.cinfo_tags:
                new_value = str(self.new_edited_cinfo.get_attr_by_name(cinfo_tag))
                if new_value == self.MULTIPLE_VALUES_CONFLICT:
                    logger.trace(LOG_TAG + f"Ignoring {cinfo_tag}. Keeping old values")
                    continue
                old_value = str(loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag))
                if old_value == new_value:
                    logger.trace(LOG_TAG + f"Ignoring {cinfo_tag}. Field has not changed")
                    continue
                if cinfo_tag not in loaded_cinfo.changed_tags:
                    loaded_cinfo.changed_tags.append((cinfo_tag, old_value, new_value))
                logger.debug(LOG_TAG + f"[{cinfo_tag:15s}] {TerCol.GREEN}Updating{TerCol.RESET} - Old '{TerCol.RED}{old_value}{TerCol.RESET}' vs "
                             f"New: '{TerCol.YELLOW}{new_value}{TerCol.RESET}' - Keeping {TerCol.YELLOW}new{TerCol.RESET} value")
                loaded_cinfo.cinfo_object.set_attr_by_name(cinfo_tag, new_value)
                loaded_cinfo.has_changes = True
                any_has_changes = True
            if any((loaded_cinfo.cover_action is not None,loaded_cinfo.backcover_action is not None)):
                any_has_changes = True
                loaded_cinfo.has_changes = True
            # if loaded_cinfo.is_metadata_modified(self.cinfo_tags):

        self.new_edited_cinfo = None
        return any_has_changes

    def open_cinfo_list(self) -> None:
        """
        Creates a list of comicinfo with the comicinfo metadata from the selected files.

        :raises CorruptedComicInfo: If the data inside ComicInfo.xml could not be read after trying to fix te data
        :raises BadZipFile: If the provided zip is not a valid zip or is broken
        """

        logger.debug("Loading files")
        self.loaded_cinfo_list: list[LoadedComicInfo] = list()
        for file_path in self.selected_files_path:
            try:
                loaded_cinfo = LoadedComicInfo(path=file_path)
                if settings.cache_cover_images and not self.is_cli:
                    loaded_cinfo.load_all()
                else:
                    loaded_cinfo.load_metadata()
            except CorruptedComicInfo as e:
                # Logging is handled already in LoadedComicInfo load_metadata method
                loaded_cinfo = LoadedComicInfo(path=file_path, comicinfo=comicinfo.ComicInfo()).load_metadata()
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
            self.loaded_cinfo_list.append(loaded_cinfo)
            self.on_item_loaded(loaded_cinfo)
        logger.debug("Files selected")

    def preview_export(self, loaded_cinfo):
        """
        Debug function to preview loaded_cinfo in terminal
        :param loaded_cinfo:
        :return:
        """
        ...
        # print(loaded_cinfo.__dict__)
        # export = StringIO()
        # print(loaded_cinfo.cinfo_object is None)
        # loaded_cinfo.cinfo_object.export(export, 0)
        # print(export.getvalue())

    def fetch_online(self,series_name):

        selected_source = [source for source in sources_factory["MetadataSources"] if source.name == source_settings.default_metadata_source.value]
        if not selected_source:
            raise Exception("Unhandled exception. Metadata sources are not loaded or there's a bug in it."
                            "Raise an issue if this happens.")
        source = selected_source[0]
        try:
            return source.get_cinfo(series_name)
        except MangaNotFoundError as e:
            logger.exception(str(e))
            self.on_manga_not_found(e, series_name)
            return None


