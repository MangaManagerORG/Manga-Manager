from tkinter import Checkbutton, BooleanVar

from src.Common.utils import parse_bool
from src.MetadataManager.GUI.widgets.MessageBoxWidget import MessageBoxWidget
from src.Settings import Settings, SettingHeading

DISABLED_MESSAGE_BOX = "disabled_message_box"


class OneTimeMessageBox(MessageBoxWidget):
    """
    Messagebox that implements a checkbox to not show again
    """
    def __new__(cls, mb_id, *args, **kwargs):
        if mb_id is None:
            raise AttributeError("mb_id can't be NoneType")
        mb_setting = Settings().get_default(SettingHeading.MessageBox, mb_id, False)
        if parse_bool(mb_setting):
            cls.disabled = True
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, mb_id=None, *args, **kwargs):
        self.mb_id = mb_id
        super().__init__(*args, **kwargs)
        self.with_dontshowagain()

    def with_dontshowagain(self):
        if not self.disabled:
            self.dont_show_again_value = BooleanVar(self, value=False, name="Dont show again checkbtn")
            Checkbutton(self, text="Don't show this window again", variable=self.dont_show_again_value).pack(pady=(10, 0))

    def prompt(self):
        if self.disabled:
            return DISABLED_MESSAGE_BOX
        ret = super().prompt()
        if self.dont_show_again_value.get():
            Settings().set(section=SettingHeading.MessageBox, key=self.mb_id, value=True)
            Settings().save()
        return ret
