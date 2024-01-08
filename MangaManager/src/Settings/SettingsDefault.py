from enum import StrEnum


class SettingHeading(StrEnum):
    Main = "Main",
    WebpConverter = "Webp Converter",
    ExternalSources = "External Sources",
    MessageBox = "Message Box"


default_settings = {
    SettingHeading.Main: [
        {"library_path": ""},
        {"covers_folder_path": ""},
        {"cache_cover_images": True},
        {"create_backup_comicinfo": True},
        # {"selected_layout": "default"},
        {"move_to_template": ""},
        {"remove_old_selection_on_drag_drop":True},
        {"darkmode_enabled":False}

    ],
    SettingHeading.WebpConverter: [
        {"default_base_path": ""},
    ],
    SettingHeading.ExternalSources: [
        {"default_metadata_source": "AniList"},
        {"default_cover_source": "MangaDex"},
    ],
    SettingHeading.MessageBox: {}
}


