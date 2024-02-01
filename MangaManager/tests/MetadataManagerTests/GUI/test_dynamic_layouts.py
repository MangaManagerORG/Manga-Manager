import glob
import importlib
import os

from src.MetadataManager import MetadataManagerGUI
from tests.common import create_dummy_files, TKinterTestCase, parameterized_class

layouts_path = os.path.abspath("src/Layouts")

modules = glob.glob(os.path.join(layouts_path, "*.py"))

extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
loaded_layouts = []
for ext in extensions:
    loaded_layouts.append([importlib.import_module(f'.{ext}',
                                                                  package="src"
                                                                          ".Layouts").Layout])


@parameterized_class(('GUI',), loaded_layouts)
class DynamicLayoutTests(TKinterTestCase):
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

    def test_all_fields_are_populated(self):
        self.root = self.GUI()
        app: MetadataManagerGUI.GUIApp = self.root
        app.is_test = True
        app.title(f"test_all_fields_are_populated_{app.name}")
        print("Assert all fields are registered")
        self.assertTrue(app.widget_mngr.get_tags())
        self.pump_events()