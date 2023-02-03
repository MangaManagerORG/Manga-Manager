
from src.Settings.SettingControl import SettingControl

"""
 A section of config controls. Will render under a group in Settings window
"""
class SettingSection:
    pretty_name: str = ''
    values: list[SettingControl] = []