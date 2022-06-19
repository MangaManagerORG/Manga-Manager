import datetime
import io
import json
import logging
import os
import pathlib
import re
import shutil
import sys
import zipfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

import iso639

import MangaManager.MetadataManagerLib.cbz_handler
import MetadataManagerLib.models
from MetadataManagerLib import ComicInfo

# <Logger>
logger = logging.getLogger()
# formatter = logging.Formatter()
PROJECT_PATH = pathlib.Path(__file__).parent


def _setup_logging():
    # Create the logging directory/file if it doesn't exist.
    logging.getLogger('MetadataManagerLib.cbz_handler').setLevel(logging.WARNING)
    log_path = f"{PROJECT_PATH}/logs/MangaManager.log"
    if not os.path.exists(log_path):
        if not os.path.isdir(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        open(log_path, 'w').close()

    rotating_file_handler = RotatingFileHandler(log_path, maxBytes=5725760,
                                                backupCount=2)
    rotating_file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    # self._logger.addHandler(handler)
    # self._logger.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout), rotating_file_handler]
                        # filename='/tmp/myapp.log'
                        )


logger = logging.getLogger()
logging.getLogger('MangaManager.MetadataManagerLib.cbz_handler').setLevel(logging.INFO)
_setup_logging()
logger.debug('DEBUG LEVEL - MAIN MODULE')
logger.info('INFO LEVEL - MAIN MODULE')

folder_to_scan = r"D:\Descargas\ANIME\Htorrent\FAKKU_COLLECTION\FAKKU Unlimited 2022.05.30"


# folder_to_scan = r"D:\Descargas\ANIME\Htorrent\FAKKU_COLLECTION\TEST"
# data_file = input("Data json file\n> ")
def cleanFilename(sourcestring, removestring=" %:/,.\\[]<>*?\""):
    """Clean a string by removing selected characters.

    Creates a legal and 'clean' source string from a string by removing some
    clutter and  characters not allowed in filenames.
    A default set is given but the user can override the default string.

    Args:
        | sourcestring (string): the string to be cleaned.
        | removestring (string): remove all these characters from the string (optional).

    Returns:
        | (string): A cleaned-up string.

    Raises:
        | No exception is raised.
    """
    # remove the undesireable characters
    return ''.join([c for c in sourcestring if c not in removestring])

def remove_text_inside_brackets(text, brackets="()[]"):
    count = [0] * (len(brackets) // 2)  # count open/close brackets
    saved_chars = []
    for character in text:
        for i, b in enumerate(brackets):
            if character == b:  # found bracket
                kind, is_close = divmod(i, 2)
                count[kind] += (-1) ** is_close  # `+1`: open, `-1`: close
                if count[kind] < 0:  # unbalanced bracket
                    count[kind] = 0  # keep it
                else:  # found bracket to remove
                    break
        else:  # character is not a [balanced] bracket
            if not any(count):  # outside brackets
                saved_chars.append(character)
    return (''.join(saved_chars)).strip()


def remove_chapter(text):
    r = r"(?i)((?:chapter|ch|#)(?:\s|\.)?(?:\s|\.)?\d+)"
    match = re.findall(r, text)
    if match:
        match = match[0]
        text = text.replace(match, "")

    r = r"(?i)((?:volume|vol|v)(?:\s|\.)?(?:\s|\.)?\d+)"
    match = re.findall(r, text)
    if match:
        match = match[0]
        text = text.replace(match, "")
    # if hasChapter or hasVolume:
    return text


def findChapter(text):
    r = r"(?i)(?:chapter|ch)(?:\s|\.)?(?:\s|\.)?(\d+)"
    match = re.findall(r, text)
    if match:
        return match[0]
    return match

def fetchChapter(text):
    r = r"(?i)(?:chapter|ch|#)(?:\s|\.)?(?:\s|\.)?(\d+)"
    return re.findall(r, text)


def fetchVolume(text):
    r = r"(?i)(?:volume|vol|v)(?:\s|\.)?(?:\s|\.)?(\d+)"
    return re.findall(r, text)


def main():
    logger.info("Starting...")
    scanPath = Path(folder_to_scan)
    for root, dirs, files in os.walk(scanPath):
        for file in files:
            file_path = os.path.join(root, file)
            if not os.path.exists(file_path):
                logger.info(f"Skipping {file_path}, doesn't exist")
                continue
            try:
                if not file.endswith(".cbz"):
                    continue
                file_name = os.path.basename(file)
                logger.info(f"Processing {file_name.strip('.cbz')}")

                comicinfo = ComicInfo.ComicInfo()
                isComicInfo = True
                with zipfile.ZipFile(file_path, 'r') as zin:
                    # isComicInfo = "ComicInfo.xml" in zin.namelist()
                    json_data = json.loads(zin.read("info.json"))
                    logger.debug(f"Loaded Info.json: {json_data}")

                    comicinfo.set_AgeRating(ComicInfo.AgeRating.X_18)

                    comicinfo.set_Web(json_data.get("URL"))

                    comicinfo.set_Title(json_data.get("Title"))
                    logger.debug(f"Set title : {json_data.get('Title')}")

                    comicinfo.set_Writer(json_data.get("Artist"))

                    comicinfo.set_AlternateSeries(json_data.get("Parody"))

                    if re.match(r"(?i)_([0-9]+) - ", file_name):
                        comicinfo.set_Number(re.findall(r"_([0-9]+) - ", file_name)[0])
                    elif findChapter(file_name):
                        comicinfo.set_Number(findChapter(file_name))
                    elif re.match(r"(?i)ch.(?:\s|.|)([0-9]+)", file_name):
                        comicinfo.set_Number(re.findall(r"_([0-9]+) - ", file_name)[0])
                    elif re.match(r"(?i)ch.(?:\s|.|)([0-9]+-[0-9]+)", file_name):
                        comicinfo.set_Number(re.findall(r"_([0-9]+) - ", file_name)[0])
                    elif comicinfo and json_data:
                        if re.match(r"(?i)_([0-9]+) - ", json_data.get("Title")):
                            comicinfo.set_Number(re.findall(r"_([0-9]+) - ", json_data.get("Title"))[0])
                        elif re.match(r"(?i)ch.(?:\s|.|)([0-9]+)", json_data.get("Title")):
                            comicinfo.set_Number(re.findall(r"_([0-9]+) - ", json_data.get("Title"))[0])
                        elif re.match(r"(?i)ch.(?:\s|.|)([0-9]+-[0-9]+)", json_data.get("Title")):
                            comicinfo.set_Number(re.findall(r"_([0-9]+) - ", json_data.get("Title"))[0])
                        elif re.match(r"(?i)([0-9]+)(?:\.cbz)", file_name):
                            comicinfo.set_Number(re.findall(r"(?i)([0-9]+)(?:\.cbz)", file_name)[0])
                        elif re.match(r"_Chapter", file_name):
                            comicinfo.set_Number("0")
                        else:
                            comicinfo.set_Number("0")

                    elif re.match(r"(?i)([0-9]+)(?:\.cbz)", file_name):
                        comicinfo.set_Number(re.findall(r"(?i)([0-9]+)(?:\.cbz)", file_name)[0])
                    elif re.match(r"_Chapter", file_name):
                        comicinfo.set_Number("0")
                    else:
                        comicinfo.set_Number("0")

                    logger.debug(f"Set Number: {comicinfo.get_Number()}")
                    magazine = json_data.get("Magazine")
                    if not magazine:
                        logger.debug("Not magazine resorting to title")
                        comicinfo.set_Series(json_data.get("Title"))
                        logger.debug(f"Set Series: {json_data.get('Title')}")
                    else:
                        if isinstance(magazine, list):
                            magazine = magazine[0]
                        logger.debug(f"Processing magazine: {magazine}")
                        if not fetchChapter(magazine) and not fetchVolume(magazine):
                            r = r"(([\d]{4})-([\d]{2})(?:-([\d]{2}))?)"
                            magazine_match = re.findall(r, magazine)

                            if magazine_match:
                                magazine_name = re.sub("\s\s+", " ",
                                                       remove_text_inside_brackets(remove_chapter(magazine)))
                                magazine_match = magazine_match[0]
                                magazine_name = magazine_name.replace(magazine_match[0],
                                                                      "")  # Set magazine name as Name - year
                                comicinfo.set_Series(magazine_name)
                                logger.debug(f"Set Series: {magazine_name}")

                                comicinfo.set_Volume(magazine_match[1])
                                logger.debug(f"Set Volume: {magazine_match[1]}")
                                if magazine_match[2]:
                                    comicinfo.set_Number("0")
                                    logger.debug(f"Set Number:0")
                            else:
                                comicinfo.set_Number("0")

                                re.findall(r"(\d{4})", magazine)
                                magazine_name = re.sub("\s\s+", " ",
                                                       remove_chapter(remove_text_inside_brackets(magazine)))
                                comicinfo.set_Series(magazine_name)
                                comicinfo.set_Number("0")

                                volume = re.findall(r"(\d{4})", magazine)
                                if volume:
                                    comicinfo.set_Volume(volume[0])
                        else:
                            chapter = fetchChapter(magazine)
                            if chapter:
                                comicinfo.set_Number(chapter[0])
                                logger.debug(f"Set Number: {chapter[0]}")
                            volume = fetchVolume(magazine)
                            if volume:
                                comicinfo.set_Volume(volume[0])
                                logger.debug(f"Set Volume: {volume[0]}")


                    comicinfo.set_Publisher(json_data.get("Publisher"))

                    comicinfo.set_LanguageISO(iso639.Language.from_name(json_data.get("Language")).part1)

                    comicinfo.set_Summary(json_data.get("Description"))

                    comicinfo.set_Genre(", ".join(json_data.get("Tags")))

                    date = datetime.datetime.strptime(json_data.get("Released"), "%Y-%m-%d %H:%M:%S %Z")

                    comicinfo.set_Year(date.year)

                    comicinfo.set_Month(date.month)

                    comicinfo.set_Day(date.day)
                    json_data["Notes"] = "Converted from Info.json to ComicInfo.xml with Manga-Manager"
                    comicinfo.set_Notes(json.dumps(json_data))

                    # comicinfo.set_Number(3)
                export_io = io.StringIO()

                if not isComicInfo:
                    try:
                        comicinfo.export(export_io, 0)
                        _export_io = export_io.getvalue()
                        print(_export_io)

                    except AttributeError as e:
                        logger.info(f"Attribute error :{str(e)}")
                        continue

                    except Exception as e:
                        logger.error(e)
                        continue

                    with zipfile.ZipFile(file_path, mode='a', compression=zipfile.ZIP_STORED) as zf:
                        # We finally append our new ComicInfo file
                        zf.writestr("ComicInfo.xml", _export_io)
                        logger.debug("[Write] New ComicInfo.xml added to the file")
                else:
                    MangaManager.MetadataManagerLib.cbz_handler.WriteComicInfo(
                        MetadataManagerLib.models.LoadedComicInfo(file_path, comicInfo=comicinfo)).to_file(
                        skip_backup=False, skip_if_comicinfo_is_present=False)
                    logger.debug("[Write] New ComicInfo.xml added to the file after backup")

                parent_folder = pathlib.Path(scanPath, cleanFilename(comicinfo.get_Series().strip()))
                parent_folder = parent_folder.resolve(strict=False)

                print("New parent folder:" + str(parent_folder))
                parent_folder.mkdir(exist_ok=True, parents=True)
                try:
                    parent_folder.mkdir(exist_ok=True, parents=True)
                except OSError as e:
                    if not "WinError 123" in str(e):
                        raise e
                    parent_folder = pathlib.Path(scanPath, cleanFilename(str(comicinfo.get_Series()).strip()))
                    parent_folder = parent_folder.resolve(strict=False)
                    parent_folder.mkdir(exist_ok=True, parents=True)
                counter = 0
                try:
                    shutil.move(file_path, parent_folder)
                except shutil.Error as e:
                    if f"Destination path '{file_path}' already exists" == str(e):
                        successful = False
                        while not successful:
                            counter += 1
                            new_file_path = file_path.strip(".cbz") + str(counter) + ".cbz"
                            print(file_path)
                            print(new_file_path)
                            shutil.move(file_path, parent_folder.joinpath(new_file_path))


            except PermissionError as e:
                logger.error(e)

                os.makedirs(Path(os.path.dirname(scanPath), "PermissionError_Files"), exist_ok=True)
                # shutil.move(file_path, Path(os.path.dirname(scanPath), "PermissionError_Files"))
            except FileNotFoundError as e:
                raise e
                print(f"File not found: {file_path}")
                logger.error(f"File not found: {file_path}")
            except Exception as e:
                logger.error(e)
                # print(e)
                raise e
        break

if __name__ == '__main__':
    main()
