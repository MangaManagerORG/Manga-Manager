import tkinter

from Extensions.Interface import IExtensionApp


class DummyExtension(IExtensionApp):
    name = "Dummy Extension"
    def serve_gui(self):
        tkinter.Label(self.master_frame, text="Testing the new loading extension loader").pack()
