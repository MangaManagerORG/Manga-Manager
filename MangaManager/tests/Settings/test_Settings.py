import os.path
import unittest
import shutil

from src.Settings import SettingHeading
from src.Settings.Settings import Settings


class SettingsTest(unittest.TestCase):

    def setUp(self):
        print('Copying default file from ', os.getcwd().replace('tests', 'settings.ini'))
        shutil.copyfile(os.getcwd().replace('tests', 'settings.ini'), 'settings.ini')
    def tearDown(self):
        if os.path.exists('settings.ini'):
            print('Cleaning up created settings.ini')
            os.remove('settings.ini')

    def test_Settings_will_create_if_nothing_on_disk(self):
        s = Settings()
        self.assertTrue(os.path.exists(s.config_file))

    def test_Settings_will_create_if_nothing_on_disk(self):
        s = Settings()
        self.assertEqual(s.get(SettingHeading.Main, 'library_path'), '')
        s.set(SettingHeading.Main, 'library_path', 'test_dir')
        s.save()

        s.load()
        self.assertEqual(s.get(SettingHeading.Main, 'library_path'), 'test_dir')




if __name__ == '__main__':
    unittest.main()
