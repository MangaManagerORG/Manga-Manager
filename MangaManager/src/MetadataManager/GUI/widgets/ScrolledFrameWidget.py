import tkinter
from tkinter import Frame

from src.MetadataManager.GUI.scrolledframe import ScrolledFrame


class ScrolledFrameWidget(ScrolledFrame):
    def __init__(self, master, *_, **kwargs):
        super(ScrolledFrameWidget, self).__init__(master, **kwargs)
        self.configure(usemousewheel=True)
        self.paned_window = tkinter.PanedWindow(self.innerframe)
        self.paned_window.pack(fill="both", expand=False)
        self.pack(expand=False, fill='both', side='top')

    def create_frame(self, **kwargs):
        """Creates a subframe and packs it"""
        frame = Frame(self.paned_window)
        frame.pack(**kwargs or {})
        # frame.pack()
        self.paned_window.add(frame)
        return frame