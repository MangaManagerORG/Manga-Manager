import configparser
import io
import os
import random
import sys
import unittest
import warnings
import zipfile

import _tkinter
from PIL import Image
from lxml import etree

from MangaManager.LoadedComicInfo.LoadedComicInfo import COMICINFO_FILE, LoadedComicInfo


def create_dummy_files(nfiles):
    test_files_names = []
    for i in range(nfiles):
        out_tmp_zipname = f"random_image_{i}_not_image.ext.cbz"
        test_files_names.append(out_tmp_zipname)
        with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
            zf.writestr("Dummyfile.ext", "Dummy")
    return test_files_names


def create_test_cbz(nfiles, nimages=4, loaded_cinfo: LoadedComicInfo = None) -> list[str]:
    image = Image.new('RGB', (100, 100), 'white')
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG')

    test_files_names = []
    for i in range(nfiles):
        out_tmp_zipname = f"Test__{i}_Generated{random.randint(1, 6000)}.cbz"
        test_files_names.append(out_tmp_zipname)
        with zipfile.ZipFile(out_tmp_zipname, "w") as zf:
            if loaded_cinfo is not None:
                # noinspection PyProtectedMember
                zf.writestr(COMICINFO_FILE, loaded_cinfo._export_metadata())
            for j in range(nimages):
                zf.writestr(f"{str(j).zfill(3)}.png", buffer.getvalue())

    return test_files_names


class CBZManipulationTests(unittest.TestCase):
    test_files_names = []
    root = None

    def setUp(self) -> None:
        print("Super setup")
        leftover_files = [listed for listed in os.listdir() if listed.startswith("Test__") and listed.endswith(".cbz")]
        for file in leftover_files:
            os.remove(file)

    def tearDown(self) -> None:
        print("Super Teardown:")
        try:
            self.root.destroy()
        except:
            pass
        for filename in self.test_files_names:
            print(f"     Deleting: {filename}")  # , self._testMethodName)
            try:
                os.remove(filename)
            except Exception as e:
                print(e)


class TKinterTestCase(unittest.TestCase):
    """These methods are going to be the same for every GUI test,
    so refactored them into a separate class
    """
    root = None

    def setUp(self):
        ...

    def tearDown(self):
        if self.root:
            try:
                self.root.destroy()
                self.pump_events()
            except:
                pass

    def pump_events(self):
        while self.root.dooneevent(_tkinter.ALL_EVENTS | _tkinter.DONT_WAIT):
            pass


def parameterized_class(attrs, input_values=None, classname_func=None,  **__):
    """ Parameterizes a test class by setting attributes on the class.

        Can be used in two ways:

        1) With a list of dictionaries containing attributes to override::

            @parameterized_class([
                { "username": "foo" },
                { "username": "bar", "access_level": 2 },
            ])
            class TestUserAccessLevel(TestCase):
                ...

        2) With a tuple of attributes, then a list of tuples of values:

            @parameterized_class(("username", "access_level"), [
                ("foo", 1),
                ("bar", 2)
            ])
            class TestUserAccessLevel(TestCase):
                ...

    """

    if isinstance(attrs, str):
        attrs = [attrs]

    input_dicts = (
        attrs if input_values is None else
        [dict(zip(attrs, vals)) for vals in input_values]
    )

    if classname_func:
        warnings.warn(
            "classname_func= is deprecated; use class_name_func= instead. "
            "See: https://github.com/wolever/parameterized/pull/74#issuecomment-613577057",
            DeprecationWarning,
            stacklevel=2,
        )
    def decorator(base_class):
        test_class_module = sys.modules[base_class.__module__].__dict__
        for idx, input_dict in enumerate(input_dicts):
            test_class_dict = dict(base_class.__dict__)
            test_class_dict.update(input_dict)

            name = base_class.__name__ + " Layout=" + input_dict.get("GUI").name

            test_class_module[name] = type(name, (base_class,), test_class_dict)

        # We need to leave the base class in place (see issue #73), but if we
        # leave the test_ methods in place, the test runner will try to pick
        # them up and run them... which doesn't make sense, since no parameters
        # will have been applied.
        # Address this by iterating over the base class and remove all test
        # methods.
        for method_name in list(base_class.__dict__):
            if method_name.startswith("test"):
                delattr(base_class, method_name)
        return base_class

    return decorator


# configparser patch stuff
def custom_get_item(key):
    if key == 'DynamicProgramingParamaters':
        return {'wealth_state_total': 'Just a test 3!'}
    else:
        raise KeyError(str(key))


class CustomConfigParser1(configparser.ConfigParser):
    def __getitem__(self, key):
        if key == 'DynamicProgramingParamaters':
            return {'wealth_state_total': 'Just a test 4!'}
        else:
            raise KeyError(str(key))


class CustomConfigParser2(configparser.ConfigParser):
    def read(self, filenames, *args, **kwargs):
        # Intercept the calls to configparser -> read and replace it to read from your test data
        if './path' == filenames:
            # Option 1: If you want to manually write the configuration here
            self.read_string("[DynamicProgramingParamaters]\nwealth_state_total = Just a test 5!")

            # Option 2: If you have a test configuration file
            # super().read("./test_path")
        else:
            super().read(filenames, *args, **kwargs)


def is_valid_xml(xml:str) -> bool:
    # Load the XML file and XSD schema
    try:
        xml_file = etree.fromstring(xml.encode("utf-8"),parser=etree.XMLParser(encoding='utf-8'))
    except ValueError:
     print("dasd")
    xsd_schema = etree.parse('MangaManager/Common/models/ComicInfo.xds')

    # Create a validator object
    xml_validator = etree.XMLSchema(xsd_schema)

    # Validate the XML file against the XSD schema
    is_valid = xml_validator.validate(xml_file)
    if not is_valid:
        print(xml)
        for error in xml_validator.error_log:
            print(f'{error.message} (line {error.line}, column {error.column})')
    return is_valid
