import glob
import importlib
import logging
import os
import sys
from pathlib import Path

from src import sources_factory
from src.Common.utils import match_pyfiles_with_foldername
from src.DynamicLibController.extension_manager import extract_folder_and_module
from src.DynamicLibController.models.CoverSourceInterface import ICoverSource
from src.DynamicLibController.models.MetadataSourcesInterface import IMetadataSource

logger = logging.getLogger()

SOURCES_DIR = Path(os.getcwd(), "ExternalSources") # Fixme: Harcodign to use local project files
METADATA_DIR = Path(SOURCES_DIR, "MetadataSources")
METADATA_DIR.mkdir(exist_ok=True)

COVER_DIR = Path(SOURCES_DIR, "CoverSources")
COVER_DIR.mkdir(exist_ok=True)


extensions_path = os.path.expanduser(SOURCES_DIR)
sys.path.append(extensions_path)

# Search for Python files in the extensions directory
cover_sources = [extension for extension in
                   glob.glob(os.path.join(COVER_DIR, "*/**.py"), recursive=True)
                   if match_pyfiles_with_foldername(extension)]

metadata_sources = [extension for extension in
                    glob.glob(os.path.join(METADATA_DIR, "*/**.py"), recursive=True)
                    if match_pyfiles_with_foldername(extension)]


logger.debug(f"Found Cover sources: {', '.join(os.path.basename(cover_source) for cover_source in cover_sources)}")
logger.debug(f"Found Metadata sources: {', '.join(os.path.basename(source_path) for source_path in metadata_sources)}")
# Load metadata

for source_file in cover_sources:
    # Import the extension module
    try:
        extension_module = importlib.import_module(f"CoverSources.{'.'.join(extract_folder_and_module(source_file))}",
                                                   package=SOURCES_DIR)
    except ModuleNotFoundError:
        logger.exception(f"Failed to Import Cover Source: {source_file}")
        continue

    # Get the ExtensionApp subclasses from the module
    extension_classes = [
        cls
        for cls in extension_module.__dict__.values()
        if isinstance(cls, type) and issubclass(cls, ICoverSource) and cls != ICoverSource
    ]
    logger.debug(
        f"Loaded cover sources: {', '.join((extension_class.name for extension_class in extension_classes))}")

    # Instantiate the ExtensionApp subclasses and add them to the list of extensions
    sources_factory["CoverSources"].extend([cls for cls in extension_classes])


for source_file in metadata_sources:
    # Import the extension module
    try:
        extension_module = importlib.import_module(f"MetadataSources.{'.'.join(extract_folder_and_module(source_file))}",
                                                   package=SOURCES_DIR)
    except ModuleNotFoundError:
        logger.exception(f"Failed to Import Metadata Source: {source_file}")
        continue

    # Get the ExtensionApp subclasses from the module
    extension_classes = [
        cls
        for cls in extension_module.__dict__.values()
        if isinstance(cls, type) and issubclass(cls, IMetadataSource) and cls != IMetadataSource
    ]
    logger.debug(f"Loaded metadata sources: {', '.join((extension_class.name for extension_class in extension_classes))}")
    # Instantiate the ExtensionApp subclasses and add them to the list of extensions
    sources_factory["MetadataSources"].extend([cls for cls in extension_classes])





