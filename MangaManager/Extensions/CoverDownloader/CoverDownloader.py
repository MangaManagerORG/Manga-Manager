from tkinter import Label, Frame, Entry

from Extensions.Interface import IExtensionApp
from ExternalSources.CoverSources import Cover
from src import settings_class

settings = settings_class.get_setting("main")
covers_folder_path = settings.covers_folder_path


# logger = logging.getLogger()
#
def get_cover_from_source_dummy() -> list[Cover]:
    ...

class CoverDownloader(IExtensionApp):
    name = "Cover Downloader"

    def serve_gui(self):
        if not self.master:
            return Exception("Tried to initialize ui with no master window")

        frame = Frame(self.master)
        frame.pack()

        Label(frame, text="Manga identifier").pack()
        Entry(frame).pack()
        # Combobox(frame, state="readonly",values=sources_factory["CoverSources"]).pack()

        covers = get_cover_from_source_dummy()




