import glob
import importlib
from os.path import dirname, basename, isfile, join

from MangaManager_ThePromidius.Common.Templates.extension import ExtensionGUI

modules = glob.glob(join(join(dirname(__file__),"extensions"), "*.py"))
extensions = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
import  tkinter
root = tkinter.Tk()


class test:
    def __init__(self):
        for extension in extensions:
            extension_app: ExtensionGUI = importlib.import_module(f'extensions.{extension}').ExtensionApp(self)


            # ScrolledFrameWidget()

        root.mainloop()
    def print_test(self):
        print("Test")
test()
# import tkinter as tk
# from tkinter import Menu
#
# # root window
# root = tk.Tk()
# root.title('Menu Demo')
#
# # create a menubar
# menubar = Menu(root, tearoff=False)
# root.config(menu=menubar)
#
# # create a menu
# file_menu = Menu(menubar)
#
# # add a menu item to the menu
# file_menu.add_command(
#     label='Exit',
#     command=root.destroy
# )
#
#
# # add the File menu to the menubar
# menubar.add_cascade(
#     label="File",
#     menu=file_menu
# )
#
# root.mainloop()