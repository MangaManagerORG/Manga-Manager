from .SettingControl import SettingControl
from .SettingControlType import SettingControlType
from .SettingSection import SettingSection

default_settings = {
    "main": SettingSection("Main Settings", [
        SettingControl("library_path", "Library Path", SettingControlType.Text, "", "The path to your library. This location will be opened by default when choosing files"),
        SettingControl("covers_folder_path", "Covers folder path", SettingControlType.Text, "", "The path to your covers. This location will be opened by default when choosing covers"),
        SettingControl("cache_cover_images", "Cache cover images", SettingControlType.Bool, False, "If enabled, the covers of the file will be cached and shown in the ui"),
        SettingControl("selected_layout", "* Active layout", SettingControlType.Options, "", "Selects the layout to be displayed"),
    ]),
    "WebpConverter": SettingSection("Webp Converter Settings", [
        SettingControl("default_base_path", "Default base path", SettingControlType.Text, "", "The starting point where the glob will begin looking for files that match the pattern"),
    ]),
    "ExternalSources": SettingSection("External Sources Settings", [
        SettingControl("default_metadata_source", "Default metadata source", SettingControlType.Options, "The source that will be hit when looking for metadata"),
        SettingControl("default_cover_source", "Default cover source", SettingControlType.Options, "The source that will be hit when looking for cover images"),
    ])
}