import re
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
def extract_paths_from_string(input_string):
    return re.findall(r'{(.*?)}', input_string)
class DragAndDropFilesApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Drag and Drop Files")
        self.geometry("400x400")

        self.lb = tk.Listbox(self)
        self.lb.insert(1, "Drag files here")

        # Register the Listbox as a drop target
        self.lb.drop_target_register(DND_FILES)
        self.lb.dnd_bind('<<Drop>>', self.on_drop)

        self.lb.pack(fill="both")

    def on_drop(self, event):
        # Get the list of filenames from the dropped data
        files_str = event.data
        files = extract_paths_from_string(files_str)

        # Split the string into individual filenames
        # Process the dropped files and add their filenames to the Listbox
        for file in files:
            self.lb.insert(tk.END, file)

if __name__ == "__main__":
    app = DragAndDropFilesApp()
    app.mainloop()