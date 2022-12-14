import dataclasses
import fnmatch
import os
import tkinter
from idlelib.tooltip import Hovertip
from pathlib import Path
from tkinter import font
from tkinter import ttk, Frame

from src.MetadataManager.GUI.widgets import ScrolledFrameWidget


@dataclasses.dataclass
class DummyFile:
    name: str
    def __str__(self):
        return self.name

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self,path, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        if not completion_list:
            self._completion_list = []
        else:
            self._completion_list = [str(Path(path,item)) for item in completion_list]  # Work with a sorted list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):  # Match case insensitively
                _hits.append(element)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            self.position = self.index(tkinter.END)
        if event.keysym == "Left":
            if self.position < self.index(tkinter.END):  # delete the selection
                self.delete(self.position, tkinter.END)
            else:
                self.position = self.position - 1  # delete one character
                self.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.index(tkinter.END)  # go to end (no selection)
        if len(event.keysym) == 1:
            self.autocomplete()
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion


class TreeviewExplorerWidget(ttk.Treeview):

    def __init__(self,master, *_, **__):
        super(TreeviewExplorerWidget, self).__init__(master)
        self.on_select_hooks:callable = []
        self.nodes:dict = dict()
        self.directory_nodes:dict = dict()
        self.tree = dict()
        self.FOLDER_ICON = tkinter.PhotoImage(
            data="""iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABmJLR0QA/wD/AP+gvaeTAAABF0lEQVQ4jcXQQS8DQRTA8f9sZ7dVdCvsgcSNC4kQ4uJLSIRP4nP4IOJuv4CLi8RNE044oJrVaraz3XkOyyLZTboH8U4zk/d+782D/w71dRheHe2BXcpuzmNz6/RiYqB/ebCOsteA8/luFRyL4r6oSAQz245DtXo+0gCm21sTJc6PHEfPtE8c1y1ua4XXu/QQONMA/Ydnd2ohQNUyo9Zo4q9sgFLFABDd3uzmwPTi8ub89s7vMREQKQWSaKABdDaR1TYdlSYX/iJNyAGsQcZxJQBrvoF64HfS5L1SfT3wOzngtbyuNYNKgNfyujmQmgikfOOFobIFa4Dx8M1A+cZLBJMDL9FTONfw9pXgTVIqCtOLTVix4x/FB+6JXX9v9hbtAAAAAElFTkSuQmCC""")
        self.FILE_ICON = tkinter.PhotoImage(
            data="""iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABmJLR0QA/wD/AP+gvaeTAAAAtklEQVRIid2VSwrCMBRFjyJ06LZK99GhIzfg0H2Jo+6i2YArsE5ewYY03rwoSC88Qj435+VHYItqgQBMH+LiBYzC5FWQ2ayMmYDrrwHFEA+gCOIFJCG7FfNaXzwmpYXvkEtTnSQH3TsBsv4GcAdumXo14Mlyj+N6kZRrKvvUFZyADjhadNbmUpxJz/rD6jM+GdAAZ2AAHhaDtTXfAKiqOgO3UoBgpfrpvGceENRS9qvNMZp3Y3oBGlFzy7XlpJsAAAAASUVORK5CYII=""")
        self.bind('<Double-1>', self._on_select)


    def nothing(self, *event):
        """ # Hacking moment: A function that does nothing, for those times you need it...
        """
        pass
    def _on_select(self,*args):
        if not self.selection():
            return
        self.item(self.selection()[0],open=True)
        for hook in self.on_select_hooks:
            hook(*args)
        return "break"

    def clear(self):
        self.delete(*self.get_children())
        self.nodes = dict()
        self.tree = dict()
        self.directory_nodes = dict()

    def show_nested_items(self, current_path,glob="*.cbz"):
        current_path = str(Path(current_path))
        self.clear()
        files = []
        items = os.scandir(current_path)
        for item in items:
            if item.is_dir():
                node = self.insert('', 'end', text=item.name, open=True, image=self.FOLDER_ICON)
                self.tree[node] = {"path": str(Path(current_path, item.name)),
                                   "is_dir": True}
            else:
                files.append(item)
        for file in fnmatch.filter(files, glob):
            node = self.insert('', 'end', text=file.name, open=True, image=self.FILE_ICON)
            self.tree[node] = {"path": str(file.path),
                               "is_dir": False}


class FileChooser(tkinter.Toplevel):
    def __init__(self, parent, initialdir=None,*_, **__):
        super(FileChooser, self).__init__(parent)
        self.prev_path = [None]
        self.next_path = [None]
        self.current_search_path: Path = Path(initialdir) if initialdir else None
        self.title("File Selector")
        self.geometry("800x600")

        header = Frame(self)
        header.pack(expand=False,fill="x")

        self.search_bar = search_bar = Frame(header, highlightbackground="blue", highlightthickness=2,background="grey")
        search_bar.pack(expand=False, fill="x", pady=10,padx=10,ipady=5,ipadx=1)
        search_bar.bind('<Double-Button-1>', self.change_to_entry)

        control_arrow_frame = Frame(header)
        control_arrow_frame.pack(side="left")

        self.prev_btn = tkinter.Button(control_arrow_frame, text="🡰", command=lambda:self.update_search_bar(self.prev_path[-1]))
        self.prev_btn.pack(side="left")
        tkinter.Button(control_arrow_frame, text="⮥", command= lambda:self.update_search_bar(Path(*self.current_search_path.parts[:-1]))).pack(side="right")


        glob_frame = Frame(header)
        glob_frame.pack(side="right")
        glob_frame.tooltip = Hovertip(glob_frame, "Find all files with the provided glob. (Enables recursiveness)", 20)

        tkinter.Label(glob_frame,text="Glob:  ⁱ").pack(side="left")

        self.glob_entry = ttk.Entry(glob_frame)
        self.glob_entry.insert(0, "*.cbz")
        self.glob_entry.pack(side="right")
        treeview_frame = ScrolledFrameWidget(self).create_frame()

        self.tree = TreeviewExplorerWidget(master=treeview_frame,selectmode="extended")
        self.tree.on_select_hooks.append(self.on_treeview_select)
        self.tree.heading("#0", text='Filename', anchor='n')
        self.tree.pack(expand=True, fill="both")
        self.tree.bind("<FocusIn>", lambda x: self.update_search_bar(self.current_search_path))

        footer = Frame(self)
        footer.pack(side="bottom")

        tkinter.Button(footer,text="Accept", command=self.get_selection).pack()

        self.selection = None
        if self.current_search_path:
            self.update_search_bar(self.current_search_path)

    def update_suggestions(self):
        try:
            list_of_files = os.listdir(self.entry.get())
        except NotADirectoryError:
            list_of_files = []
        self.entry.set_completion_list(self.entry.get(), list_of_files)
        self.entry.event_generate("<Button-1>")

    def change_to_entry(self, *_):
        self.clear_search_chilren()
        self.entry = entry = AutocompleteCombobox(self.search_bar)
        entry.set(self.current_search_path)
        entry.set_completion_list(self.current_search_path, os.listdir(entry.get()))
        entry.bind("<Tab>",lambda x:self.update_suggestions())

        self.entry.focus()
        # entry.bind("<FocusOut>", lambda x: self.update_search_bar(self.entry.get()))
        entry.bind("<Return>", lambda x: self.update_search_bar(self.entry.get()))

        entry.pack(expand=False, fill="x", anchor="center")

    def clear_search_chilren(self, *_):
        """
        Removes all widgets in the search bar frame
        :param event:
        :return:
        """
        for child in self.search_bar.winfo_children():
            child.destroy()

    def update_search_bar(self, new_path):
        """
        Processes the given paths and creates a button instance of each part of the path.
        Displays the buttons in order in the search frame
        :param new_path:
        :return:
        """
        if not new_path:
            return
        if new_path != self.prev_path[-1]:
            self.prev_path.append(self.current_search_path)
        else:
            self.prev_path.pop()
        self.clear_search_chilren()

        parts = Path(new_path).parts
        current_iter_path = ""

        for i, part in enumerate(parts):
            current_iter_path = Path(current_iter_path, part) if current_iter_path else part
            self.current_search_path = current_iter_path
            s = ttk.Style(self)
            # s.theme_use('clam')
            s.configure('flat.TButton', borderwidth=0, width="1", font=1)
            btn = tkinter.Button(master=self.search_bar,
                       text=part,
                       command=lambda x=current_iter_path: self.update_search_bar(x),relief="flat",justify="left", height=1,
                                 anchor="center",padx=2)
            btn["font"] = font.Font(size=7)
            btn.bind('<Button-1>', lambda evenht,x=current_iter_path:self.update_search_bar(x))
            btn.bind('<Double-Button-1>', self.change_to_entry)
            btn.pack(side="left", expand=False, fill="none",)
        self.tree.show_nested_items(current_iter_path,self.glob_entry.get())

    def on_treeview_select(self, *_):
        """
        When an item is selected in the treeview.
        If double click and is directory, browse to that folder
        :param args:
        :return:
        """
        selection = self.tree.selection()
        if not selection or len(selection)>1:
            return
        item = self.tree.tree.get(selection[0])
        if not item.get("is_dir"):
            return
        self.update_search_bar(Path(item.get("path")))
        self.tree.item(self.tree.selection(),open=True)
        return "break"
    # def update_treeview(self,base_path):

    def get_selection(self):
        self.selection = [DummyFile(str(Path(self.tree.tree.get(item).get("path")))) for item in self.tree.selection()]
        self.destroy()

    def get_selected_files(self, *_):

        self.wm_protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window(self)
        return self.selection

    def exit_btn(self):
        self.destroy()
        self.update()


def askopenfiles(parent,*args, **kwargs):
    # root = tkinter.Tk()
    filechooser = FileChooser(parent,*args,**kwargs)
    selection = filechooser.get_selected_files()
    return selection
