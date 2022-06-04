
import logging
import os
import re
import tkinter as tk
from itertools import cycle
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter.filedialog import askopenfiles

from PIL import ImageTk, Image, UnidentifiedImageError

from CommonLib.ProgressBarWidget import ProgressBar
from .cbz_handler import SetCover
from .models import cover_process_item_info

logger = logging.getLogger(__name__)

ScriptDir = os.path.dirname(__file__)


if os.path.exists("/manga"):
    manga_launch_path = "/manga"
else:
    manga_launch_path = ""
if os.path.exists("/covers"):
    cover_launch_path = "/covers"
else:
    cover_launch_path = ""


class App:
    def __init__(self, master: tk.Toplevel):
        self.deleteCoverFilePath = f"{ScriptDir}/DELETE_COVER.jpg"
        self.recoverCoverFilePath = f"{ScriptDir}/RECOVER_COVER.jpg"
        self.master = master

        self.do_overwrite_first = tk.BooleanVar()
        self.checkbox0_settings_val = tk.BooleanVar(value=True)
        self.checkbox1_settings_val = tk.BooleanVar(value=False)
        self.checkbox2_settings_val = tk.BooleanVar(value=False)
        self.covers_path_in_confirmation = {}
        self._initialized_UI = False

    def start_ui(self):
        # build ui
        logger.debug("Starting UI")
        self.master.title("Cover Manager")
        # build ui
        self._frame_coversetter = tk.Frame(self.master)
        self._canvas_frame = tk.Frame(self._frame_coversetter)
        self._canvas1_coverimage = tk.Canvas(self._canvas_frame)
        self._canvas1_coverimage.configure(background='#878787', height='260', width='190')
        self._canvas1_coverimage.grid(column='0', row='0')
        self._label_coverimagetitle = tk.Label(self._canvas_frame)
        self._label_coverimagetitle.configure(text='OPEN ONE OR MORE IMAGES')
        self._label_coverimagetitle.grid(column='0', row='1')
        self._button3_load_images = tk.Button(self._canvas_frame)
        self._button3_load_images.configure(text='Select covers')
        self._button3_load_images.grid(column='0', row='0')
        self._button3_load_images.configure(command=self.opencovers)

        self._button1_next = tk.Button(self._canvas_frame)
        self._button1_next.configure(justify='center', state='disabled', text='Next cover')
        self._button1_next.grid(column='0', row='2', sticky='ew')
        self._button1_next.grid_propagate(0)
        self._button1_next.configure(command=self.display_next_cover)

        self._canvas_frame.configure(width='200')
        self._canvas_frame.place(anchor='nw', height='310', relx='0.01', rely='0.02', width='200', x='9', y='0')
        self._controller_buttons_frame = tk.Frame(self._frame_coversetter)
        self._do_overwrite_first_label = tk.Label(self._controller_buttons_frame)
        self._do_overwrite_first_label.configure(text='Replace current cover?')
        self._do_overwrite_first_label.grid(column='0', row='0', sticky='ew')
        self._controller_buttons_frame.rowconfigure('0', pad='5')
        self._overwrite_yes_button = tk.Button(self._controller_buttons_frame)
        self._overwrite_yes_button.configure(text='No')
        self._overwrite_yes_button.grid(column='0', row='1', sticky='ew')
        self._controller_buttons_frame.rowconfigure('1', pad='10')
        self._overwrite_yes_button.configure(command=self.set_do_overwrite_first_label)
        self._separator_2 = ttk.Separator(self._controller_buttons_frame)
        self._separator_2.configure(orient='horizontal')
        self._separator_2.grid(column='0', row='2', sticky='ew')
        self._controller_buttons_frame.rowconfigure('2', pad='10')
        self._button2_openfile = tk.Button(self._controller_buttons_frame)
        self._button2_openfile.configure(text='Open File to Apply this cover')
        self._button2_openfile.grid(column='0', row='3', sticky='ew')
        self._controller_buttons_frame.rowconfigure('3', pad='10')
        self._button2_openfile.configure(command=self.add_file_to_list)
        self._button5_delete_covers = tk.Button(self._controller_buttons_frame)
        self._button5_delete_covers.configure(text='Open Files to Delete their cover')
        self._button5_delete_covers.grid(column='0', row='4', sticky='ew')
        self._controller_buttons_frame.rowconfigure('4', pad='10')
        self._button5_delete_covers.configure(command=self._deleteCover)

        self._controller_buttons_frame.rowconfigure('5', pad='10')
        self._button6_reselect_covers = tk.Button(self._controller_buttons_frame)
        self._button6_reselect_covers.configure(text='Select new set of covers')
        self._button6_reselect_covers.grid(column='0', row='6', sticky='ew')
        self._button6_reselect_covers.configure(command=self.opencovers)

        self._controller_buttons_frame.rowconfigure('6', pad='10')

        self._button_8_recover = tk.Button(self._controller_buttons_frame)
        self._button_8_recover.configure(text='Recover covers')
        self._button_8_recover.grid(column='0', row='2', sticky='ew')
        self._button_8_recover.configure(command=self.recover)
        self._controller_buttons_frame.configure(borderwidth='0', height='200', highlightbackground='grey',
                                                 highlightcolor='grey')
        self._controller_buttons_frame.configure(highlightthickness='1', padx='10', pady='10', width='200')
        self._controller_buttons_frame.place(anchor='nw', relx='0.01', rely='0.485', x='15', y='0')
        self._settings = tk.Frame(self._frame_coversetter)
        self._label_2_settings = ttk.Label(self._settings)
        self._label_2_settings.configure(text='Settings')
        self._label_2_settings.grid(column='0', row='0', sticky='w')
        self._checkbox0_settings = tk.Checkbutton(self._settings)

        self._checkbox0_settings.configure(text='Display next cover after adding a file to the queue (not delete)',
                                           variable=self.checkbox0_settings_val)
        self._checkbox0_settings.grid(column='0', row='1', sticky='w')

        self._checkbox1_settings = tk.Checkbutton(self._settings)
        self._checkbox1_settings.configure(text='Open File selector dialog after adding to queue (default replace: no)',
                                           variable=self.checkbox1_settings_val)
        self._checkbox1_settings.grid(column='0', row='2', sticky='w')

        self._checkbox2_settings = tk.Checkbutton(self._settings)
        self._checkbox2_settings.configure(text='Convert images to webp (may take a lot of time)',
                                           variable=self.checkbox2_settings_val)
        self._checkbox2_settings.grid(column='0', row='3', sticky='w')

        self._settings.configure(height='160', highlightbackground='black', highlightcolor='black',
                                 highlightthickness='1')
        self._settings.configure(width='200')
        self._settings.place(anchor='nw', relx='0.03', rely='0.85', x='0')
        s = ttk.Style()
        s.configure('Treeview', rowheight=65, rowpady=5, rowwidth=360)

        self._treeview1 = ttk.Treeview(self._frame_coversetter)
        self._treeview1.tag_configure('monospace', font=('courier', 10))
        self._treeview1_cols = ['column3', 'overwrite']
        self._treeview1_dcols = ['column3', 'overwrite']
        self._treeview1.configure(columns=self._treeview1_cols, displaycolumns=self._treeview1_dcols)
        self._treeview1.column('#0', anchor='center', stretch=False, width=80)
        self._treeview1.column('column3', anchor='w', stretch='true', width='260', minwidth='20')
        self._treeview1.column('overwrite', anchor='center', stretch='false', width='60', minwidth='20')
        self._treeview1.heading('column3', anchor='center', text='Queue')
        self._treeview1.heading('overwrite', anchor='center', text='Overwrite')
        self._treeview1.bind('<Button-1>', self._handle_click, add='')

        self._treeview1.place(anchor='nw', height='350', relheight='0.14', relwidth='0.69', relx='0.28', rely='0.02')

        self._frame_6 = tk.Frame(self._frame_coversetter)
        self._button_7_clearqueue = tk.Button(self._frame_6)
        self._button_7_clearqueue.configure(compound='top', font='TkTextFont', text='Clear Queue')
        self._button_7_clearqueue.grid(column='0', row='0', sticky='ew')
        self._frame_6.rowconfigure('0', pad='5')
        self._button_7_clearqueue.configure(command=self.clearqueue)
        self._button4_proceed = tk.Button(self._frame_6)
        self._button4_proceed.configure(text='Proceed')
        self._button4_proceed.grid(column='0', columnspan='2', row='1', sticky='ew')
        self._frame_6.rowconfigure('1', pad='5')
        self._button4_proceed.configure(command=self.process)

        self._frame_6.rowconfigure('2', pad='5')

        self._frame_6.configure(height='200', width='200')
        self._frame_6.place(anchor='n', relx='0.62', rely='0.69', x='0', y='0')
        self._progressbar_frame = tk.Frame(self._frame_coversetter)
        self._progressbar_frame.lower(self._settings)
        self._progressbar_frame.place(anchor='nw', height='80', relx='0.4', rely='0.79', width='400', x='0', y='0')
        self._frame_coversetter.configure(height='690', highlightbackground='grey', highlightcolor='black',
                                          highlightthickness='1', width='800')
        self._frame_coversetter.pack(anchor='center', expand='true', side='top')

        # Main widget
        self._mainwindow = self._frame_coversetter

        self.disableButtons(self._frame_coversetter)
        self._button3_load_images.config(state="normal")
        self._button5_delete_covers.config(state="normal")
        self._button_8_recover.config(state="normal")
        self._initialized_UI = True
        # Main widget
        logger.debug("UI initialised")

    def run(self):
        self.master.mainloop()

    # UI Controllers
    def set_do_overwrite_first_label(self):
        if self.do_overwrite_first.get():
            self.do_overwrite_first.set(False)
            self._overwrite_yes_button.configure(text="No")
        else:
            self.do_overwrite_first.set(True)
            self._overwrite_yes_button.configure(text="Yes")

    def opencovers(self):
        """
        Open tkinter.askopenfilename all covers that are going to be placed inside each chapter and loads iter cycle
        """

        def show_first_cover(cls):
            logger.debug("Printing first image in canvas")
            cls.thiselem, cls.nextelem = cls.nextelem, next(cls.licycle)
            image = Image.open(cls.thiselem.name)
            image = image.resize((190, 260), Image.ANTIALIAS)
            cls.image = ImageTk.PhotoImage(image)
            cls.canvas_image = cls._canvas1_coverimage.create_image(0, 0, anchor=tk.NW, image=cls.image)
            cls._label_coverimagetitle.configure(text=os.path.basename(cls.thiselem.name))

        logger.debug("Selecting covers")

        self._button3_load_images.configure(text="Loading...", state="disabled")

        covers_path_list = askopenfiles(initialdir=cover_launch_path,
                                        title="Open all covers you want to work with:"
                                        )
        self.licycle = cycle(covers_path_list)
        try:
            self.nextelem = next(self.licycle)
        except StopIteration:
            # self.button3_load_images.configure(text="Select covers")
            mb.showwarning("No file selected", "No images were selected.")
            self.image = None
            self._button3_load_images.configure(text="Select covers", state="normal")
            self._button3_load_images.grid()
            logger.error("No images were selected when asked for")
            raise
        self.prevelem = None
        self.enableButtons(self._frame_coversetter)
        try:
            self._button3_load_images.grid_remove()
            self.canvas_image = ""
            show_first_cover(self)

        except UnidentifiedImageError as e:
            mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
            logger.error(f"UnidentifiedImageError - Image file: {self.thiselem.name}")
            self._button3_load_images.configure(text="Select covers", state="normal")
            self._button3_load_images.grid()

    def display_next_cover(self):
        logger.info(f"Printing next cover in canvas - {self.nextelem}")
        self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        try:
            rawimage: Image = Image.open(self.thiselem.name)
            image = rawimage.resize((190, 260), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(image)
            # logger.debug(self.label.gettags("IMG10"))
            self._canvas1_coverimage.itemconfig(self.canvas_image, image=self.image)
            self._label_coverimagetitle.configure(text=os.path.basename(self.thiselem.name))

        except UnidentifiedImageError as e:
            mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
            logger.error(f"UnidentifiedImageError - Image file: {self.thiselem.name}")

    def add_file_to_list(self, delete=False, recover=False):
        logger.debug("Adding files to processing list")
        option_delete = False
        option_overwrite = False
        option_recover = False
        title = ""
        if delete:
            option_delete = True
            image_path = self.deleteCoverFilePath
            title = "Select files to delete cover"
        elif recover:
            option_recover = True
            image_path = self.recoverCoverFilePath
            title = "Select files to recover cover"
        else:
            option_overwrite = self.do_overwrite_first.get()
            image_path = self.thiselem.name
            if option_overwrite:
                title = "Select files to overwrite cover"
            else:
                title = "Select file to apply cover"
        cbzs_path_list = askopenfiles(initialdir=manga_launch_path, title=title,
                                      filetypes=(("CBZ Files", ".cbz"),)
                                      )

        image = Image.open(image_path)
        image = image.resize((40, 60), Image.ANTIALIAS)
        self.image_in_confirmation = ImageTk.PhotoImage(image)
        if not self.covers_path_in_confirmation.get(str(self.image_in_confirmation)):
            self.covers_path_in_confirmation[str(self.image_in_confirmation)] = list[cover_process_item_info]()

        for iterated_file_path in cbzs_path_list:
            iterated_file_path = iterated_file_path.name
            file_format = re.findall(r"(?i)\.[a-z]+$", image_path)[0]
            tmp_info = cover_process_item_info(
                cbz_file=iterated_file_path,
                cover_path=image_path,
                cover_name=os.path.basename(image_path),
                cover_format=file_format,
                coverDelete=option_delete,
                coverRecover=option_recover,
                coverOverwrite=option_overwrite
            )
            tmp_info.imageObject = self.image_in_confirmation

            self.covers_path_in_confirmation[str(self.image_in_confirmation)].append(tmp_info)
            logger.info(f"Added to the processing queue -> {os.path.basename(iterated_file_path)} ")

            # Adding file is done. Just adding visual feedback in UI
            displayed_file_path = f"...{os.path.basename(iterated_file_path)[-47:]}"
            overwrite_displayedval = self.do_overwrite_first.get() if not delete else "Delete"
            self._treeview1.insert(parent='', index='end', image=self.image_in_confirmation, tags='monospace',
                                   values=(displayed_file_path, overwrite_displayedval))
            self._treeview1.yview_moveto(1)
        selected_files = True if cbzs_path_list else False
        cbzs_path_list = tuple()
        self.do_overwrite_first.set(False)
        self._overwrite_yes_button.configure(text="No")
        self._button_7_clearqueue.config(state="normal")
        self._button4_proceed.config(state="normal", text="Proceed")
        if not delete and not recover:
            if self.checkbox0_settings_val.get():
                self.display_next_cover()
            if self.checkbox1_settings_val.get() and selected_files:
                self.add_file_to_list()

    def _deleteCover(self):
        self.add_file_to_list(delete=True)

    def process(self):
        logger.debug("Starting processing of files.")
        self._button4_proceed.config(relief=tk.SUNKEN, text="Processing")

        self.disableButtons(self._frame_coversetter)
        total = len(self._treeview1.get_children())
        # TBH I'd like to rework how this processing bar works. - Promidius
        progressBar = ProgressBar(self._initialized_UI, self._progressbar_frame, total)
        convert_images = self.checkbox2_settings_val.get()

        for item in self.covers_path_in_confirmation:
            for file in self.covers_path_in_confirmation[item]:
                logger.info(f"Starting processing for file: {item}")
                try:
                    SetCover(file, conver_to_webp=convert_images)
                    # label_progress_text.set(
                    #     f"Processed: {processed_counter}/{total} - {processed_errors} errors"
                    #     f" - Elapsed time: {get_elapsed_time}")
                    progressBar.increaseCount()
                except FileExistsError as e:
                    mb.showwarning(f"[ERROR] File already exists",
                                   f"Trying to create:\n`{e.filename2}` but already exists\n\nException:\n{e}")
                    progressBar.increaseError()
                    continue
                except PermissionError as e:
                    mb.showerror("Can't access the file because it's being used by a different process",
                                 f"Exception:{e}")
                    progressBar.increaseError()
                    continue
                except FileNotFoundError as e:
                    mb.showerror("Can't access the file because it's being used by a different process",
                                 f"Exception:{e}")
                    progressBar.increaseError()
                    continue
                except Exception as e:
                    mb.showerror("Something went wrong", "Error processing. Check logs.")
                    logger.critical("Exception Processing", e)
                    progressBar.increaseError()
                progressBar.updatePB()
        self.covers_path_in_confirmation = {}  # clear queue

        self.disableButtons(self.master)

        logger.debug("Clearing queue")

        try:
            logger.debug("Cleanup: Try to clear treeview")
            self._treeview1.delete(*self._treeview1.get_children())
            # self.treeview1.grid_forget()
        except AttributeError:
            logger.debug("Can't clear treeview. -> doesnt exist yet")
        except Exception as e:
            logger.debug("Can't clear treeview", exc_info=e)
        logger.debug("All done")

        self.enableButtons(self._frame_coversetter)
        self._button4_proceed.config(relief=tk.RAISED, text="Proceed")

    def clearqueue(self):
        self.covers_path_in_confirmation = {}  # clear queue
        try:
            logger.debug(" Try to clear treeview")
            self._treeview1.delete(*self._treeview1.get_children())
            # self.treeview1.grid_forget()
        except AttributeError:
            logger.debug("Can't clear treeview. -> doesnt exist yet")
        except Exception as e:
            logger.error("Can't clear treeview", exc_info=e)

        logger.info("Cleared queue")
        pass

    def recover(self):
        self.add_file_to_list(recover=True)

    def enableButtons(self, thisframe):
        for w in thisframe.winfo_children():
            if w.winfo_class() == "Button":
                w.configure(state="normal")
            if w.winfo_children():
                for w2 in w.winfo_children():
                    if w2.winfo_class() == "Button":
                        w2.configure(state="normal")
                    if w2.winfo_children():
                        for w3 in w2.winfo_children():
                            if w3.winfo_class() == "Button":
                                # logger.debug(w.winfo_class())
                                w3.configure(state="normal")

    def disableButtons(self, thisframe):
        for w in thisframe.winfo_children():
            if w.winfo_class() == "Button":
                w.configure(state="disabled")
            if w.winfo_children():
                for w2 in w.winfo_children():
                    if w2.winfo_class() == "Button":
                        w2.configure(state="disabled")
                    if w2.winfo_children():
                        for w3 in w2.winfo_children():
                            if w3.winfo_class() == "Button":
                                w3.configure(state="disabled")

    def _handle_click(self, event):
        if self._treeview1.identify_region(event.x, event.y) == "separator":
            return "break"
