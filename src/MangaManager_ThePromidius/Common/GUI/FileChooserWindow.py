import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# TODO: ADJUST THIS CLASS TO FIT UI
class FileChooserWindow(Gtk.Window):
    """
    Filedialog for unix
    """

    def __init__(self, title=None, filters:list[(str,str)]=None):
        """

        :param title: The title of the window
        :param filters: list of (filter_name, mime_type)
        """
        super().__init__(title=title)
        self.filters = filters
        box = Gtk.Box(spacing=6)
        self.add(box)
        self.on_file_clicked()
        # button1 = Gtk.Button(label="Choose File")
        # button1.connect("clicked", self.on_file_clicked)
        # box.add(button1)
        #
        # button2 = Gtk.Button(label="Choose Folder")
        # button2.connect("clicked", self.on_folder_clicked)
        # box.add(button2)

    def on_file_clicked(self):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        if self.filters:
            for filter_data in self.filters:
                ext_filter = Gtk.FileFilter()
                ext_filter.set_name(filter_data[0])
                ext_filter.add_mime_type(filter_data[1])
                dialog.add_filter(ext_filter)
        #
        # filter_py = Gtk.FileFilter()
        # filter_py.set_name("Python files")
        # filter_py.add_mime_type("text/x-python")
        # dialog.add_filter(filter_py)
        #
        # filter_any = Gtk.FileFilter()
        # filter_any.set_name("Any files")
        # filter_any.add_pattern("*")
        # dialog.add_filter(filter_any)

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


__all__ = [
    "FileChooserWindow"
]
