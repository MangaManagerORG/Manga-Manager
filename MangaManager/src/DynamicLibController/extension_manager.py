import glob
import importlib
import logging
import os
import sys
from pathlib import Path

from Extensions.IExtensionApp import IExtensionApp
from src import sub_mm_path

logger = logging.getLogger()


# Extension loader
def extract_folder_and_module(file_path):
    file_name, ext = os.path.splitext(os.path.basename(file_path))
    dir_name = os.path.basename(os.path.dirname(file_path))
    return dir_name, file_name


def match_pyfiles_with_foldername(file_path):
    folder, file_ = extract_folder_and_module(file_path)

    return folder == file_


loaded_extensions = []


def load_extensions(extensions_directory,) -> list[IExtensionApp]:
    # EXTENSIONS_DIRECTORY = extensions_directory

    EXTENSIONS_DIRECTORY = Path(sub_mm_path, "Extensions")
    extensions_path = os.path.expanduser(EXTENSIONS_DIRECTORY)
    sys.path.append(extensions_path)

    # Search for Python files in the extensions directory
    extension_files = [extension for extension in
                       glob.glob(os.path.join(EXTENSIONS_DIRECTORY, "*/**.py"), recursive=True)
                       if match_pyfiles_with_foldername(extension)]
    if not extension_files:
        EXTENSIONS_DIRECTORY = os.path.join(os.getcwd(), "Extensions")
        extension_files = [extension for extension in
                           glob.glob(os.path.join(os.getcwd(), "Extensions", "*/**.py"), recursive=True)
                           if match_pyfiles_with_foldername(extension)]

    print(f"Found extensions: {extension_files}")
    # Load the extensions
    loaded_extensions = []
    for extension_file in extension_files:
        if extension_file in loaded_extensions:
            continue
        # Import the extension module
        try:
            extension_module = importlib.import_module(f"Extensions.{'.'.join(extract_folder_and_module(extension_file))}",package=EXTENSIONS_DIRECTORY)
        except ModuleNotFoundError:
            logger.exception(f"Failed to Import Extension: {extension_file}")
            continue
        except Exception:
            logger.exception(f"Failed to Load extension {extension_file}")

        # Get the ExtensionApp subclasses from the module
        extension_classes = [
            cls
            for cls in extension_module.__dict__.values()
            if isinstance(cls, type) and issubclass(cls, IExtensionApp) and cls != IExtensionApp
        ]

        # Instantiate the ExtensionApp subclasses and add them to the list of extensions
        loaded_extensions.extend([cls for cls in extension_classes])
    return loaded_extensions
