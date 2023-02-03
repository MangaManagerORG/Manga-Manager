import abc

from src.Settings.SettingControlType import SettingControlType


class SettingControl(abc.ABC):
    key: str = ''
    name: str = ''
    tooltip: str | None = ''
    type_: SettingControlType
    values = ''