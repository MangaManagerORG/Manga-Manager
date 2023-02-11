import tkinter

from src.__version__ import __version__
from src.MetadataManager.GUI.widgets import HyperlinkLabelWidget, ButtonWidget


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
        tkinter.Label(self.frame, text=f"Version number: {__version__}", font=("Helvetica", 12), justify="left").pack(
            fill="x", expand=True, side="top", anchor="center")
        # create close button
        ButtonWidget(master=self.frame, text="Close", command=self.close).pack()

    def close(self):
        self.frame.destroy()
        self.top_level.destroy()