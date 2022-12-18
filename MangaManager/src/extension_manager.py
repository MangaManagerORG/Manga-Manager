# import glob
# import importlib
# import os
#
# from Extensions.Interface import IExtensionApp
#
#
#
# # Extension loader
# def extract_folder_and_module(file_path):
#     file_name, ext = os.path.splitext(os.path.basename(file_path))
#     dir_name = os.path.basename(os.path.dirname(file_path))
#     return dir_name, file_name
#
#
# def match_pyfiles_with_foldername(file_path):
#     folder, file = extract_folder_and_module(file_path)
#
#     return folder == file
#
#
# loaded_extensions = []
#
#
# def load_extensions(extensions_directory) -> list[IExtensionApp]:
#     global EXTENSIONS_DIRECTORY
#     EXTENSIONS_DIRECTORY = extensions_directory
#     global loaded_extensions
#     if not EXTENSIONS_DIRECTORY:
#         raise FileNotFoundError("The extensions directory is not found")
#
#     # Search for Python files in the extensions directory
#     extension_files = [extension for extension in
#                        glob.glob(os.path.join(EXTENSIONS_DIRECTORY, "*/**.py"), recursive=True)
#                        if match_pyfiles_with_foldername(extension)]
#
#     # Load the extensions
#     loaded_extensions = []
#     for extension_file in extension_files:
#         if extension_file in loaded_extensions:
#             continue
#         # Import the extension module
#         extension_module = importlib.import_module(f"Extensions.{'.'.join(extract_folder_and_module(extension_file))}",package=EXTENSIONS_DIRECTORY)
#
#         # Get the ExtensionApp subclasses from the module
#         extension_classes = [
#             cls
#             for cls in extension_module.__dict__.values()
#             if isinstance(cls, type) and issubclass(cls, IExtensionApp) and cls != IExtensionApp
#         ]
#
#         # Instantiate the ExtensionApp subclasses and add them to the list of extensions
#         loaded_extensions.extend([cls for cls in extension_classes])
#     return loaded_extensions
