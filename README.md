# Manga Manager

[![Python tests](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml/badge.svg)](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Run_Tests.yml) [![Build & publish Docker Images](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Build_Docker_Images.yml/badge.svg)](https://github.com/ThePromidius/Manga-Manager/actions/workflows/Build_Docker_Images.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ThePromidius_Manga-Manager&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ThePromidius_Manga-Manager)

# NOTE: REWORK BETA IS LIVE:

Manga Manager is currently being reworked. Little features will be added to the current codebase. Only fixes and easy
additions.

Release URL:
https://github.com/MangaManagerORG/Manga-Manager/releases/tag/v1.0.0-beta.1

## Min required version: Python 3.9


## What is Manga Manager

Manga Manager collects useful tools to make managing your manga library easy.

These are the tools available

- [Cover Manager](https://github.com/ThePromidius/Manga-Manager/wiki/Cover-Manager) - Lets you change / delete the first
  page of a CBZ file
- [Metadata Manager](https://github.com/ThePromidius/Manga-Manager/wiki/Metadata-Manager) - A GUI metadata editor. Load
  the files, modify the metadata and save.
    - [copy command CLI](https://github.com/ThePromidius/Manga-Manager/wiki/Metadata-Manager#copy-command---cli) - CLI
      tool that lets you copy the metadata from one file to multiple
- [Volume Manager](https://github.com/ThePromidius/Manga-Manager/wiki/Volume-Manager) - Lets you assign a volume
  tag `Vol.xx` to a filename and metadata
- [Webp Converter](https://github.com/ThePromidius/Manga-Manager/wiki/WEBP-Converter) - Converts the images in a cbz to
  webp
  - [CLI command](https://github.com/ThePromidius/Manga-Manager/wiki/Metadata-Manager#cli---copy-command) - Used to
    batch convert files to Webp
- [Epub to CBZ](https://github.com/ThePromidius/Manga-Manager/wiki/EPUB-to-CBZ-converter) - Moves the images of a epub
  to a cbz file. (Metadata does not get copied yet)

## Requirements

Min required version: Python 3.9

## Docker

This suite of applications can be run using Docker!
In the repo's root you can find a docker-compose.yml to use or derive your docker run command from. Truly essential is
to expose port `3000` and map the volumes for `/manga` and `/covers`.
[Watch the docker-compose.yml template at the wiki](https://github.com/ThePromidius/Manga-Manager/wiki/Docker#docker-composeyml)
The stable releases are built from the master branch of this repo, nightlies are built from the develop branch.

![Screenshot-1](/project-docs/screenshot-1.png)

![Screenshot-2](/project-docs/screenshot-2.png)

### Art attribution

Wallpaper Photo by [Ian Valerio](https://unsplash.com/@iangvalerio?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/anime?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)
