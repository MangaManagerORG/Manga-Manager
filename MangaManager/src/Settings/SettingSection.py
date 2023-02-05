from .SettingControl import SettingControl


class SettingSection:
    """
     A section of config controls. Will render under a group in Settings window
    """
    pretty_name: str = ''
    values: list[SettingControl] = []

    def __init__(self, name, key, values=[]):
        self.pretty_name = name
        self.key = key
        self.values = values

    def get_control(self, key):
        for v in self.values:
            if v.key == key:
                return v
        return None
