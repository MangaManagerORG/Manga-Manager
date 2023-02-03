import abc

from src.Settings.SettingControlType import SettingControlType


class SettingControl(abc.ABC):
    key: str = ''
    name: str = ''
    tooltip: str | None = ''
    type_: SettingControlType
    value = ''
    """
    Only applicable for SettingControlType.Options
    """
    values: list = []

    def __init__(self, key, name, type_, value='', tooltip=''):
        self.key = key
        self.name = name
        self.type_ = type_
        self.value = value
        self.tooltip = tooltip

        if value == '' and type is SettingControlType.Bool:
            self.value = False
