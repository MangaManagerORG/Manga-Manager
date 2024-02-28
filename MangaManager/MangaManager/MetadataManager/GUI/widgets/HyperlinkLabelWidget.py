import webbrowser
from tkinter.ttk import Frame, Label


class HyperlinkLabelWidget(Frame):
    def __init__(self, master=None, text="", url="", url_text=None, **kwargs):
        Frame.__init__(self, master, **kwargs)
        self.url = url
        self.label = Label(self,text=text, font=("Helvetica", 12), justify="left")
        self.label.pack(side="left")
        self.url_label = Label(self, text=url_text if url_text else url, font=("Helvetica", 12), justify="left")
        self.url_label.configure(foreground="blue", underline=True)
        self.url_label.pack(side="left")
        self.url_label.bind("<1>", lambda e: self.open_url())
        self.url_label.bind("<Enter>", lambda e: self.configure(cursor="hand2"))
        self.url_label.bind("<Leave>", lambda e: self.configure(cursor=""))

    def open_url(self):
        webbrowser.open(self.url)

    def set_text(self, text):
        self.configure(text=text)

    def set_url(self, url):
        self.url = url
