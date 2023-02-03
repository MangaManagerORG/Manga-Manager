
from src.Settings.SettingControl import SettingControl

"""
 A section of config controls. Will render under a group in Settings window
"""
class SettingSection:
    pretty_name: str = ''
    values: list[SettingControl] = []

    def __init__(self, name, values=[]):
        self.pretty_name = name
        self.values = values

    def get_control(self, key):
        for v in self.values:
            if v.key == key:
                return v
        return None