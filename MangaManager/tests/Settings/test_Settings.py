import os.path
import unittest

from src.Settings.Settings import Settings


class SettingsTest(unittest.TestCase):

    def tearDown(self) -> None:
        if os.path.exists('setting.ini'):
            os.remove('settings.ini')

    def test_Settings_will_create_if_nothing_on_disk(self):
        s = Settings('setting.ini')
        self.assertTrue(os.path.exists(s.config_file))



if __name__ == '__main__':
    unittest.main()
