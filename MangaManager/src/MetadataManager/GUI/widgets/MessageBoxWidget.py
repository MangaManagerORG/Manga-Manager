from tkinter import Button, Label, Frame, Toplevel

from src.MetadataManager.GUI.scrolledframe import ScrolledFrame
from src.MetadataManager.GUI.utils import center


class MessageBoxButton:
    def __init__(self, id, title):
        self.id = id
        self.title = title


class MessageBoxWidget(Toplevel):
    """A Toplevel widget that represents a message box with a title, content, and buttons."""

    icon_warning = "::tk::icons::warning"
    icon_error = "::tk::icons::error"
    icon_information = "::tk::icons::information"
    icon_question = "::tk::icons::question"

    selected_value = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Setting Geometry
        self.geometry("460x180+100+100")

        self.label = Label(self, text="Dummy_Text", font=("Helvetica", 16), justify="center")
        self.label.pack(side="top", fill="x", expand=False)
        self.label.configure(wraplength=500)

        self.description = Label(self, text="Dummy_Text", font=("monospace", 12), justify="center")
        self.description.pack(side="top", fill="x", expand=False)
        self.description.configure(wraplength=500)

        self._scrolled_frame = ScrolledFrame(master=self, scrolltype="vertical", usemousewheel=True)
        self.content_frame = self._scrolled_frame.innerframe

        self.control_frame = Frame(self)
        self.control_frame.pack(pady=10, side="bottom",anchor="center")

        # Removing titlebar from the Dialogue
        self.overrideredirect(False)

        # Making MessageBox Visible
        center(self)

        # Make the windows always on top
        self.attributes("-topmost", True)
        self.lift()

        # Force focus on this window
        self.grab_set()


    def with_icon(self, icon_path):
        """Adds an icon to the MessageBoxWidget.

        :param icon_path: The path to the icon image.
        :return: The MessageBoxWidget instance.
        """
        self.label.configure(image=icon_path, compound="left")
        return self

    def with_title(self, title):
        """
        Adds a title to the MessageBoxWidget.
        :param title: The text for the title.
        :return: The MessageBoxWidget instance.
        """
        self.title = title
        self.label.configure(text=title)

        return self

    def with_description(self, description):
        self.description.configure(text=description)
        return self

    def with_content(self, content_frame: Frame):
        """
        Adds content to the MessageBoxWidget.
        :param content_frame: The content frame.
        :return: The MessageBoxWidget instance.
        """
        self._scrolled_frame.pack(fill="both", expand=True)
        self.content_frame.pack()

        content_frame.master = self.content_frame
        return self

    def with_actions(self, action_buttons):
        """
        Adds buttons to the MessageBoxWidget.
        :param action_buttons: A list of MessageBoxButton instances.
        :return: The MessageBoxWidget instance.
        """
        # button is a MessageBoxButton class with id, title
        for button in action_buttons:
            Button(self.control_frame, text=button.title, padx=10, pady=5, borderwidth=3,
                   command=lambda btn=button: self._set_selected_value(btn.id)).pack(side="left", ipadx=20)
            Label(self.control_frame).pack(side="left", padx=5)
        return self

    def build(self):
        """
        Builds the MessageBoxWidget.
        :return: The MessageBoxWidget instance.
        """
        return self

    def prompt(self):
        """
        Displays the MessageBoxWidget and waits for a button press.
        :return: The selected value (the value of the pressed button).
        """

        # Set to wait for window to get deleted.
        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        # return the value
        return self.selected_value

    def _set_selected_value(self, value):
        """
        Sets the selected value of the MessageBoxWidget.
        :param value: The selected value.
        """
        self.selected_value = value
        self.destroy()
