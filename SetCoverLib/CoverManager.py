import tkinter
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from PIL import ImageTk, Image, UnidentifiedImageError
from itertools import cycle
from tkinter import ttk
import os
import sys

import SetCoverLib.models
from models import cover_process_item_info
import zipfile
import tempfile
import re
import time
from datetime import datetime
from threading import Thread
from dataclasses import dataclass
import logging
from SetCoverLib.models import *
from SetCoverLib.cbz_handler import SetCover


launch_path =""
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)]
                    # filename='/tmp/myapp.log'
                    )

velog = logging.info
delog = logging.debug
logging.getLogger('PIL').setLevel(logging.WARNING)
ScriptDir = os.path.dirname(__file__)


# Todo: delete
undoJson = {}
undoJsonFile = f"{ScriptDir}/undo.json"

font_H0 = ("BOLD", 20)
font_H1 = ("BOLD", 18)
font_H2 = ("BOLD", 15)
font_H3 = ("BOLD", 12)


class CoverManagerApp:
    def __init__(self,master:tkinter.Tk):
        self.deleteCoverFilePath = f"{ScriptDir}/DELETE_COVER.jpg"
        self.master = master


        self.do_overwrite_first = tk.BooleanVar()
        self.checkbox0_settings_val = tk.BooleanVar()
        self.checkbox1_settings_val = tk.BooleanVar()
        self.covers_path_in_confirmation = {}

    def start_ui(self):


        # build ui
        delog("inside tool-coversetter")

        self.master.title("Cover Setter")
        self.master.geometry("860x940")

        self.frame_coversetter = ttk.Frame(self.master)
        self.frame_coversetter.rowconfigure(0, minsize=0, weight=1)
        self.frame_coversetter.rowconfigure(1)
        self.frame_coversetter.rowconfigure(2, pad=40)

        self.canvas_frame = ttk.Frame(self.frame_coversetter)
        self.canvas_frame.grid(row=0, column=0)

        self.canvas1_coverimage = tk.Canvas(self.canvas_frame)
        self.canvas1_coverimage.configure(background='#878787', height=442, state='normal', width=296)
        self.canvas1_coverimage.grid(column=0, row=0, padx="10 30")
        self.button3_load_images = tk.Button(self.canvas_frame, text="Select covers", command=self.opencovers)
        self.button3_load_images.grid(column=0, row=0, pady=20)

        self.label_coverimagetitle = ttk.Label(self.canvas_frame)
        self.label_coverimagetitle.configure(text='OPEN ONE OR MORE IMAGES')
        self.label_coverimagetitle.grid(column=0, row=1, sticky='n')


        self.button1_next = tk.Button(self.canvas_frame)
        self.button1_next.configure(cursor='arrow', default='disabled', justify='center', text='Next', width=20)
        self.button1_next.grid(column=0, row=2)
        # self.button1_next.grid_propagate(0)
        self.button1_next.configure(command=self.display_next_cover)

        # Column 0 Frame
        self.column_0_frame = tk.Frame(self.canvas_frame)

        self.do_overwrite_first.set(False)
        self.do_overwrite_first_label = tk.Label(self.column_0_frame, text="Replace current cover?")
        self.do_overwrite_first_label.grid(column=0, row=1, columnspan=2)
        self.overwrite_yes_button = tk.Button(self.column_0_frame, text="No",
                                              command=self.set_do_overwrite_first_label)
        self.overwrite_yes_button.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=2, pady="0 10")


        self.button2_openfile = tk.Button(self.column_0_frame)
        self.button2_openfile.configure(font='TkDefaultFont', justify='center', text='Open File to Apply this cover')
        self.button2_openfile.grid(column=0, row=4, columnspan=2, pady="15 0")
        self.button2_openfile.configure(command=self.add_file_to_list)


        separator = ttk.Separator(self.column_0_frame, orient="horizontal")
        separator.grid(column=0, row=5, sticky=tk.W + tk.E, pady="7 7", columnspan=2)
        self.button5_delete_covers = tk.Button(self.column_0_frame, text="Delete covers")
        self.button5_delete_covers.configure(command=lambda: self.add_file_to_list(True))
        self.button5_delete_covers.grid(column=0, row=6, sticky=tk.W + tk.E, columnspan=2)

        separator2 = ttk.Separator(self.column_0_frame, orient="horizontal")
        separator2.grid(column=0, row=7, sticky=tk.W + tk.E, pady="20 10", columnspan=2)
        self.button6_reselect_covers = tk.Button(self.column_0_frame, text="Select new set of covers")
        self.button6_reselect_covers.configure(command=self.opencovers)
        self.button6_reselect_covers.grid(column=0, row=8, sticky=tk.W + tk.E, columnspan=2)
        self.column_0_frame.grid(row=3, pady=20)

        settings = tk.Frame(self.frame_coversetter, height=160, width=200)
        settings.grid(row=4, column=0, sticky=tk.E)

        self.checkbox0_settings_val.set(True)
        checkbox0_settings = tk.Checkbutton(settings, text="Display next cover after adding a file to the queue (not delete)",
                                            variable=self.checkbox0_settings_val)
        checkbox0_settings.grid(row=0, sticky=tk.W)

        checkbox1_settings = tk.Checkbutton(settings,text="Open File selector dialog after adding to queue (default replace: no)",variable=self.checkbox1_settings_val)
        checkbox1_settings.grid(row=1, sticky=tk.W)


        # This is the 2d column of Frame
        # Column 1 - Row 0
        s = ttk.Style()
        s.configure('Treeview', rowheight=65, rowpady=5, rowwidth=360)
        self.treeview1 = ttk.Treeview(self.frame_coversetter)
        self.treeview1_cols = ['column3', 'overwrite']
        self.treeview1_dcols = ['column3', 'overwrite']
        self.treeview1.configure(columns=self.treeview1_cols, displaycolumns=self.treeview1_dcols)
        self.treeview1.column('#0', anchor='center', stretch=False, width=65)
        self.treeview1.column('column3', anchor='w', stretch=True, width=300, minwidth=260)
        self.treeview1.column('overwrite', anchor='center', stretch=True, width=60)

        self.treeview1.heading('column3', anchor='center', text='Queue')
        self.treeview1.heading('overwrite', anchor='center', text='Overwrite')
        self.treeview1.grid(column=1, row=0, sticky=tk.N, pady="2 0")
        # Column 1 - Row 1
        self.button4_proceed = tk.Button(self.frame_coversetter)
        self.button4_proceed.configure(text='Proceed')
        self.button4_proceed.grid(column=1, row=1)
        self.button4_proceed.configure(command=self.process)


        # Column 1 - Row 2

        self.progressbar_frame = tk.Frame(self.frame_coversetter,width=60,height=60)
        self.progressbar_frame.grid(column=1, row=2, rowspan=2, sticky=tk.W+tk.E,padx=30)

        # End frame
        self.frame_coversetter.configure(height=420, padding='20', width='400')
        self.frame_coversetter.grid(column=0, row=0)

        self.disableButtons(self.frame_coversetter)
        self.button3_load_images.config(state="normal")
        self.button5_delete_covers.config(state="normal")

        # Main widget

    def run(self):
        self.master.mainloop()

    #UI Controller

    def set_do_overwrite_first_label(self):
        if self.do_overwrite_first.get():
            self.do_overwrite_first.set(False)
            self.overwrite_yes_button.configure(text="No")
        else:
            self.do_overwrite_first.set(True)
            self.overwrite_yes_button.configure(text="Yes")

    # Works
    def opencovers(self):
        """
        Open tki nter.askopenfilename all covers that are going to be placed inside each chapter and loads iter cycle
        """

        def show_first_cover(cls):
            velog("Printing first image in canvas")
            cls.thiselem, cls.nextelem = cls.nextelem, next(cls.licycle)
            image = Image.open(cls.thiselem.name)
            image = image.resize((300, 445), Image.ANTIALIAS)
            cls.image = ImageTk.PhotoImage(image)
            cls.canvas_image = cls.canvas1_coverimage.create_image(0, 0, anchor=tk.NW, image=cls.image)
            cls.label_coverimagetitle.configure(text=os.path.basename(cls.thiselem.name))
        velog("Selecting covers in opencovers")

        self.button3_load_images.configure(text="Loading...", state="disabled")
        covers_path_list = filedialog.askopenfiles(initialdir=launch_path,
                                                   title="Open all covers you want to work with:"
                                                   )
        self.licycle = cycle(covers_path_list)
        try:
            self.nextelem = next(self.licycle)
        except StopIteration:
            # self.button3_load_images.configure(text="Select covers")
            mb.showwarning("No file selected", "No images were selected.")
            self.image = None
            self.button3_load_images.configure(text="Select covers", state="normal")
            self.button3_load_images.grid()
            logging.error("No images were selected when asked for")
            raise
        self.prevelem = None
        self.enableButtons(self.frame_coversetter)
        try:
            self.button3_load_images.grid_remove()

            show_first_cover(self)

        except UnidentifiedImageError as e:
            mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
            logging.error(f"UnidentifiedImageError - Image file: {self.thiselem.name}")
            self.button3_load_images.configure(text="Select covers", state="normal")
            self.button3_load_images.grid()

    # Works
    def display_next_cover(self):
        velog(f"Printing next cover in canvas - {self.nextelem}")
        self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        try:
            rawimage: Image = Image.open(self.thiselem.name)
        except UnidentifiedImageError as e:
            mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
            logging.error(f"UnidentifiedImageError - Image file: {self.thiselem.name}")
        image = rawimage.resize((300, 445), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(image)
        # delog(self.label.gettags("IMG10"))
        self.canvas1_coverimage.itemconfig(self.canvas_image, image=self.image)
        self.label_coverimagetitle.configure(text=os.path.basename(self.thiselem.name))

    def add_file_to_list(self, delete=False):
        velog("Adding files to processing list")
        option_delete = False
        option_overwrite = False
        if delete:
            option_delete = True
            image_path = self.deleteCoverFilePath
        else:
            option_overwrite = self.do_overwrite_first.get()
            image_path = self.thiselem.name

        cbzs_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                                 filetypes=(("CBZ Files", "cbz"),)
                                                 )

        image = Image.open(image_path)
        image = image.resize((40, 60), Image.ANTIALIAS)
        self.image_in_confirmation = ImageTk.PhotoImage(image)
        if not self.covers_path_in_confirmation.get(str(self.image_in_confirmation)):
            self.covers_path_in_confirmation[str(self.image_in_confirmation)] = list[cover_process_item_info]()

        for iterated_file_path in cbzs_path_list:
            iterated_file_path = iterated_file_path.name
            tmp_info = cover_process_item_info(
                cbz_file=iterated_file_path,
                cover_path=image_path,
                cover_name=os.path.basename(image_path),
                cover_format=image_path[-3:],
                coverDelete=option_delete,
                coverOverwrite=option_overwrite
            )
            tmp_info.imageObject = self.image_in_confirmation


            self.covers_path_in_confirmation[str(self.image_in_confirmation)].append(tmp_info)
            velog(f"Added {os.path.basename(iterated_file_path)} to the processing queue")

            # Adding file is done. Just adding visual feedback in UI
            displayed_file_path = f"...{os.path.basename(iterated_file_path)[-46:]}"
            overwrite_displayedval = self.do_overwrite_first.get() if not delete else "Delete"
            self.treeview1.insert(parent='', index='end', image=self.image_in_confirmation,
                                  values=(displayed_file_path, overwrite_displayedval))
            self.treeview1.yview_moveto(1)


        self.do_overwrite_first.set(False)
        self.overwrite_yes_button.configure(text="No")

        self.button4_proceed.config(state="normal", text="Proceed")
        if not delete:
            if self.checkbox0_settings_val.get():
                self.display_next_cover()
            if self.checkbox1_settings_val.get() and cbzs_path_list:
                self.add_file_to_list()

    def process(self):
        velog("Starting processing of files.")
        self.button4_proceed.config(relief=tk.SUNKEN, text="Processing")

        class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
            def __init__(self_waitup):
                Thread.__init__(self_waitup)  # Override the __init__
                self_waitup.i_waited_for_this = ""

            def run(self_waitup):
                undoJsonFile_modify = undoJsonFile
                # with open(undoJsonFile, "w") as f:
                #     json.dump(self.undo_task_json, f)
                processed_counter = 1
                processed_errors = 0
                timestamp = time.time()
                total = len(self.treeview1.get_children())
                # for v in self.covers_path_in_confirmation:
                #     total +=len(v)
                for item in self.covers_path_in_confirmation:
                    # pathdict = self.covers_path_in_confirmation
                    for file in self.covers_path_in_confirmation[item]:
                        velog(f"Starting processing for file: {item}")
                        try:
                            SetCover(file)
                        #     if overwrite == "delete":
                        #         delog("Entering delete cover function")
                        #         cbz_han(cbz_file)
                        #     elif overwrite == True:
                        #         delog("Entering overwrite cover function")
                        #         data = cover_process_item_info(cbz_file, cover_path, cover_name, cover_format)
                        #         doUpdateZip(data)
                        #     else:
                        #         delog("Entering append cover function")
                        #         data = cover_process_item_info(cbz_file, cover_path, cover_name, cover_format)
                        #         doAppendZip(data)

                            global label_progress_text
                            label_progress_text.set(
                                f"Processed: {processed_counter}/{total} - {processed_errors} errors")
                            processed_counter += 1

                        except FileExistsError as e:
                            mb.showwarning(f"[ERROR] File already exists",
                                           f"Trying to create:\n`{e.filename2}` but already exists\n\nException:\n{e}")
                            processed_errors += 1
                            continue
                        except PermissionError as e:
                            mb.showerror("Can't access the file because it's being used by a different process",
                                         f"Exception:{e}")
                            processed_errors += 1
                            continue
                        except FileNotFoundError as e:
                            mb.showerror("Can't access the file because it's being used by a different process",
                                         f"Exception:{e}")
                            processed_errors += 1
                            continue
                        except Exception as e:
                            mb.showerror("Something went wrong", "Error processing. Check logs.")
                            logging.critical("Exception Processing", e)

                delog("Just before exiting progress_bar loop")
                self.covers_path_in_confirmation = {}  # clear queue
                self.undo_task_json = {}
                global pb_flag
                pb_flag = False
                self_waitup.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass

        class ProgressBarIn:
            def __init__(self_progress, title="", label="", text=""):
                self_progress.title = title  # Build the progress bar
                self_progress.text = text
                global label_progress_text
                label_progress_text = tk.StringVar()
                self_progress.label_progress_text = label_progress_text

            def startup(self_progress):
                self_progress.pb_root = self.progressbar_frame  # create a window for the progress bar
                # self_progress.pb_root.configure(padx=30)
                # self_progress.pb_label = tk.Label(self_progress.pb_root, textvariable=self_progress.label)  # make label for progress bar
                self_progress.pb = ttk.Progressbar(self_progress.pb_root, length=400,
                                                   mode="indeterminate")  # create progress bar

                # global label_progress_text
                self_progress.pb_text = tk.Label(self_progress.pb_root, textvariable=self_progress.label_progress_text,
                                                 anchor=tk.W)
                self_progress.pb.start()
                velog("Started progress bar")

                # self_progress.pb_label.grid(row=0, column=0, sticky=tk.W)
                self_progress.pb.grid(row=0, column=0, sticky=tk.E)
                self_progress.pb_text.grid(row=1, column=0, sticky=tk.E)
                while pb_flag == True:  # move the progress bar until multithread reaches line 19
                    self_progress.pb_root.update()
                    self_progress.pb['value'] += 1
                    time.sleep(.1)

            def stop(self_progress):
                # self_progress.label_progress_text.set("Done")
                self_progress.pb.stop()  # stop and destroy the progress bar
                self_progress.pb.config(mode="determinate")
                self_progress.pb.step(99.99)
                # self.pb_root.destroy()
                self_progress.pb.grid_forget()
                self_progress.pb_text.grid_forget()

                velog("File processed")

                # for widget in self_progress.pb_root.winfo_children():
                #     widget.destroy()
                return

        global pb_flag
        pb_flag = True
        global t1
        global t2
        FrameToProcess: tk.Frame = self.frame_coversetter

        self.disableButtons(FrameToProcess)
        t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
        t2 = WaitUp()
        t2.start()  # use start() instead of run() for threading module
        t1.startup()  # start the progress bar
        t2.join()  # wait for WaitUp to finish before proceeding
        t1.stop()  # destroy the progress bar object
        velog("Clearing queue")

        try:
            velog("Cleanup: Try to clear treeview")
            self.treeview1.delete(*self.treeview1.get_children())
            # self.treeview1.grid_forget()
        except AttributeError:
            delog("Can't clear treeview. -> doesnt exist yet")
        except Exception as e:
            delog("Can't clear treeview", exc_info=e)
        velog("All done")

        self.enableButtons(FrameToProcess)
        self.button4_proceed.config(relief=tk.RAISED, text="Proceed")
        # TODO: Add clear queue button

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
                                # delog(w.winfo_class())
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


if __name__ == "__main__":
    root = tk.Tk()
    app = CoverManagerApp(root)
    app.start_ui()
    app.run()

