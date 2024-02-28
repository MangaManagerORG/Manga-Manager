from MangaManager.LoadedComicInfo.ArchiveFile import ArchiveFile

if __name__ == '__main__':
    with ArchiveFile("!00_SAMPLE_FILE.rar", "r") as rfile:
        print(rfile.namelist())
        print(rfile.read("ComicInfo.xml"))
    with ArchiveFile("!00_SAMPLE_FILE.CBZ", "r") as rfile:
        print(rfile.namelist())
        print(rfile.read("ComicInfo.xml"))
