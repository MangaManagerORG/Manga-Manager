import enum
from tkinter import Button, Label, Frame, Tk, Toplevel

from src.MetadataManager.GUI.scrolledframe import ScrolledFrame
from src.MetadataManager.GUI.utils import center


class MessageBoxReturns(enum.Enum):
    OK = 1
    YES = 1
    NO = 2
    CANCEL = 3


class MessageBox(Toplevel):
    _icon_warning = "::tk::icons::warning"
    _icon_error = "::tk::icons::error"
    _icon_information = "::tk::icons::information"
    _icon_question = "::tk::icons::question"

    selected_value = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setting Geometry
        self.geometry("300x120+100+100")
        
        self.label = Label(self, text="Dummy_Text",font=("Helvetica",18))
        self.label.pack(side="top")

        frame = ScrolledFrame(master=self, scrolltype="vertical", usemousewheel=True)
        frame.pack(fill="both", expand=True)
        self.content_frame = frame.innerframe
        self.content_frame.pack()

        self.control_frame = Frame(self)
        self.control_frame.pack(pady=10)

        # Removing titlebar from the Dialogue
        self.overrideredirect(False)

        # Making MessageBox Visible
        center(self)

    def info(self, title, text):
        self.title = title
        self.label.configure(image=self._icon_information, compound="left")
        self.label.configure(text=text)
        # self.wait_window()

    def warning(self, title, text):
        self.title = title
        self.label.configure(image=self._icon_warning, compound="left")
        self.label.configure(text=text)
        # self.wait_window()

    def error(self, title, text):
        self.title = title
        self.label.configure(image=self._icon_error, compound="left")
        self.label.configure(text=text)
        # self.wait_window()


    def yes_no_question(self, title, text):
        """
        Asks a question. Buttons displayed are [Yes, No]
        :param title:
        :param text:
        :return:
        """
        # Update title and main label
        self.title = title
        self.label.configure(image=self._icon_question, compound="left")
        self.label.configure(text=text)

        # Setup buttons
        Button(self.control_frame,text="Yes",padx=10,pady=5, borderwidth=3, command=lambda:self.set_selected_value(MessageBoxReturns.YES)).pack(side="left", ipadx=20)
        Label(self.control_frame).pack(side="left",padx=5)
        Button(self.control_frame, text="No",padx=10,pady=5, borderwidth=3, command=lambda:self.set_selected_value(MessageBoxReturns.NO)).pack(side="left", ipadx=20)

        # Set to wait for window to get deleted.
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        # return the value
        return self.selected_value

    def set_selected_value(self, value):
        self.selected_value = value
        self.destroy()


if __name__ == '__main__':
    root = Tk()
    a = MessageBox(root)
    print(a.info("Info Message", "Info Message"))
    print(a.warning("Warn Message", "Warning Message"))
    print(a.error("Error Message", "Error Message"))
    print(a.yes_no_question("Question Message", "Question Message"))
    # a.get_selected_value()
    root.mainloop()
