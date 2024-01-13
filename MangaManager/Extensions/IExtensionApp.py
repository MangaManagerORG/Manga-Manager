import abc
import tkinter
from typing import final

from src.Settings import SettingSection, SettingControl, Settings


class IExtensionApp(tkinter.Toplevel, metaclass=abc.ABCMeta):
    """
        
    """
    name = None
    embedded_ui = False
    master = None
    _super = None

    @final
    def __init__(self, master, super_=None, **kwargs):
        """
        Initializes the toplevel window but hides the window.
        """
        if self.name is None:  # Check if the "name" attribute has been set
            raise ValueError(f"Error initializing the {self.__class__.__name__} Extension. The 'name' attribute must be set in the ExtensionApp class.")
        # if self.embedded_ui:
        super().__init__(master=master,**kwargs)
        self.settings = []
        self.title(self.__class__.name)
        self.master = self
        if super_ is not None:
            self._super = super_
        # else:
        #     frame = tkinter.Frame()
        #     self.master_frame = frame
        if not self.master:
            return Exception("Tried to initialize ui with no master window")
        self.serve_gui()
        # self.withdraw()  # Hide the window

    def init_settings(self):
        """
        Method called in extension initialization to load custom settings into main app
        -- Grabs extension settings and loads it to the base setting controller
        :return:
        """
        for section in self.settings:
            section: SettingSection
            for control in section.values:
                control: SettingControl
                Settings().set_default(section.key, control.key, control.value)
        Settings().save()

        # Load any saved settings into memory to overwrite defaults
        self.save_settings()

    def _initialize(self):
        ...
    #     """
    #     Sets the new master window and displays the Toplevel window
    #     :param master:
    #     :return:
    #     """
    #     self.master = master
    #     self.deiconify()
    #     self.serve_gui()

    @abc.abstractmethod
    def serve_gui(self):
        ...


