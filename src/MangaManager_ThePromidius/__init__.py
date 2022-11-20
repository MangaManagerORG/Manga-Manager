import glob
import importlib
import os.path

from MangaManager_ThePromidius.Common.settings import Settings, SettingsSection


# from MetadataManager.extensions import ExtensionController
# print("sad")
# _ext_controller = ExtensionController
# _ext_controller.path_to_extensions = os.path.abspath(os.path.join(os.getcwd(),"MetadataManager/extensions"))
# extension_controller = _ext_controller()

class main_settings(SettingsSection):
    name = "main"
    def initialize(self):
        self.library_path = ""
        self.covers_folder_path = ""


a = os.path.abspath(os.path.join(os.getcwd(),"MetadataManager/extensions"))
modules = glob.glob(os.path.join(a, "*.py"))
if not modules and "src" in os.listdir(os.getcwd()):
    a = os.path.join(os.getcwd(), "src/MangaManager_ThePromidius/MetadataManager/extensions")
    modules = glob.glob(os.path.join(a, "*.py"))
extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
settings_class = Settings("config.ini")
settings_class.import_(main_settings())
random_setting = main_settings
random_setting.name = "random_setting"
random_setting = random_setting()
random_setting.random_dynamic_var = "random_din_ var"

settings_class.import_(random_setting)
for extension in extensions:
    settings_class.import_(importlib.import_module(f".MetadataManager.extensions.{extension}",
                                                   package="src.MangaManager_ThePromidius").SettingsSectionTemplate())
print("te")
settings_class.read()
# settings_class.write()
# Load Extension settings

