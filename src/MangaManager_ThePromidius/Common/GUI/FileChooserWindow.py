from __future__ import annotations

import dataclasses

try:
    import pgi
    pgi.require_version("Gtk", "3.0")
    from pgi.repository import Gtk
except (ModuleNotFoundError, NameError, ImportError):
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk


@dataclasses.dataclass
class DummyFile:
    name: str
    def __str__(self):
        return self.name


# TODO: ADJUST THIS CLASS TO FIT UI
class FileChooserWindow(Gtk.Window):
    """
    Filedialog for unix
    """

    def __init__(self, title=None, filters: list[(str, str)] = None):
        """

        :param title: The title of the window
        :param filters: list of (filter_name, mime_type)
        """
        super().__init__(title=title)

    def on_file_clicked(self, initial_dir, filetype_filters, title):
        dialog = Gtk.FileChooserDialog(
            title=title, parent=self, action=Gtk.FileChooserAction.OPEN
        )
        if initial_dir:
            dialog.set_current_folder(initial_dir)
        for file_filter in filetype_filters:
            filetype_filter = Gtk.FileFilter()
            filetype_filter.set_name(file_filter[0])
            filetype_filter.add_pattern(f"*{file_filter[1]}")
            dialog.add_filter(filetype_filter)

        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        response = dialog.run()
        files_selected = None
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            files_selected = dialog.get_filename()
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
            dialog.destroy()
        self.destroy()
        return [DummyFile(name=files_selected)]

    def on_folder_clicked(self):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            parent=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )

        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Select clicked")
            print("Folder selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


def askopenfiles(initialdir, title="Select Files", filetypes=None, parent=None):
    """


    :param initialdir:  path to start browsing at
    :param title: The title of the window
    :param filetypes: Tuple with content: (str:<Name of the extension> , str:<dot + extension: '.cbz'>)
    :param parent: required to monkeypatch tkinter askopenfilename
    :return:
    """

    file_chooser = FileChooserWindow(title)
    if filetypes:
        filetypes = filetypes + (("All Files", ""),)
    else:
        filetypes = (("All Files", ""),)

    return file_chooser.on_file_clicked(initial_dir=initialdir, filetype_filters=filetypes, title=title)


__all__ = [
    "FileChooserWindow"
]
