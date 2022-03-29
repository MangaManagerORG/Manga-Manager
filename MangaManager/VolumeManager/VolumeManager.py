import io
import logging
import os
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import ttk

from lxml.etree import XMLSyntaxError
from typing.io import IO

from ProgressBarWidget import ProgressBar
from .errors import NoFilesSelected
from .models import ChapterFileNameData

launch_path = ""

logger = logging.getLogger(__name__)

ScriptDir = os.path.dirname(__file__)


class App:
    def __init__(self, master: tk.Tk = None):
        self._master = master
        self._checkbutton_1_settings_val = tk.BooleanVar(value=True)  # Auto increase volume number
        self._checkbutton_2_settings_val = tk.BooleanVar(value=False)  # Open FIle Selector dialog after processing
        self._checkbutton_3_settings_val = tk.BooleanVar(value=False)  # Automatic preview
        self.checkbutton_4_settings_val = tk.BooleanVar(value=False)  # Adds volume info to ComicInfo
        self.checkbutton_4_settings_val.trace("w", self._on_checkbutton_4_val_change)

        self.checkbutton_4_5_settings_val = tk.BooleanVar(value=False)  # Only add volumeinfo to ComicInfo -> No rename

        self._label_4_selected_files_val = tk.StringVar(value='')
        self._spinbox_1_volume_number_val = tk.IntVar(value=1)
        self._spinbox_1_volume_number_val_prev = tk.IntVar(value=-1)
        self._spinbox_1_volume_number_val.trace(mode='w', callback=self.validateIntVar)
        self._initialized_UI = False

    def validateIntVar(self, *args):
        try:
            # if self.spinbox_3_volume_var.get() < -1 or
            if not isinstance(self._spinbox_1_volume_number_val.get(), int):
                self.mainwindow.bell()
                self._spinbox_1_volume_number_val.set(-1)
            else:
                self._spinbox_1_volume_number_val_prev.set(self._spinbox_1_volume_number_val.get())
        except tk.TclError as e:
            if str(e) == 'expected floating-point number but got ""' or str(
                    e) == 'expected floating-point number but got "-"':
                return
            elif re.match(r"-[0-9]*", str(e)):
                return
            self.mainwindow.bell()
            if self._spinbox_1_volume_number_val_prev.get() != (-1):
                self._spinbox_1_volume_number_val.set(self._spinbox_1_volume_number_val_prev.get())
                return
            self._spinbox_1_volume_number_val.set(-1)

    def start_ui(self):

        self._frame_1_title = tk.Frame(self._master, container='false')
        # Must keep :
        self._validate_spinbox = (self._frame_1_title.register(self._ValidateIfNum), '%s', '%S')  # Validates spinbox

        # build ui

        self._settings = tk.Frame(self._frame_1_title, container='false')
        self._label_2_settings = ttk.Label(self._settings)
        self._label_2_settings.configure(anchor='center', font='TkMenuFont', text='Settings')
        self._label_2_settings.grid(column='0', row='0', sticky='ew')
        self._settings.columnconfigure('0', weight='1')
        self._checkbutton_1_settings = tk.Checkbutton(self._settings)
        self._checkbutton_1_settings.configure(text='Auto increase volume number after processing',
                                               variable=self._checkbutton_1_settings_val)
        self._checkbutton_1_settings.grid(column='0', row='1', sticky='w')
        self._checkbutton_2_settings = tk.Checkbutton(self._settings)
        self._checkbutton_2_settings.configure(text='Open File selector dialog after processing',
                                               variable=self._checkbutton_2_settings_val)
        self._checkbutton_2_settings.grid(column='0', row='2', sticky='w')
        self._checkbutton_3_settings = tk.Checkbutton(self._settings)
        self._checkbutton_3_settings.configure(text='Automatic preview', variable=self._checkbutton_3_settings_val)
        self._checkbutton_3_settings.grid(column='0', row='3', sticky='w')
        self._checkbutton_4_settings = tk.Checkbutton(self._settings)
        self._checkbutton_4_settings.configure(text='Add volume number to ComicInfo',
                                               variable=self.checkbutton_4_settings_val)
        self._checkbutton_4_settings.grid(column='0', row='4', sticky='w')

        self.checkbutton_4_5_settings = tk.Checkbutton(self._settings)
        self.checkbutton_4_5_settings.configure(text="Don't rename file. Only add to ComicInfo",
                                                variable=self.checkbutton_4_5_settings_val, state="disabled")
        self.checkbutton_4_5_settings.grid(column=0, row=5, sticky='w', padx=(25, 0))

        self._settings.configure(height='160', highlightbackground='black', highlightcolor='black',
                                 highlightthickness='01')
        self._settings.configure(width='200')
        self._settings.grid(column='0', padx='0 70', pady='10 0', row='3', rowspan='4', sticky='e')
        self._frame_1_title.rowconfigure('3', weight='0')
        self._frame_1_title.columnconfigure('0', pad='15', weight='1')
        self._label_1 = tk.Label(self._frame_1_title)
        self._label_1.configure(font='{Title} 20 {bold}', text='Volume Manager')
        self._label_1.grid(column='0', row='0')
        self._label_2_instructions = tk.Label(self._frame_1_title)
        self._label_2_instructions.configure(font='{subheader} 12 {}',
                                             text='This script will append Vol.XX just before any Ch X.ext / Chapter XX.ext')
        self._label_2_instructions.grid(column='0', row='1')
        self._label_3_subinstructions = tk.Label(self._frame_1_title)
        self._label_3_subinstructions.configure(
            text='This naming convention must be followed for the script to work properly')
        self._label_3_subinstructions.grid(column='0', row='2')
        self._label_4_selected_files = tk.Label(self._frame_1_title)
        self._label_4_selected_files.configure(textvariable=self._label_4_selected_files_val)
        self._label_4_selected_files.grid(column='0', row='3')
        self._button_1_openfiles = tk.Button(self._frame_1_title)
        self._button_1_openfiles.configure(text='Open', width='15')
        self._button_1_openfiles.grid(column='0', row='4')
        self._button_1_openfiles.configure(command=self._open_files)
        self._label_5_volume_number_input = tk.Label(self._frame_1_title)
        self._label_5_volume_number_input.configure(text='Volume number to apply to the selected files')
        self._label_5_volume_number_input.grid(column='0', row='5')
        self._spinbox_1_volume_number = tk.Entry(self._frame_1_title)
        self._spinbox_1_volume_number.configure(justify="center", textvariable=self._spinbox_1_volume_number_val)
        # self._spinbox_1_volume_number.configure(validate='all')
        self._spinbox_1_volume_number.grid(column='0', row='6')
        self._spinbox_1_volume_number.configure(validatecommand=self._validate_spinbox)
        self._button_2_preview = tk.Button(self._frame_1_title)
        self._button_2_preview.configure(text='Preview')
        self._button_2_preview.grid(column='0', row='7')
        self._frame_1_title.rowconfigure('7', pad='20')
        self._button_2_preview.configure(command=self._preview_changes)
        self._treeview_1 = ttk.Treeview(self._frame_1_title)
        self._treeview_1_cols = ['old_name', 'to', 'new_name']
        self._treeview_1_dcols = ['old_name', 'to', 'new_name']
        self._treeview_1.configure(columns=self._treeview_1_cols, displaycolumns=self._treeview_1_dcols)
        self._treeview_1.column('#0', anchor='w', stretch='true', width='0', minwidth='0')
        self._treeview_1.column('old_name', anchor='center', stretch='false', width='525', minwidth='20')
        self._treeview_1.column('to', anchor='center', stretch='false', width='26', minwidth='26')
        self._treeview_1.column('new_name', anchor='center', stretch='true', width='525', minwidth='20')
        self._treeview_1.heading('#0', anchor='w', text='column_1')
        self._treeview_1.heading('old_name', anchor='center', text='OLD NAME')
        self._treeview_1.heading('to', anchor='center', text='to')
        self._treeview_1.heading('new_name', anchor='center', text='NEW NAME')
        self._treeview_1.grid(column='0', row='8')
        self._treeview_1.grid_propagate(0)
        self._frame_1_title.rowconfigure('8', pad='25')
        self._treeview_1.bind('<Button-1>', self._handle_click, add='')
        self._frame_2_finalButtons = tk.Frame(self._frame_1_title)
        self._button_4_clearqueue = tk.Button(self._frame_2_finalButtons)
        self._button_4_clearqueue.configure(font='{Custom} 11 {bold}', text='Clear Queue', width='15')
        self._button_4_clearqueue.grid(column='1', row='0')
        self._button_4_clearqueue.configure(command=self._clear_queue)
        self._button_3_proceed = tk.Button(self._frame_2_finalButtons)
        self._button_3_proceed.configure(font='{Custom} 11 {bold}', text='Proceed', width='15')
        self._button_3_proceed.grid(column='0', row='0')
        self._frame_2_finalButtons.columnconfigure('0', pad='15', weight='1')
        self._button_3_proceed.configure(command=self._pre_process)
        self._frame_2_finalButtons.configure(height='200', width='200')
        self._frame_2_finalButtons.grid(column='0', row='9')
        self._frame_1_title.rowconfigure('9', pad='30')
        self.frame_1_progressbar = ttk.Frame(self._frame_1_title)
        self.frame_1_progressbar.configure(height='200', width='200')
        self.frame_1_progressbar.grid(column='0', row='10')
        self._frame_1_title.rowconfigure('10', pad='10')
        self._frame_1_title.configure(height='800', highlightbackground='red', highlightcolor='red', pady='20')
        self._frame_1_title.configure(width='1150')
        self._frame_1_title.grid(column='0', padx='25', pady='25', row='1', sticky='ew')
        self._frame_1_title.grid_propagate(0)



        self._master.rowconfigure('1', weight='0')
        self._master.columnconfigure('0', pad='25', weight='1')

        # Main widget
        self.mainwindow = self._frame_1_title

        # External config for widgets
        # disable some buttons by default
        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="disabled")
        self._button_3_proceed.configure(state="disabled")
        self._button_4_clearqueue.configure(state="disabled")
        self._treeview_1.tag_configure('monospace', font=('courier',10))
        self._initialized_UI = True
    def run(self):
        self._master.mainloop()

    # UI Controllers
    def _ValidateIfNum(self, s, S):  # Spinbox validator
        # disallow anything but numbers
        valid = S == '' or S.isdigit()
        if not valid:
            self._frame_1_title.bell()
            # logger.info("[VolumeManager] input not valid")
        return valid

    def _on_checkbutton_4_val_change(self, *args):
        if self.checkbutton_4_settings_val.get():
            if self._initialized_UI:
                self.checkbutton_4_5_settings.configure(state="normal")
        else:
            self.checkbutton_4_5_settings_val.set(False)
            if self._initialized_UI:
                self.checkbutton_4_5_settings.configure(state="disabled")

    # def _on_checkbutton_4_5_val_change(self, *args):

    def _handle_click(self, event):
        if self._treeview_1.identify_region(event.x, event.y) == "separator":
            return "break"

    def _open_files(self):

        logger.debug("inside openfiles")
        self.cbz_files_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                                           filetypes=(("CBZ Files", ".cbz"),)
                                                           )
        if not self.cbz_files_path_list:
            # self.tool_volumesetter()
            self._label_4_selected_files_val.set(f"Selected 0 files.")
        else:
            self._label_4_selected_files_val.set(f"Selected {len(self.cbz_files_path_list)} files")
        # self.enableButtons(self.frame_volumesetter)

        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="normal")
        self._button_3_proceed.configure(state="disabled")
        self._button_4_clearqueue.configure(state="normal")

        if self._checkbutton_3_settings_val.get():
            self._preview_changes()

    def _preview_changes(self):

        s = ttk.Style()
        s.configure('Treeview', rowheight=20, rowpady=5, rowwidth=365)
        self._list_filestorename = list[ChapterFileNameData]()
        counter = 0
        if not self.cbz_files_path_list:
            logger.warning("No files selected. Aborting preview")
            self._button_2_preview.configure(state="disabled", relief=tk.RAISED)
            return NoFilesSelected
        if self._initialized_UI:
            self._clear_queue()

        volume_to_apply = self._spinbox_1_volume_number_val.get()

        for cbz_path in self.cbz_files_path_list:

            if isinstance(cbz_path, io.TextIOWrapper):
                filepath = cbz_path.name
                logger.debug(f"[Preview] Adding ' {filepath}' to list")
            else:
                filepath = cbz_path
                logger.debug(f"[Preview] Adding ' {filepath}' to list")
            filename = os.path.basename(filepath)
            regexSearch = re.findall(r"(?i)(.*)((?:Chapter|CH)(?:\.|\s)[0-9]+[.]*[0-9]*)(\.[a-z]{3})", filename)
            if regexSearch:
                r = regexSearch[0]
                file_regex_finds: ChapterFileNameData = ChapterFileNameData(name=r[0], chapterinfo=r[1],
                                                                            afterchapter=r[2], fullpath=filepath,
                                                                            volume=volume_to_apply)
            else:
                # Todo: add warning no ch/chapter detected and using last int as ch identifier
                regexSearch = re.findall(r"(?i)(.*\s)([0-9]+[.]*[0-9]*)(\.[a-z]{3}$)",
                                         filename)  # TODO: this regex must be improved yo cover more test cases
                if regexSearch:
                    r = regexSearch[0]
                    file_regex_finds: ChapterFileNameData = ChapterFileNameData(name=r[0], chapterinfo=r[1],
                                                                                afterchapter=r[2], fullpath=filepath,
                                                                                volume=volume_to_apply)
            new_file_path = os.path.dirname(filepath)
            if self.checkbutton_4_5_settings_val.get():
                newFile_Name = "Filename won't be modified. Vol will be added to ComicInfo.xml"
                file_regex_finds.complete_new_path = filepath
            else:
                newFile_Name = f"{new_file_path}/{file_regex_finds.name} Vol.{str(volume_to_apply).zfill(2)} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}".replace(
                    "  ", " ")
                file_regex_finds.complete_new_path = newFile_Name

            self._list_filestorename.append(file_regex_finds)
            if newFile_Name != "Filename won't be modified. Vol will be added to ComicInfo.xml":
                newFile_Name = "..." + newFile_Name[-60:]
            if self._initialized_UI:
                self._treeview_1.insert(parent='', index='end', iid=counter, text='', tags='monospace',
                                        values=("..." + filepath[-60:],
                                                "🠆",
                                                newFile_Name
                                                ))
                self._treeview_1.yview_moveto(1)
            logger.debug(f"[Preview] Successfully added")
            counter += 1
        # self.cbz_files_path_list = None
        if self._initialized_UI:
            # logger.debug(self._treeview_1.get_children())
            if len(self._treeview_1.get_children()) != 0:
                self._button_3_proceed.configure(state="normal",relief=tk.RAISED)
            self._button_4_clearqueue.config(state="normal", relief=tk.RAISED)


    def _clear_queue(self):
        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="normal")
        self._button_3_proceed.config(state="disabled", text="Proceed", relief=tk.RAISED)
        self._button_4_clearqueue.config(state="disabled", relief=tk.RAISED)
        try:
            logger.debug("Try to clear treeview")
            self._treeview_1.delete(*self._treeview_1.get_children())
            logger.debug("Treeview cleared")

        except AttributeError as e:
            logger.debug(f"Can't clear treeview. -> doesnt exist yet.")
        except Exception as e:
            logger.error("Can't clear treeview", exc_info=e)
        self._list_filestorename = list[ChapterFileNameData]()

    def _pre_process(self):
        self.cbz_files_path_list = tuple[IO]()
        self._button_1_openfiles.configure(state="disabled")
        self._button_2_preview.configure(state="disabled")
        self._button_3_proceed.config(state="disabled", relief=tk.SUNKEN, text="Processing")

        self.process()

        self._treeview_1.delete(*self._treeview_1.get_children())
        self._clear_queue()
        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="disabled")
        self._button_3_proceed.config(state="disabled", text="Proceed", relief=tk.RAISED)

        if self._checkbutton_1_settings_val.get():  # Increases volume number by one
            self._spinbox_1_volume_number_val.set(self._spinbox_1_volume_number_val.get() + 1)

        if self._checkbutton_2_settings_val.get():
            try:
                self._open_files()
            except NoFilesSelected:
                logger.warning("No files selected.")

    def cli_select_files(self, files: list[str]):
        self.cbz_files_path_list = files
        self._preview_changes()

    def cli_set_volume(self, volumeNumber: int):
        self._spinbox_1_volume_number_val.set(volumeNumber)

    def process(self):

        total_times_count = len(self._list_filestorename)
        if self._initialized_UI:
            progressBar = ProgressBar(self._initialized_UI, self.frame_1_progressbar, total_times_count)
        else:
            progressBar = ProgressBar(self._initialized_UI, None, total_times_count)
        if not self.checkbutton_4_5_settings_val.get():
            for item in self._list_filestorename:
                logger.info(f"[VolumeManager] Renaming {item.complete_new_path}")
                oldPath = item.fullpath
                try:
                    os.rename(oldPath, item.complete_new_path)
                    logger.info(f"[VolumeManager] Renamed {item.name}")
                    progressBar.increaseCount()
                except PermissionError as e:
                    if self._initialized_UI:
                        mb.showerror("Can't access the file because it's being used by a different process")
                    logger.error("Can't access the file because it's being used by a different process")
                    progressBar.increaseError()
                except FileNotFoundError as e:
                    if self._initialized_UI:
                        mb.showerror("Can't access the file because it's was not found")
                    logger.error("Can't access the file because it's being used by a different process")
                    progressBar.increaseError()
                except Exception as e:
                    progressBar.increaseError()
                    logger.error("Unhandled exception", exc_info=e)
                progressBar.updatePB()
        if self._initialized_UI:
            progressBar = ProgressBar(self._initialized_UI, self.frame_1_progressbar, total_times_count)
        else:
            progressBar = ProgressBar(self._initialized_UI, None, total_times_count)
        if self.checkbutton_4_settings_val.get():
            logger.info("[VolumeManager] Save to ComicInfo is enabled. Starting process")
            from MetadataManagerLib.MetadataManager import App as taggerApp
            for item in self._list_filestorename:
                try:
                    cominfo_app = taggerApp(disable_metadata_notFound_warning=True)
                    cominfo_app.create_loadedComicInfo_list([item.complete_new_path])
                    cominfo_app.entry_Volume_val.set(item.volume)
                    vol_val = cominfo_app.entry_Volume_val.get()

                    cominfo_app.do_save_UI()
                    progressBar.increaseCount()
                except XMLSyntaxError:
                    logger.error(f"Failed to load ComicInfo.xml file inside file: {item.complete_new_path}'")
                    progressBar.increaseError()
                except PermissionError as e:
                    logger.error(str(e))
                    progressBar.increaseError()
                except Exception as e:
                    logger.error(f"Uncaught exception for file: '{item.complete_new_path}'", exc_info=e)
                    progressBar.increaseError()
                progressBar.updatePB()
