# Manga Manager

[![Python tests](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml/badge.svg)](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml) [![Build & publish Docker Images](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Build_Docker_Images.yml/badge.svg)](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Build_Docker_Images.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)

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



# Donate
If you enjoy using MangaManager, consider making a voluntary donation as a show of support. Your donation is greatly appreciated and will help fuel the continued development of the software.
You can donate through Ko-fi. Thank you for your generosity and for being a part of the MangaManager community.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U4IC14H)

## Docker

MangaManager provides a convenient solution for remote access to the software through a web browser.

A docker container with a remote desktop is available. It's important to expose port 3000 and mount the volumes for `/manga` and `/covers`. For detailed instructions, refer to the [docker-compose.yml template at the wiki](https://github.com/ThePromidius/Manga-Manager/wiki/Docker#docker-composeyml).

The stable releases are built from the master branch, while nightly builds are generated from the develop branch.


![Screenshot-1](/project-docs/Screenshot_1.png)
![Screenshot-2](/project-docs/screenshot-2.png)

### Art attribution
Wallpaper Photo by [Ian Valerio](https://unsplash.com/@iangvalerio?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/anime?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)

## Bare metal requirements
Min required version: Python 3.10.8
Requirements in requirements.txt

#### Additional for Linux
- tkinter
- idlelib