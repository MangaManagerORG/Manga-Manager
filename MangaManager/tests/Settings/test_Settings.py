import os.path
import unittest

from src.Settings import SettingHeading, Settings


class SettingsTest(unittest.TestCase):

    def tearDown(self):
        if os.path.exists('settings.ini'):
            print('Cleaning up created settings.ini')
            os.remove('settings.ini')

    def test_Settings_will_create_if_nothing_on_disk(self):
        s = Settings()
        self.assertTrue(os.path.exists(s.config_file))

    def test_Settings_will_set_values(self):
        s = Settings()
        s._load_test()
        self.assertEqual(s.get(SettingHeading.Main, 'library_path'), '')

        s.set(SettingHeading.Main, 'library_path', 'test_dir')
        self.assertEqual(s.get(SettingHeading.Main, 'library_path'), 'test_dir')

    def test_Settings_will_write_default_tag_if_not_exists(self):
        s = Settings()
        self.assertNotEqual(s.get(SettingHeading.ExternalSources, 'default_metadata_source'), '')




if __name__ == '__main__':
    unittest.main()
