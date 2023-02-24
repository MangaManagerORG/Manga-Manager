from src.MetadataManager.GUI.widgets.MessageBoxWidget import MessageBoxWidget
from src.Settings import Settings, SettingHeading


class OneTimeMessageBox(MessageBoxWidget):

    def __init__(self, mb_id, *args, **kwargs):
        self.mb_id = mb_id
        if Settings().get(SettingHeading.MessageBox, mb_id) is None:
            super().__init__()

    def prompt(self) -> bool:
        if Settings().get(SettingHeading.MessageBox, self.mb_id) is None:
            return True