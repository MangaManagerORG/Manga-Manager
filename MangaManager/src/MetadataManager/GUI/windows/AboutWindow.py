import logging
import tkinter
from typing import NamedTuple

import requests

from src.MetadataManager.GUI.widgets import HyperlinkLabelWidget, ButtonWidget
from src.__version__ import __version__

log = logging.getLogger('AboutWindow')

Versions = NamedTuple('Versions', [('prev_latest', str), ('latest', str), ('prev_nightly', str)])

def get_release_tag() -> Versions:
    """
    Get the latest release tag from GitHub
    :return: previous latest release tag, latest release tag
    """
    # Replace these values with your own
    username = 'MangaManagerOrg'
    repo_name = 'Manga-Manager'

    # Make a GET request to the GitHub API endpoint to get the releases
    response = requests.get(f'https://api.github.com/repos/{username}/{repo_name}/releases', params={'per_page': 100})

    # Parse the JSON response
    data = response.json()

    # Filter out pre-releases
    latest_version = None
    prev_latest = None
    prev_nightly = None
    for release in data:
        if latest_version and prev_latest and prev_nightly:
            break

        if release['draft']:
            continue
        if not release['prerelease']:
            if latest_version:
                prev_latest = release['tag_name']
                break
            latest_version = release['tag_name']
            continue
        else:
            if not prev_nightly:
                prev_nightly = release['tag_name']
                continue

    if latest_version:
        print(latest_version)
        print(prev_latest)
    else:
        print('No non-pre-release version found.')
    return Versions(prev_latest, latest_version,prev_nightly)


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
        parsed_version = __version__.split(":")
        version = __version__
        releases = get_release_tag()
        if len(parsed_version) > 2:
            if parsed_version[1].startswith("nightly"):
                version_url = f"https://github.com/MangaManagerOrg/Manga-Manager/compare/{releases.prev_nightly}...{parsed_version[2]}"
            if parsed_version[1].startswith("stable"):

                version_url = f"https://github.com/MangaManagerOrg/Manga-Manager/compare/{releases.prev_latest}...{releases.latest}"
                version = f"{parsed_version[0]}:stable"
        HyperlinkLabelWidget(self.frame, "Version number", url_text=version,
                             url=version_url).pack(fill="x", expand=True, side="top", anchor="center", pady=10)
        # create close button
        ButtonWidget(master=self.frame, text="Close", command=self.close).pack()

    def close(self):
        self.top_level.destroy()
if __name__ == '__main__':
    get_release_tag()