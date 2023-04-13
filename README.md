[![Python tests](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml/badge.svg)](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)

# Welcome to the Manga Manager rework

The current version in this branch is pretty much a brand new MangaManager. The old code was very limited due to how limited its original purpose was.

With a lot of effort and support from the community, the rework was born.

Please note that you are accessing the Beta Version of MangaManger which is in the process of being developed with all it's features before its official release. The sole purpose of this BETA Version is to conduct testing and obtain feedback.
All releases are tested but if you happen to find an error or a bug please report them with the label "Rework Issue".

## What is Manga Manager

Manga Manager is an all-in-one tool to make managing your manga library easy.
Has a built-in metadata editor as well as cover and back cover editor.

# Key Features:

* Select multiple files and preview the covers of each file
* Bulk edit metadata for all files at once
* Changes are kept in one session, allowing flexible editing
* Apply all changes (save to file) at once when done editing
* Edit cover or back cover from the metadata view itself
* Cover manager for batch editing of covers
* Online metadata scraping
* Webp converter
* Error and warning log within the UI itself
* Terminal interface (supports ssh)

### Does it work for comics?

Yes! MangaManager works on any .cbz file!

# Donate

If you enjoy using MangaManager, consider making a voluntary donation as a show of support. Your donation is greatly appreciated and will help fuel the continued development of the software.
You can donate through Ko-fi. Thank you for your generosity and for being a part of the MangaManager community.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U4IC14H)

## Docker

MangaManager provides a convenient solution for remote access to the software through a web browser.

A docker container with a remote desktop is available. It's important to expose port 3000 and mount the volumes for `/manga` and `/covers`. For detailed instructions, refer to the [docker-compose.yml template at the wiki](https://github.com/ThePromidius/Manga-Manager/wiki/Docker#docker-composeyml).

The stable releases are built from the master branch, while nightly builds are generated from the develop branch.


![Screenshot-1](/project-docs/Screenshot_1.png)

### Art attribution

Wallpaper Photo by [Ian Valerio](https://unsplash.com/@iangvalerio?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/anime?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)

## Bare metal requirements

Min required version: Python 3.10.8

Requirements in requirements.txt

#### Additional for Linux
- tkinter
- idlelib

## FAQ
### No rar tools detected on windows.
Download [unrar](https://www.winrar.es/descargas/unrar), execute it and select a place to decompress the contents. A file `unrar.exe` will be decompressed and you can move so it sits alongside MangaManager.exe file.
