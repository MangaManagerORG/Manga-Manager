import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox as mb

import logging
import os
import sys
import re
import time
from lxml.etree import XMLSyntaxError
from typing.io import IO

from MangaManager.VolumeManager.errors import NoFilesSelected
from MangaManager.VolumeManager.models import ChapterFileNameData, ProgressBarData

launch_path = ""
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]
                    # filename='/tmp/myapp.log'
                    )

velog = logging.info
delog = logging.debug
logging.getLogger('PIL').setLevel(logging.WARNING)
ScriptDir = os.path.dirname(__file__)

class VolumeManagerApp:
    def __init__(self, master: tk.Tk=None):
        self._master = master
        self._checkbutton_1_settings_val = tk.BooleanVar(value=True)  # Auto increase volume number
        self._checkbutton_2_settings_val = tk.BooleanVar(value=False)  # Open FIle Selector dialog after processing
        self._checkbutton_3_settings_val = tk.BooleanVar(value=False)  # Automatic preview
        self.checkbutton_4_settings_val = tk.BooleanVar(value=False)  # Adds volume info to ComicInfo
        self._label_4_selected_files_val = tk.StringVar(value='')
        self._spinbox_1_volume_number_val = tk.IntVar(value=1)
        self._initialized_UI = False

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
        self._checkbutton_4_settings.configure(text='Add volume number to ComicInfo if it exists',
                                               variable=self.checkbutton_4_settings_val)
        self._checkbutton_4_settings.grid(column='0', row='4', sticky='w')
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
        self._spinbox_1_volume_number = tk.Spinbox(self._frame_1_title)
        self._spinbox_1_volume_number.configure(from_='1', state='normal',
                                                textvariable=self._spinbox_1_volume_number_val, to='500')
        self._spinbox_1_volume_number.configure(validate='all')
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
            # logging.info("[VolumeManager] input not valid")
        return valid

    def _handle_click(self, event):
        if self._treeview_1.identify_region(event.x, event.y) == "separator":
            return "break"

    def _open_files(self):

        logging.debug("inside openfiles")
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
        self._button_3_proceed.configure(state="normal")
        self._button_4_clearqueue.configure(state="normal")

        if self._checkbutton_3_settings_val.get():
            self._preview_changes()

    def _preview_changes(self):

        s = ttk.Style()
        s.configure('Treeview', rowheight=20, rowpady=5, rowwidth=365)
        self._list_filestorename = list[ChapterFileNameData]()
        counter = 0
        if not self.cbz_files_path_list:
            raise NoFilesSelected
        if self._initialized_UI:
            self._clear_queue()

        volume_to_apply = self._spinbox_1_volume_number_val.get()

        for cbz_path in self.cbz_files_path_list:
            if isinstance(cbz_path,IO):
                filepath = cbz_path.name
            else:
                filepath = cbz_path
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
            newFile_Name = f"{new_file_path}/{file_regex_finds.name} Vol.{volume_to_apply} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}".replace(
                "  ", " ")
            file_regex_finds.complete_new_path = newFile_Name

            self._list_filestorename.append(file_regex_finds)

            if self._initialized_UI:
                self._treeview_1.insert(parent='', index='end', iid=counter, text='', tags='monospace',
                                       values=("..." + filepath[-60:],
                                               "🠆",
                                               "..." + newFile_Name[-60:]
                                               ))
                self._treeview_1.yview_moveto(1)
            logging.debug(f"[VolumeManager] Inserted item in treeview -> {file_regex_finds.name}")
            counter += 1
        # self.cbz_files_path_list = None
        if self._initialized_UI:
            logging.debug(self._treeview_1.get_children())
            if len(self._treeview_1.get_children()) != 0:
                self._button_3_proceed.configure(state="normal",relief=tk.RAISED)
            self._button_4_clearqueue.config(state="normal", relief=tk.RAISED)

    def _clear_queue(self):
        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="normal")
        self._button_3_proceed.config(state="disabled", text="Proceed", relief=tk.RAISED)
        self._button_4_clearqueue.config(state="disabled", relief=tk.RAISED)
        try:
            logging.debug("Try to clear treeview")
            self._treeview_1.delete(*self.treeview_1.get_children())

        except AttributeError:
            logging.debug("Can't clear treeview. -> doesnt exist yet")
        except Exception as e:
            logging.error("Can't clear treeview", exc_info=e)
        self._list_filestorename = list[ChapterFileNameData]()


    def _pre_process(self):
        self.cbz_files_path_list = tuple[IO]()
        self._button_1_openfiles.configure(state="disabled")
        self._button_2_preview.configure(state="disabled")
        self._button_3_proceed.config(state="disabled", relief=tk.SUNKEN, text="Processing")
        self.process()

        self._treeview_1.delete(*self.treeview_1.get_children())
        self._clear_queue()
        self._button_1_openfiles.configure(state="normal")
        self._button_2_preview.configure(state="disabled")
        self._button_3_proceed.config(state="disabled", text="Proceed", relief=tk.RAISED)

        if self._checkbutton_1_settings_val.get():
            self._open_files()
    
    def cli_select_files(self,files: list[str]):
        self.cbz_files_path_list = files
        self._preview_changes()
    def cli_set_volume(self,volumeNumber: int):
        self._spinbox_1_volume_number_val.set(volumeNumber)
    def process(self):

        total_times_count = len(self._list_filestorename)
        processed_counter = 0
        processed_errors = 0
        if self._initialized_UI:
            pb_root = self.frame_1_progressbar

            style = ttk.Style(pb_root)
            style.layout('text.Horizontal.TProgressbar',
                         [
                             ('Horizontal.Progressbar.trough',
                              {
                                  'children': [
                                      ('Horizontal.Progressbar.pbar',
                                       {
                                           'side': 'left',
                                           'sticky': 'ns'
                                       }
                                       )
                                  ],
                                  'sticky': 'nswe'
                              }
                              ),
                             ('Horizontal.Progressbar.label',
                              {
                                  'sticky': 'nswe'
                              }
                              )
                         ]
                         )
            pb = ttk.Progressbar(pb_root, length=400, style='text.Horizontal.TProgressbar',
                                 mode="determinate")  # create progress bar
            style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')
            label_progress_text = tk.StringVar()
            pb_text = tk.Label(pb_root, textvariable=label_progress_text, anchor=tk.W)
            logging.info("[VolumeManager] Initialized progress bar")
            pb.grid(row=0, column=0, sticky=tk.E)
            pb_text.grid(row=1, column=0, sticky=tk.E)

        for item in self._list_filestorename:
            logging.info(f"[VolumeManager] Renaming {item.complete_new_path}")
            oldPath = item.fullpath
            try:
                os.rename(oldPath, item.complete_new_path)
                processed_counter += 1
                logging.info(f"[VolumeManager] Renamed {item.name}")

            except PermissionError as e:
                if self._initialized_UI:
                    mb.showerror("Can't access the file because it's being used by a different process")
                logging.error("Can't access the file because it's being used by a different process")
                processed_errors += 1
            except FileNotFoundError as e:
                if self._initialized_UI:
                    mb.showerror("Can't access the file because it's was not found")
                logging.error("Can't access the file because it's being used by a different process")
                processed_errors += 1
            except Exception as e:
                processed_errors += 1
                logging.error("Unhandled exception", exc_info=e)
            if self._initialized_UI:
                pb_root.update()
                percentage = ((processed_counter + processed_errors) / total_times_count) * 100
                style.configure('text.Horizontal.TProgressbar',
                                text='{:g} %'.format(round(percentage, 2)))  # update label
                pb['value'] = percentage
                label_progress_text.set(
                f"Renamed: {(processed_counter + processed_errors)}/{total_times_count} files - {processed_errors} errors")


        if self.checkbutton_4_settings_val.get():
            # Process ComicInfo
            logging.info("[VolumeManager] Save to ComicInfo is enabled. Starting process")
            processed_counter = 0
            processed_errors = 0
            if self._initialized_UI:
                label_progress_text.set(
                    f"Processed ComicInfo: {(processed_counter + processed_errors)}/{total_times_count} files - "
                    f"{processed_errors} errors")

                pb_root.update()
                percentage = ((processed_counter + processed_errors) / total_times_count) * 100
                style.configure('text.Horizontal.TProgressbar',
                                text='{:g} %'.format(round(percentage, 2)))  # update label
                pb['value'] = percentage

            from MangaManager.MangaTaggerLib.MangaTagger import MangataggerApp

            for item in self._list_filestorename:

                try:
                    cominfo_app = MangataggerApp()
                    cominfo_app.create_loadedComicInfo_list([item.complete_new_path])
                    cominfo_app.spinbox_3_volume_var.set(item.volume)
                    cominfo_app.parseUI_toComicInfo()
                    cominfo_app.saveComicInfo()
                    processed_counter += 1
                except XMLSyntaxError:
                    logging.error("Failed to load ComicInfo.xml file for file ->"+item.complete_new_path)
                    processed_errors += 1
                except Exception as e:
                    logging.error("Uncaught exception for file ->" + item.complete_new_path, exc_info=e)
                    processed_errors += 1
                if self._initialized_UI:
                    pb_root.update()
                    percentage = ((processed_counter + processed_errors) / total_times_count) * 100
                    style.configure('text.Horizontal.TProgressbar',
                                    text='{:g} %'.format(round(percentage, 2)))  # update label
                    pb['value'] = percentage
                    label_progress_text.set(
                        f"Processed ComicInfo: {(processed_counter + processed_errors)}/{total_times_count} files - "
                        f"{processed_errors} errors")




if __name__ == "__main__":
    root = tk.Tk()
    app = VolumeManagerApp(root)
    app.start_ui()
    app.run()
