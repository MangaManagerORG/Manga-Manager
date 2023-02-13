import logging
import tkinter

from src.__version__ import __version__
from src.MetadataManager.GUI.widgets import HyperlinkLabelWidget, ButtonWidget

log = logging.getLogger('AboutWindow')

class AboutWindow:
    top_level = None
    frame = None

    def __init__(self, parent):
        self.top_level = tkinter.Toplevel(parent)
        self.frame = tkinter.Frame(self.top_level)
        self.frame.pack(pady=30, padx=30, fill="both")
        HyperlinkLabelWidget(self.frame, "Github repo:", url_text="Go to Github rework main page",
                             url="https://github.com/MangaManagerORG/Manga-Manager/tree/rework/master").pack(fill="x",
                                                                                                             expand=True,
                                                                                                             side="top",
                                                                                                             anchor="center")
        HyperlinkLabelWidget(self.frame, "Get support:", url_text="Join MangaManager channel in Kavita discord",
                             url="https://discord.gg/kavita-821879810934439936").pack(fill="x", expand=True, side="top",
                                                                                      anchor="center")
        HyperlinkLabelWidget(self.frame, "Report issue in GitHub", url_text="Create GitHub Issue",
                             url="https://github.com/MangaManagerORG/Manga-Manager/issues/new?assignees=ThePromidius&labels=Rework+Issue&template=rework_issue.md&title=%5BRework+Issue%5D").pack(
            fill="x", expand=True, side="top", anchor="center")
        HyperlinkLabelWidget(self.frame, "Donate in Ko-fi",
                             "https://ko-fi.com/thepromidius").pack(fill="x", expand=True, side="top", anchor="center")
        tkinter.Label(self.frame, text="", font=("Helvetica", 12), justify="left").pack(fill="x", expand=True, side="top",
                                                                                   anchor="center")

        tkinter.Label(self.frame, text="Software licensed under the GNU General Public License v3.0",
                      font=("Helvetica", 12), justify="left").pack(fill="x", expand=True, side="top", anchor="center")
        version_url = "https://github.com/MangaManagerORG/Manga-Manager/releases/latest"
        parsed_version_tag = __version__.split(":")
        version = __version__
        try:
            if len(parsed_version_tag) > 1:
                if parsed_version_tag[1].startswith("nightly"):
                    parsed_version_tag = parsed_version_tag[1].replace("nightly--", "")
                    shortened_shas = parsed_version_tag.split("->-")
                    version = __version__.split("nightly")[0] + f"nightly:{shortened_shas[1]}"

                    version_url = f"https://github.com/MangaManagerOrg/Manga-Manager/compare/{shortened_shas[0]}...{shortened_shas[1]}"
        except Exception:
            log.warning("Failed to parse version url. Defaulting to latest release")
        HyperlinkLabelWidget(self.frame, "Version number", url_text=version,
                             url=version_url).pack(fill="x", expand=True, side="top", anchor="center", pady=10)
        # create close button
        ButtonWidget(master=self.frame, text="Close", command=self.close).pack()

    def close(self):
        self.top_level.destroy()
