import tkinter

from src.Common.progressbar import ProgressBar
from src.MetadataManager.GUI.utils import center
from src.MetadataManager.GUI.widgets import ProgressBarWidget


class LoadingWindow(tkinter.Toplevel):
    initialized: bool = False
    # abort_flag:bool = None

    def __init__(self, total):
        super().__init__()
        content = tkinter.Frame(self,background="white",borderwidth=3,border=3,highlightcolor="black",highlightthickness=2,highlightbackground="black")
        content.pack(ipadx=20, ipady=20,expand=False,fill="both")

        self.title = "Loading Files"
        self.loading_label_value = tkinter.StringVar(content, name="Loading_label")
        self.loading_label = tkinter.Label(content, textvariable=self.loading_label_value)
        # Removing titlebar from the Dialogue
        self.geometry("300x100+30+30")
        # Make the windows always on top
        self.attributes("-topmost", True)
        self.lift()
        self.abort_flag = False
        # Force focus on this window
        self.grab_set()
        center(self)

        self.overrideredirect(True)

        self.pb = ProgressBarWidget(content)

        self.pb.pb_label.configure(justify="center",background="white")
        self.pb.pb_label.pack(expand=False, fill="x", side="top")
        self.pb.set_template(f"Loaded:{ProgressBar.PROCESSED_TAG}/{ProgressBar.TOTAL_TAG}\n")
        self.pb.start(total)

        abort_btn = tkinter.Button(content,text="Abort",command=self.set_abort)
        abort_btn.pack()
        self.initialized = True
    def is_abort(self):
        return self.abort_flag
    def set_abort(self,*_):
        if self.initialized:
            self.abort_flag = True
            self.pb.set_template("Aborting...\n")
            self.after(2000, self.finish_loading)
    #
    #     self.pb = ProgressBar()
    #     self.pb.set_template(f"Loaded:{ProgressBar.PROCESSED_TAG}/{ProgressBar.TOTAL_TAG}\n")

    def loaded_file(self, value: str):
        if self.initialized:
            self.pb.set_template(f"Loading: {ProgressBar.PROCESSED_TAG}/{ProgressBar.TOTAL_TAG}\nLast loaded: '{value}'")
            self.pb.increase_processed()

    def finish_loading(self):
        if self.initialized:
            self.grab_release()
            self.destroy()



if __name__ == '__main__':
    root = tkinter.Tk()
    a = LoadingWindow(2,False)
    a.loaded_file("asda")
    root.mainloop()
