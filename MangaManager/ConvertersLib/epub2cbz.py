import zipfile
import os
import re
import tempfile
import zipfile

# from CommonLib import webp_converter as convert_to_webp
logger = logging.getLogger(__name__)


class epub2cbz:
    def __init__(self, epubsPathList: list[str], convert_to_webp=False):
        self.convert_to_webp = convert_to_webp
        logger.info(f"Loaded file list: \n" + "\n".join(epubsPathList))
        l = len(epubsPathList)
        printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
        for i, epubPath in enumerate(epubsPathList):
            logger.info(f"Processing '{epubPath}'")
            self.zipFilePath = epubPath
            tmpfd, self._tmpname = tempfile.mkstemp(dir=os.path.dirname(self.zipFilePath))
            os.close(tmpfd)
            try:
                self._process()
                # os.remove(self.zipFilePath)
                os.rename(self._tmpname, self.zipFilePath.replace(re.findall(r"(?i).*(\.[a-z]+)", self.zipFilePath)[0],
                                                                  ".cbz"))
                print(" " * int(66 + len(os.path.basename(epubPath))), end="\r")
                print(f"Processed '{os.path.basename(epubPath)}'")
            except Exception as e:
                print("   " * int(61 + len(os.path.basename(epubPath))), end="\r")
                print(f"Error. Not processed '{os.path.basename(epubPath)}'")
                logger.error(f"Error processing '{epubPath}': {str(e)}", exc_info=True)
                os.remove(self._tmpname)
            printProgressBar(i + 1, l, prefix=f"Progress:", suffix='Complete', length=50)
        logger.info("Completed processing for all selected files")

    def _process(self):
        with zipfile.ZipFile(self.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(self._tmpname, 'w') as zout:
                images_in_ImagesFolder = [v for v in zin.infolist() if
                                          "images/" in v.filename]  # Notes all folders to not process them.
                if not images_in_ImagesFolder:
                    raise FileNotFoundError
                covers = [v for v in zin.namelist() if re.match(r"(?i)cover\.[a-z]+", v)]
                if covers:
                    if self.convert_to_webp:
                        # zout.writestr(covers[0],  zin.read(covers[0]))
                        raise NotImplementedError
                        pass
                    else:
                        zout.writestr(covers[0], zin.read(covers[0]))

                for image in images_in_ImagesFolder:
                    image_name = image.filename.split("/")
                    logger.debug(f"Processing file {image.filename}")
                    if re.match(r"(?i).*\.[a-z]+", image_name[-1]):
                        image_name = image_name[-1]
                        zout.writestr(image_name, zin.read(image))
                        logger.debug(f"Added '{image.filename}' to new tempfile")


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


if __name__ == '__main__':
    import pathlib
    from logging.handlers import RotatingFileHandler
    import glob

    PROJECT_PATH = pathlib.Path(__file__).parent
    rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/epub2cbz.log", maxBytes=1025760,
                                                backupCount=1)

    logging.getLogger('PIL').setLevel(logging.WARNING)
    # formatter = logging.Formatter()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - epub2cbz - %(levelname)s - %(message)s',
                        handlers=[rotating_file_handler, ]
                        # filename='/tmp/myapp.log'
                        )
    logger.info("Starting standalone Converter")

    inputStr = input("Write the path to the epub files you want to convert to cbz.")
    if not inputStr:
        print("No files selected")
        exit()
    filenames = glob.glob(inputStr)
    if not filenames:
        print("No files found")
        exit()
    app = epub2cbz(filenames)
