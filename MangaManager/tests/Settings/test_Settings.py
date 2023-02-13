import os.path
import unittest

from src.Settings import Settings, SettingHeading


class SettingsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.last_ini = None
    def tearDown(self):
        if os.path.exists('settings.ini'):
            print('Cleaning up created settings.ini')
            os.remove('settings.ini')
        if self.last_ini:
            if os.path.exists(self.last_ini):
                print(f'Cleaning up created {self.last_ini}')
                os.remove(self.last_ini)

    def test_Settings_will_create_if_nothing_on_disk(self):
        self.last_ini = "test_Settings_will_create_if_nothing_on_disk.ini"
        s = Settings(self.last_ini)
        self.assertTrue(os.path.exists(s.config_file))

    def test_settings_saves_values(self):
        self.last_ini = "test_settings_saves_values.ini"
        s = Settings(self.last_ini)
        s.load()
        self.assertEqual('', s.get(SettingHeading.Main, 'library_path'))
        s.set(SettingHeading.Main, 'library_path', 'test_dir')
        s.save()

        s.load()
        self.assertEqual('test_dir', s.get(SettingHeading.Main, 'library_path'), )

    def test_Settings_will_write_default_tag_if_not_exists(self):
        self.last_ini = "test_Settings_will_write_default_tag_if_not_exists.ini"
        s = Settings(self.last_ini)
        self.assertEqual('', s.get(SettingHeading.Main, 'library_path'))
        s.set(SettingHeading.Main, 'library_path', 'test_dir')
        s.save()

        s.load()
        self.assertEqual(s.get(SettingHeading.Main, 'library_path'), 'test_dir')


if __name__ == '__main__':
    unittest.main()
