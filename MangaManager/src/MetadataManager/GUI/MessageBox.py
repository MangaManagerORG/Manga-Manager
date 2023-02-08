from tkinter import Button, Label, Frame, Tk, Toplevel

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
        self.geometry("300x120+100+100")

        self.label = Label(self, text="Dummy_Text", font=("Helvetica", 18))
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

    def with_content(self, content_frame):
        """
        Adds content to the MessageBoxWidget.
        :param content_frame: The content frame.
        :return: The MessageBoxWidget instance.
        """
        # I didn't see how you did this, but we can have with_content_frame or with_content
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
                   command=lambda: self._set_selected_value(button.id)).pack(side="left", ipadx=20)
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


if __name__ == '__main__':
    root = Tk()
    a = MessageBoxWidget(root).with_title("Test Message").with_actions(
        [MessageBoxButton(0, "No"), MessageBoxButton(1, "Yes")]).with_icon(MessageBoxWidget.icon_question)
    print(a.prompt())

    root.mainloop()