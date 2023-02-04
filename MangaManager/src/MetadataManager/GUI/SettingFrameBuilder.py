from tkinter import LabelFrame


class SettingFrameBuilder:
    """
        Builds a Frame from a set of SettingControl's
    """
    widgets = {}
    current_frame = ''

    def __init__(self):
        return self

    def with_frame(self, parent_frame, frame_label):
        frame = LabelFrame(master=parent_frame, text=frame_label)
        frame.pack(expand=True, fill="both")
        self.settings_widget[frame_label] = {}
        self.current_frame = frame_label
        return self

    def with_control(self):
        pass