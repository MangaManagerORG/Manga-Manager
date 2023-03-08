import glob
import importlib
import os

from logging_setup import add_trace_level
from src.MetadataManager.MetadataManagerGUI import GUIApp
from tests.common import TKinterTestCase, parameterized_class

add_trace_level()
layouts_path = os.path.abspath("src/Layouts")
print(layouts_path)

modules = glob.glob(os.path.join(layouts_path, "*.py"))
print(f"Found modules: [{', '.join(modules)}]")
extensions = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]
print(f"Found extensions: [{', '.join(extensions)}]")
loaded_layouts = []
# Note: Layout is the class
for ext in extensions:
    loaded_layouts.append([importlib.import_module(f'.{ext}', package="src.Layouts").Layout])


@parameterized_class(('GUI',), loaded_layouts)
class FetchMetadataFlowTest(TKinterTestCase):

    def test_fetch_online_button_flow(self):

        self.root = app = self.GUI()
        app: GUIApp
        app.is_test = True
        app.title("test_fetch_online_button_flow")

        # Set series name in series widget
        app.widget_mngr.get_widget("Series").set("tensei shitara datta ken")
        app.process_fetch_online()

        print("Assert series name matches")
        self.assertEqual("Tensei Shitara Slime Datta Ken", app.widget_mngr.get_widget("Series").get())
        print("Assert loc series name matches")
        self.assertEqual("That Time I Got Reincarnated as a Slime", app.widget_mngr.get_widget("LocalizedSeries").get())

        app.destroy()
