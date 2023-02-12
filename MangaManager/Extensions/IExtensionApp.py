import abc
import tkinter
from typing import final



class IExtensionApp(tkinter.Toplevel, metaclass=abc.ABCMeta):
    """
        
    """
    name = None
    embedded_ui = False
    master_frame = None
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
        self.title(self.__class__.name)
        self.master = self.master_frame = self
        if super_ is not None:
            self._super = super_
        # else:
        #     frame = tkinter.Frame()
        #     self.master_frame = frame

        self.serve_gui()
        # self.withdraw()  # Hide the window

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


