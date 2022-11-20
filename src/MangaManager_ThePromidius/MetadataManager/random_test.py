import tkinter

from MangaManager_ThePromidius.Common.GUI.widgets import CoverFrame

if __name__ == '__main__':
    root = tkinter.Tk()
    a = CoverFrame(root)
    a.serve()
    a.pack(expand=True, fill="y")
    root.mainloop()
