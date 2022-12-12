import glob
import importlib
import os

from parameterized import parameterized

from src.MetadataManager import MetadataManagerGUI
from tests.MetadataManagerTests.common import create_dummy_files, TKinterTestCase

layouts_path = os.path.abspath("src/Layouts")
print(layouts_path)

modules = glob.glob(os.path.join(layouts_path, "*.py"))
print(f"Found modules: [{', '.join(modules)}]")
extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
print(f"Found extensions: [{', '.join(extensions)}]")
loaded_layouts = []
for ext in extensions:
    loaded_layouts.append([importlib.import_module(f'.{ext}',
                                                                  package="src"
                                                                          ".Layouts").Layout])
print("sdasdsadsa")
print(loaded_layouts)



class CinfoToUiTest(TKinterTestCase):
    test_files_names = None

    def setUp(self) -> None:
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)
        self.test_files_names = create_dummy_files(2)

        def custom_askopenfiles(*_, **__):
            return [open(filename, "r") for filename in self.test_files_names]

        MetadataManagerGUI.askopenfiles = custom_askopenfiles

    def tearDown(self) -> None:

        print("Teardown:")
        try:
            self.root.destroy()
        except:
            ...
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)

    @parameterized.expand(
        loaded_layouts)
    def test_all_fields_are_populated(self, layout):
        app = self.root = layout()
        app.title(f"test_all_fields_are_populated_{layout.name}")
        self.pump_events()