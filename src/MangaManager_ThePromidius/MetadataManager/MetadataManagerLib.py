import abc
import logging
from io import StringIO

from .comicinfo import ComicInfo
from .errors import NoMetadataFileFound, NoComicInfoLoaded, FailedBackup
from .cbz_handler import LoadedComicInfo

logger = logging.getLogger("MetadataManager.Core")


class MetadataManagerLib(abc.ABC):
    """
    The core of metadata editor.
    It has the logic to merge all the data of each fields across multiple files.
    """
    selected_files_path = None
    new_edited_cinfo: ComicInfo = None
    loaded_cinfo_list: list[LoadedComicInfo]
    cinfo_tags: list[str] = ['Title', 'Series', 'LocalizedSeries', 'SeriesSort', 'Summary', 'Genre', 'Tags', 'AlternateSeries', 'Notes', 'AgeRating', 'CommunityRating', 'ScanInformation', 'StoryArc', 'AlternateCount', 'Writer', 'Inker', 'Colorist', 'Letterer', 'CoverArtist', 'Editor', 'Translator', 'Publisher', 'Imprint', 'Characters', 'Teams', 'Locations', 'Number', 'AlternateNumber', 'Count', 'Volume', 'PageCount', 'Year', 'Month', 'Day', 'StoryArcNumber', 'LanguageISO', 'Format', 'BlackAndWhite', 'Manga']
    multiple_values_conflict = "~~## Multiple Values in this Field - Keep Original Values ##~~"

    def proces(self) -> tuple[list[LoadedComicInfo], list[LoadedComicInfo]]:
        """
        Core function
        Reads the new cinfo class and compares it against all LoadedComicInfo.
        Applies the changes to the LoadedComicInfo unless the value in cinfo is a special one (-1 -keep current,-2 - clear field)
        :return: list of loadedcinfo that failed to update :
        """
        if not self.loaded_cinfo_list:
            raise NoComicInfoLoaded()
        failed_processing = []
        unhandled_failed_processing = []

        self.merge_changed_metadata()
        self.preview_export()
        for loaded_info in self.loaded_cinfo_list:
            # noinspection PyBroadException
            try:
                loaded_info.write_metadata()
            except FailedBackup:
                failed_processing.append(loaded_info)
            except Exception:
                unhandled_failed_processing.append(loaded_info)
        return failed_processing, unhandled_failed_processing

    @abc.abstractmethod
    def load_cinfo_list(self):
        """
        Creates a list of comicinfo with the comicinfo metadata from the selected files.
        Expected to be overriden with custom logic catching exceptions loading the metadata.
        """

        for file_path in self.selected_files_path:
            self.loaded_cinfo_list.append(self.load_cinfo_xml(file_path))

    @staticmethod
    def load_cinfo_xml(file_path) -> LoadedComicInfo:
        """
        Accepts a path string
        Returns a LoadedComicInfo with the ComicInfo class generated from the data contained inside ComicInfo file
        which is taken from the zip-like file type

        :param string file_path: the path to the zip-like file

        :raises CorruptedComicInfo: If the data inside ComicInfo.xml could not be read after trying to fix te data
        :raises BadZipFile: If the provided zip is not a valid zip or is broken
        :returns: LoadedComicInfo
        """
        return LoadedComicInfo(path=file_path)

    def merge_changed_metadata(self):
        """
        Edited comic info gets applied to each loaded ComicInfo
        If edited version == '~~## Multiple Values in this Field ##~~' then original values are kept
        Else it applies the edited version.
        :return:
        """
        if self.new_edited_cinfo is None:
            raise NoMetadataFileFound()

        for loaded_cinfo in self.loaded_cinfo_list:
            logger.debug(f"[Merging] Merging changes to {loaded_cinfo.file_path}")

            for cinfo_tag in self.cinfo_tags:
                new_value = self.new_edited_cinfo.get_attr_by_name(cinfo_tag)
                old_value = loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag)
                # If the value in the ui is to keep original values then we continue with the next field
                if new_value == self.multiple_values_conflict:
                    logger.debug(
                        f"[Merging][{cinfo_tag:15s}] Keeping \x1b[31;1mOld\x1b[0m '\x1b[33;20m{old_value}\x1b[0m' vs New: '{new_value}'")
                    # logger.debug(f"Keeping original value: {loaded_cinfo.cinfo_object.get_attr_by_name(cinfo_tag)}")
                    continue
                # Write whatever is in the new (edited) cinfo
                logger.debug(f"[Merging][{cinfo_tag:15s}] Keeping \x1b[31;1mNew\x1b[0m '{old_value}' vs "
                             f"New: '\x1b[33;20m{new_value}\x1b[0m' - Keeping new value")
                loaded_cinfo.cinfo_object.set_attr_by_name(cinfo_tag, new_value)

    def preview_export(self):
        for loaded_cinfo in self.loaded_cinfo_list:
            print(loaded_cinfo.__dict__)
            export = StringIO()
            print(loaded_cinfo.cinfo_object is None)
            loaded_cinfo.cinfo_object.export(export, 0)
            # print(export.getvalue())
