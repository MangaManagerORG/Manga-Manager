import argparse
import logging

from src.MangaManager_ThePromidius.Extensions.WebpConverter.src.WebpConverterPureCLI import WebpConverterPureCLI
from src.WebpConverterLib import WebpConverterLib

LOG: logging.Logger = logging.getLogger()
logging.basicConfig()
if __name__ == '__main__':
    app = WebpConverterLib
    app._pathList = ["List", "Of", "files", "List", "Of", "files", "List", "Of", "files", "List", "Of", "files",
                          "List", "Of", "files", "List", "Of", "files"]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-d', '--debug',
        help="Print lots of debugging statements",
        action="store_const", dest="loglevel", const=logging.DEBUG,
        default=logging.INFO)
    parser.add_argument("-r", help="Select recursive files", action="store_true", dest="recursive")
    parser.add_argument("path", metavar="<path>", help="The path or glob-like path with the files path.")
    args = parser.parse_args()
    app = WebpConverterPureCLI(path=args.path if isinstance(args.path, list) else [args.path]*30, recursive=args.recursive)
    app._log = LOG
    app.run()
