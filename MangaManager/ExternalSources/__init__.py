import glob
import importlib
import os
import sys

from src import SOURCES_DIR
from src.Common.utils import match_pyfiles_with_foldername, extract_folder_and_module

metadata_sources = {}
cover_sources = {}


external_sources = os.path.expanduser(SOURCES_DIR)
sys.path.append(external_sources)

global loaded_extensions
if not SOURCES_DIR:
    raise FileNotFoundError("The extensions directory is not found")

# Search for Python files in the extensions directory
extension_files = [extension for extension in
                   glob.glob(os.path.join(SOURCES_DIR, "*/**.py"), recursive=True)
                   if match_pyfiles_with_foldername(extension)]
print(f"Found extensions: {extension_files}")
# Load the extensions
loaded_extensions = []
for extension_file in extension_files:
    if extension_file in loaded_extensions:
        continue
    # Import the extension module
    try:
        extension_module = importlib.import_module(f"{'.'.join(extract_folder_and_module(extension_file))}",package=EXTENSIONS_DIRECTORY)
    except ModuleNotFoundError:
        logger.exception(f"Failed to Import Extension: {extension_file}")
        continue

    # Get the ExtensionApp subclasses from the module
    extension_classes = [
        cls
        for cls in extension_module.__dict__.values()
        if isinstance(cls, type) and issubclass(cls, IExtensionApp) and cls != IExtensionApp
    ]

    # Instantiate the ExtensionApp subclasses and add them to the list of extensions
    loaded_extensions.extend([cls for cls in extension_classes])
