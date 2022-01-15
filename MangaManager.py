import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from PIL import ImageTk, Image, UnidentifiedImageError
from itertools import cycle
from tkinter import ttk
import os
import zipfile
import tempfile
import re
import time
from datetime import datetime
from threading import Thread
from dataclasses import dataclass
import logging
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING)
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO)


def is_dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
parser.add_argument(
    '-p', '--path',
    type=is_dir_path,dest="active_dir_path")
args = parser.parse_args()

launch_path = args.active_dir_path
logging.basicConfig(level=args.loglevel,
                    format='%(asctime)s %(levelname)s %(message)s'
                    # filename='/tmp/myapp.log'
                    )
logging.getLogger('PIL').setLevel(logging.WARNING)
velog = logging.info
delog = logging.debug
ScriptDir = os.path.dirname(__file__)
undoJson = {}
undoJsonFile = f"{ScriptDir}/undo.json"
deleteCoverFilePath = f"{ScriptDir}/DELETE_COVER.jpg"
font_H0 = ("BOLD", 20)
font_H1 = ("BOLD", 18)
font_H2 = ("BOLD", 15)
font_H3 = ("BOLD", 12)

class CoverDoesNotExist(Exception):
    pass
class NoOverwriteSelected(Exception):
    pass
@dataclass
class cover_process_item_info:
    function: object
    zipFilePath: str
    coverFilePath: str
    coverFileName: str
    coverFileFormat: str

    def __init__(self, cbz_file, cover_path, cover_name, cover_format):
        # self.function = function
        self.zipFilePath = cbz_file
        self.coverFilePath = cover_path
        self.coverFileName = cover_name
        self.coverFileFormat = cover_format
@dataclass
class ChapterFileNameData:
    """Class to keep title data chapter and anything after chapter to join together after adding vol info Used in renaming"""
    name: str
    chapterinfo: str
    afterchapter: str
    fullpath: str
    volume = int
    complete_new_name:str

    def __init__(self, name: str, chapterinfo: str, afterchapter: str, fullpath: str,
                 volume: int = None, complete_new_name: str = None):
        self.name = name
        self.chapterinfo = chapterinfo
        self.afterchapter = afterchapter
        self.fullpath = fullpath
        self.volume = volume
        self.complete_new_name = complete_new_name


def backup_delete_first_cover(new_zipFilePath, tmpname,overwrite=None):
    backup_isdone = False
    def is_folder(name:str,folders_list):
        if name.split("/")[0] + "/" in folders_list:
            return True
        else:
            return False
    with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            # old_cover_filename = [v for v in zin.namelist() if v.startswith("OldCover_")]  # Find "OldCover_ file
            folders_list = [v for v in zin.namelist() if v.endswith("/")]  # Notes all folders to not process them.
            for item in zin.infolist():
                delog(f"Iterating: " + item.filename)
                if item.filename.startswith("OldCover_"):  # delete existing "OldCover_00.ext.bk file from the zip
                    continue

                if is_folder(item.filename, folders_list):  # We skip any file inside directory (for now)
                    continue

                if not backup_isdone:
                    # delog(f"File is cover/first and backup not done: {item.filename}")
                    # We save the current cover with different name to back it up
                    if item.filename.startswith("!00000."): # backup current first cover
                        newname = f"OldCover_{item.filename}.bak"
                        zout.writestr(newname, zin.read(item.filename))
                        backup_isdone = True
                        delog(f"Backed up customized first cover {item.filename}.")
                        break



            for item in zin.infolist():
                if item.filename.startswith("OldCover_") or item.filename.startswith("!00000."):  # delete existing "OldCover_00.ext.bk file from the zip
                    continue
                if is_folder(item.filename, folders_list):  # We skip any file inside directory (for now)
                    continue

                if not backup_isdone and overwrite == True:
                    newname = f"OldCover_{item.filename}.bak"
                    zout.writestr(newname, zin.read(item.filename))
                    backup_isdone = True
                    delog("Backed up first cover.")
                    continue
                else:
                    item_filename = item.filename
                    zout.writestr(item_filename, zin.read(item.filename))
                    delog(f"adding {item.filename} back to the new tempfile")
                    continue


def doDeleteCover(zipFilePath):

    oldZipFilePath = zipFilePath
    new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", zipFilePath)[0])
    delog(f"Inside doDeleteCover - .cbz will be renamed to {new_zipFilePath}")
    os.rename(zipFilePath, new_zipFilePath)

    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=True) # Overwrite true because we want to backup the cover with different name

    # checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)

    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)
    os.rename(new_zipFilePath, oldZipFilePath)


def updateZip(values: cover_process_item_info):
    velog("Updating file (overwriting 0001.ext)")
    v = values

    oldZipFilePath = v.zipFilePath
    new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", v.zipFilePath)[0])
    try:
        os.rename(v.zipFilePath, new_zipFilePath)
    except PermissionError as e:
        mb.showerror("Can't access the file because it's being used by a different process", f"Exception:{e}")
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(v.zipFilePath))
    os.close(tmpfd)
    backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=True)
    new_coverFileName = f"!00000{v.coverFileFormat}"

    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)
    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(v.coverFilePath, new_coverFileName)
    os.rename(new_zipFilePath, v.zipFilePath)
    velog("Finished processing of file")


def appendZip(values: cover_process_item_info):
    velog("Append file (append 0001.ext)")
    v = values
    new_zipFilePath = "{}.zip".format(re.findall(r'(?i)(.*)(?:\.[a-z]{3})$', v.zipFilePath)[0])
    try:
        os.rename(v.zipFilePath, new_zipFilePath)
    except PermissionError as e:
        mb.showerror("Can't access the file because it's being used by a different process", f"Exception:{e}")
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(new_zipFilePath))
    os.close(tmpfd)

    backup_delete_first_cover(new_zipFilePath, tmpname, overwrite=False)

    new_coverFileName = f"!00000{v.coverFileFormat}"
    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)
    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(v.coverFilePath, new_coverFileName)
    os.rename(new_zipFilePath, v.zipFilePath)
    velog("Finished processing of file")


def formatTimestamp(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%Y/%m/%d %H:%M:%S")


class SetVolumeCover(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing UI")
        self.title('Theme Demo')
        self.select_tool_old = None

        self.column_0_toolbox_frame = ttk.Frame(self)
        self.__tkvar = tk.StringVar(value='Select Tool')
        __toolSelectorValues = ["Cover Setter", "Volume Setter"]
        self.optionmenu1 = tk.OptionMenu(self.column_0_toolbox_frame, self.__tkvar, 'Select Tool', *__toolSelectorValues,
                                         command=self.select_tool)
        self.optionmenu1.grid(column='0', row='0', sticky='nw')
        self.column_0_toolbox_frame.configure(height='200', relief='raised', width='200')
        self.column_0_toolbox_frame.grid(column='0', row='1')
        self.column_0_toolbox_frame.grid(row=4)


        self.select_tool_old = "Cover Setter"
        self.tool_coversetter()
        # self.select_tool_old = "Volume Setter"
        # self.tool_volumesetter()

    def tool_coversetter(self):

        def set_do_overwrite_first_label():
            if self.do_overwrite_first.get():
                self.do_overwrite_first.set(False)
                self.do_overwrite_first_label_value.set("No")
            else:
                self.do_overwrite_first.set(True)
                self.do_overwrite_first_label_value.set("Yes")
            # self.do_overwrite_first_label_value.set(f"Replace: {self.do_overwrite_first}")
            print("debugp")

        def opencovers():
            """
            Open tki nter.askopenfilename all covers that are going to be placed inside each chapter and loads iter cycle
            """

            velog("Selecting covers in opencovers")
            self.button3_load_images.grid_remove()
            covers_path_list = filedialog.askopenfiles(initialdir=launch_path,
                                                       title="Open all covers you want to work with:"
                                                       )
            self.licycle = cycle(covers_path_list)
            try:
                self.nextelem = next(self.licycle)
            except StopIteration:
                mb.showwarning("No file selected","No images were selected.")
                self.image = None
                self.button3_load_images.grid()
                logging.critical("No images were selected when asked for")
                raise
            self.prevelem = None
            self.enableButtons(self.frame_coversetter)
            try:
                show_first_cover()

            except UnidentifiedImageError as e:
                mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
                logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}")
                self.button3_load_images.grid()


        def show_first_cover():
            velog("Printing first image in canvas")
            self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
            image = Image.open(self.thiselem.name)
            image = image.resize((300, 445), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(image)
            self.canvas_image = self.canvas1_coverimage.create_image(0, 0, anchor=tk.NW, image=self.image)
            self.cover_image_name_label_var.set(os.path.basename(self.thiselem.name))

        def reset_overwrite_status():
            # if self.do_overwrite_first_label_value.get() == "Selected: None":
            #     mb.showwarning(title="Select overwrite mode",
            #                    message="You need to choose to append the cover to the file or overwrite 0001.ext file")
            #     raise NoOverwriteSelected("No Overwrite mode Selected")
            self.do_overwrite_first.set(False)
            # self.do_overwrite_first_label_value.set(f"Replace: {self.do_overwrite_first}")
            self.do_overwrite_first_label_value.set("No")
            # self.overwrite_yes_button.config(relief=tk.RAISED)
            # self.overwrite_no_button.config(relief=tk.RAISED)

        def display_next_cover():
            velog(f"Printing next cover in canvas - {self.nextelem}")
            self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
            try:
                rawimage: Image = Image.open(self.thiselem.name)
            except UnidentifiedImageError as e:
                mb.showerror("File is not a valid image", f"The file {self.thiselem.name} is not a valid image file")
                logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}")
            image = rawimage.resize((300, 445), Image.ANTIALIAS)
            self.image = ImageTk.PhotoImage(image)
            # print(self.label.gettags("IMG10"))
            self.canvas1_coverimage.itemconfig(self.canvas_image, image=self.image)
            self.cover_image_name_label_var.set(os.path.basename(self.thiselem.name))

        def add_file_to_list(delete=False):
            velog("Adding files to processing list")
            if delete:
                overwriteval = "delete"
                image_path = deleteCoverFilePath
            else:
                overwriteval= self.do_overwrite_first.get()
                image_path = self.thiselem.name


            cbzs_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                filetypes=(("CBZ Files", "cbz"),)
                                )

            image = Image.open(image_path)
            image = image.resize((40, 60), Image.ANTIALIAS)
            self.image_in_confirmation = ImageTk.PhotoImage(image)

            self.covers_path_in_confirmation[str(self.image_in_confirmation)] = []
            for iterated_file_path in cbzs_path_list:
                iterated_file_path = iterated_file_path.name

                tmp_dic = dict(imagepath=image_path,
                               filepath=iterated_file_path,
                               overwrite=overwriteval,
                               image_not_garbage_collected=self.image_in_confirmation)

                self.covers_path_in_confirmation[str(self.image_in_confirmation)].append(tmp_dic)
                displayed_file_path = f"...{os.path.basename(iterated_file_path)[-46:]}"
                overwrite_displayedval = self.do_overwrite_first.get() if overwriteval != "delete" else "Delete"
                self.treeview1.insert(parent='', index='end', image=self.image_in_confirmation,
                                      values=(displayed_file_path, overwrite_displayedval))
                self.treeview1.yview_moveto(1)
                velog(f"Added {os.path.basename(iterated_file_path)} to the processing queue")
            reset_overwrite_status()
            self.button4_proceed.config(state="normal", text="Proceed")

        delog("inside tool-coversetter")
        self.title("Cover Setter")
        self.select_tool_old = "Cover Setter"
        self.covers_path_in_confirmation = {}



        self.frame_coversetter = ttk.Frame(self)
        self.frame_coversetter.rowconfigure(0, minsize=0, weight=1)
        self.frame_coversetter.rowconfigure(1)
        self.frame_coversetter.rowconfigure(2, pad=40)

        # First column from top to bottom:

        # Column 0 - Row 0
        # Join Canvas and image name together in same grid row
        self.canvas_frame = ttk.Frame(self.frame_coversetter)
        self.canvas_frame.grid(row=0, column=0)
        self.canvas1_coverimage = tk.Canvas(self.canvas_frame)
        self.canvas1_coverimage.configure(background='#878787', height=442, state='normal', width=296)
        self.canvas1_coverimage.grid(column=0, row=0, padx="10 30")
        self.button3_load_images = tk.Button(self.canvas_frame,text="Select covers",command=opencovers)
        self.button3_load_images.grid(column=0,row=0,pady=20)
        self.cover_image_name_label_var = tk.StringVar(value='OPEN ONE OR MORE IMAGES')
        self.label_coverimagetitle = ttk.Label(self.canvas_frame)
        self.label_coverimagetitle.configure(textvariable=self.cover_image_name_label_var)
        self.label_coverimagetitle.grid(column=0, row=1, sticky='n')

        self.button1_next = tk.Button(self.canvas_frame)
        self.button1_next.configure(cursor='arrow', default='disabled', justify='center', text='Next',width=20)
        self.button1_next.grid(column=0, row=2)
        # self.button1_next.grid_propagate(0)
        self.button1_next.configure(command=display_next_cover)

        # Column 0 Frame
        self.column_0_frame = tk.Frame(self.canvas_frame)
        # self.column_0_frame.columnconfigure(0, weight=1)
        # self.column_0_frame.columnconfigure(1, weight=1,pad=30)
        # self.column_0_frame.rowconfigure(2, pad=0)



        self.do_overwrite_first = tk.BooleanVar()
        self.do_overwrite_first.set(False)
        self.do_overwrite_first_label = tk.Label(self.column_0_frame,text="Replace current cover?")
        self.do_overwrite_first_label.grid(column=0, row=1, columnspan=2)
        self.do_overwrite_first_label_value = tk.StringVar()
        self.do_overwrite_first_label_value.set("No")
        self.overwrite_yes_button = tk.Button(self.column_0_frame, textvariable=self.do_overwrite_first_label_value, command=set_do_overwrite_first_label)
        self.overwrite_yes_button.grid(row=2, column=0, sticky=tk.W+tk.E,columnspan=2,pady="0 10")
        # self.overwrite_no_button = tk.Button(self.column_0_frame, text='NO', command=lambda: set_do_overwrite_first_label(False))
        # self.overwrite_no_button.grid(row=2, column=1, sticky=tk.E+tk.W)


        # self.do_overwrite_first_label = tk.Label(self.column_0_frame, textvariable=self.do_overwrite_first_label_value)
        # self.do_overwrite_first_label.grid(column=0, row=3, columnspan=2)


        #Todo
        # self.btn_undo = tk.Button(self.canvas_frame, text='UNDO', command=self.resetCover)
        # self.btn_undo.grid(row=4, sticky=tk.W + tk.E, columnspan=2)

        self.button2_openfile = tk.Button(self.column_0_frame)
        self.button2_openfile.configure(font='TkDefaultFont', justify='center', text='Open File to Apply this cover')
        self.button2_openfile.grid(column=0, row=4, columnspan=2, pady="15 0")
        self.button2_openfile.configure(command=add_file_to_list)

        separator = ttk.Separator(self.column_0_frame, orient="horizontal")
        separator.grid(column=0, row=5,sticky=tk.W+tk.E, pady="7 7",columnspan=2)
        # self.column_0_frame.grid_columnconfigure()
        self.button5_delete_covers = tk.Button(self.column_0_frame, text="Delete covers")
        self.button5_delete_covers.configure(command=lambda: add_file_to_list(True))
        self.button5_delete_covers.grid(column=0, row=6, sticky=tk.W+tk.E, columnspan=2)
        # self.column_0_frame.grid_columnconfigure()

        separator2 = ttk.Separator(self.column_0_frame, orient="horizontal")
        separator2.grid(column=0, row=7, sticky=tk.W + tk.E, pady="20 10", columnspan=2)
        # separator2 = ttk.Separator(self.column_0_frame, orient="horizontal")
        # separator2.grid(column=0, row=8, sticky=tk.W + tk.E, pady="1 7", columnspan=2)
        self.button6_reselect_covers = tk.Button(self.column_0_frame, text="Select new set of covers")
        self.button6_reselect_covers.configure(command=opencovers)
        self.button6_reselect_covers.grid(column=0, row=8, sticky=tk.W + tk.E, columnspan=2)
        self.column_0_frame.grid(row=3, pady=20)




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
        self.treeview1.grid(column=1, row=0,sticky=tk.N,pady="2 0")
        # Column 1 - Row 1
        self.button4_proceed = tk.Button(self.frame_coversetter)
        self.button4_proceed.configure(text='Proceed')
        self.button4_proceed.grid(column=1, row=1)
        self.button4_proceed.configure(command=self.process)

        # Column 1 - Row 2

        self.progressbar_frame = tk.Frame(self.frame_coversetter,width=60,height=90)
        self.progressbar_frame.grid(column=1, row=2, rowspan=2, sticky=tk.W+tk.E,padx=30)

        # End frame
        self.frame_coversetter.configure(height=420, padding='20', width='400')
        self.frame_coversetter.grid(column=0, row=0)

        # Process first cover
        # self.opencovers()
        # try:
        #     self.show_first_cover()
        # except UnidentifiedImageError as e:
        #     print(f"Errrrrrror {e}")
        #     logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}",e)
        self.disableButtons(self.frame_coversetter)
        self.button3_load_images.config(state="normal")
        self.button5_delete_covers.config(state="normal")

    def tool_volumesetter(self):
        delog("inside tool-volumesetter")
        self.geometry("500x886")
        self.resizable(0,0)
        MainLabelVar = tk.StringVar()
        self.title("Volume Setter")
        self.select_tool_old = "Volume Setter"
        self.frame_volumesetter = ttk.Frame(self)
        self.frame_volumesetter.configure(height=500, padding=20, width=886)
        self.frame_volumesetter.rowconfigure(0, minsize=0, weight=1)
        # self.frame_volumesetter.rowconfigure(1)
        # self.frame_volumesetter.rowconfigure(2, pad=40)

        self.instructionsLabel = tk.StringVar()
        self.subinstructionsLabel = tk.StringVar()

        MainLabelVar.set("Manga Manager\nProcessing done!")
        self.instructionsLabel.set(
            "This script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
        self.subinstructionsLabel.set("This naming convention must be followed for the script to work properly")

        self.label = tk.Label(self.frame_volumesetter, textvariable=self.instructionsLabel, font=font_H2)
        self.label.grid(row=0)
        self.sublabel = tk.Label(self.frame_volumesetter, textvariable=self.subinstructionsLabel, font=font_H3)
        self.sublabel.grid(row=1)
        #
        # self.btn_yes = tk.Button(self.frame_volumesetter, text='Continue' )
        # self.btn_yes.grid(row=2, sticky=tk.W + tk.E,pady="10 0")
        # self.btn_undo = tk.Button(self.frame_volumesetter, text='UNDO')
        # self.btn_undo.grid(row=3, sticky=tk.W + tk.E)
        # self.la
        label = tk.Label(self.frame_volumesetter, text="Select CBZ files")
        label.grid(row=2,pady="10 0")
        covers_path_list = None
        def open_files():
            delog("inside openfiles")
            print(covers_path_list)
            self.covers_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                                            filetypes=(("CBZ Files", "cbz"),)
                                                            )
            if not self.covers_path_list:
                # self.tool_volumesetter()
                label.configure(text=f"Selected 0 files.")
            else:
                label.configure(text=f"Selected {len(self.covers_path_list)} files")
            self.enableButtons(self.frame_volumesetter)


        self.button2_openfile = tk.Button(self.frame_volumesetter, text="Open", command=open_files)
        self.button2_openfile.grid(column=0, row=3, pady="0 20")


        def ValidateIfNum(s, S):
            # disallow anything but numbers
            valid = S == '' or S.isdigit()
            if not valid:
                self.frame_volumesetter.bell()
                velog("input not valid")
            return valid
        label = tk.Label(self.frame_volumesetter, text="Input volume number to apply to the selected files")
        label.grid(row=4, pady="5 0")
        vldt_ifnum_cmd = (self.frame_volumesetter.register(ValidateIfNum), '%s', '%S')
        self.input_volume_val = tk.IntVar()
        self.spinbox1 = tk.Spinbox(self.frame_volumesetter, from_=1, to=500, validate='all', validatecommand=vldt_ifnum_cmd)
        self.spinbox1.grid(column=0, row=5)

        def preview_changes():

            try:
                velog("Preview changes: Try to clear treeview")
                self.treeview2.delete(*self.treeview1.get_children())
            except AttributeError:
                delog("Can't clear treeview. -> doesnt exist yet")
            except Exception as e:
                delog("Can't clear treeview",exc_info=e)
            s = ttk.Style()
            s.configure('Treeview', rowheight=20, rowpady=5, rowwidth=365)
            s.layout("Treeview", [
                ('Treeview.treearea', {'sticky': 'nswe'})
            ])

            self.treeview2 = ttk.Treeview(self.frame_volumesetter, padding=5)
            self.treeview2.grid_propagate(True)
            self.treeview2['columns'] = ('old_name', 'to', 'new_name')

            self.treeview2.column("#0", width=0, stretch=False)
            self.treeview2.column("old_name", stretch=False, width=405, anchor=tk.W)
            self.treeview2.column("to", width=24, anchor=tk.CENTER, stretch=False)
            self.treeview2.column("new_name", stretch=False, width=405, anchor=tk.E)

            self.treeview2.heading("#0", text="", anchor=tk.W)
            self.treeview2.heading("old_name", text="OLD NAME", anchor=tk.CENTER)
            self.treeview2.heading("to", text="", anchor=tk.CENTER)
            self.treeview2.heading("new_name", text="NEW NAME", anchor=tk.CENTER)
            # self.treeview1.pack(expand=True, anchor="center", fill=tk.BOTH, padx=2, pady=5)
            self.treeview2.grid(column=0, row=7, pady="15 0")

            def handle_click(event):
                if self.treeview2.identify_region(event.x, event.y) == "separator":
                    return "break"

            self.treeview2.bind('<Button-1>', handle_click)
            self.list_filestorename = []
            counter = 0
            volume_to_apply  = self.spinbox1.get()
            for cbz_path in self.covers_path_list:
                filepath = cbz_path.name
                filename = os.path.basename(filepath)
                regexSearch = re.findall(r"(?i)(.*)((?:Chapter|CH)(?:\.|\s)[0-9]*[.][0-9])(\.[a-z]{3})", filename)
                if regexSearch:
                    r = regexSearch[0]
                    print(r)
                    file_regex_finds:ChapterFileNameData = ChapterFileNameData(name=r[0],chapterinfo=r[1],afterchapter=r[2],fullpath=filepath,volume=volume_to_apply)
                else:
                    #Todo: add warning no ch/chapter detected and using last int as ch identifier
                    regexSearch = re.findall(r"(?i)(.*\s)([0-9]+[.]*[0-9]*)(\.[a-z]{3}$)", filename)
                    if regexSearch:
                        r = regexSearch[0]
                        file_regex_finds:ChapterFileNameData = ChapterFileNameData(name=r[0],chapterinfo=r[1],afterchapter=r[2],fullpath=filepath,volume=volume_to_apply)

                newFile_Name = f"{file_regex_finds.name} Vol.{volume_to_apply} {file_regex_finds.chapterinfo}{file_regex_finds.afterchapter}"
                file_regex_finds.complete_new_name = newFile_Name


                self.list_filestorename.append(file_regex_finds)
                self.treeview2.insert(parent='', index='end', iid=counter, text='',
                             values=("..." + filename[-70:],
                                     " 🠆 ",
                                     "..." + newFile_Name[-70:]
                                     ))
                self.treeview2.yview_moveto(1)
                delog(f"Inserted item in treeview -> {file_regex_finds.name}")
                counter +=1
            self.covers_path_list = None
            self.button4_proceed = tk.Button(self.frame_volumesetter,text="Proceed",command=self.process)
            self.button4_proceed.grid(column=0, row=8, pady=7)

        preview_button = tk.Button(self.frame_volumesetter, text="Preview", command=preview_changes)
        preview_button.grid(column=0, row=6)


        self.progressbar_frame = tk.Frame(self.frame_volumesetter, width=60, height=90)
        self.progressbar_frame.columnconfigure(0,weight=1)
        self.progressbar_frame.columnconfigure(1,weight=1)
        self.progressbar_frame.grid(column=0, row=9, sticky="WE", padx=30)

        self.disableButtons(self.frame_volumesetter)
        self.button2_openfile.config(state="normal")

        self.frame_volumesetter.grid(row=0)

    def select_tool(self, selection):
        delog(f"Changing tool. Selected -> {selection} --|-- Old selection -> {self.select_tool_old}")
        if selection == "Cover Setter" and not self.select_tool_old == "Cover Setter":
            if self.select_tool_old is not None or self.select_tool_old == "Volume Setter":
                self.frame_volumesetter.destroy()
            self.tool_coversetter()
        elif selection == "Volume Setter" and not self.select_tool_old == "Volume Setter":
            if self.select_tool_old is not None or self.select_tool_old == "Cover Setter":
                self.frame_coversetter.destroy()
            self.tool_volumesetter()


    def process(self):
        velog("Starting processing of files.")
        self.button4_proceed.config(relief=tk.SUNKEN, text="Processing")


        class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
            def __init__(self_waitup):
                Thread.__init__(self_waitup)  # Override the __init__
                self_waitup.i_waited_for_this = ""

            def run(self_waitup):

                processed_counter = 1
                processed_errors = 0
                if self.select_tool_old == "Cover Setter":
                    timestamp = time.time()
                    undoJson["SetCover"] = {}
                    undoJson2 = undoJson["SetCover"][timestamp] = []

                    total = 0
                    for v in self.covers_path_in_confirmation:
                        total +=len(v)
                    undoJson2 = {}
                    for item in self.covers_path_in_confirmation:
                        # pathdict = self.covers_path_in_confirmation
                        undoJson2[item] = []
                        for file in self.covers_path_in_confirmation[item]:

                            delog(f"processing: {file}")
                            cover_path = file["imagepath"]
                            cbz_file = file["filepath"]
                            overwrite = file["overwrite"]
                            cover_name = os.path.basename(cover_path)
                            cover_format = re.findall(r"(?i)\.[a-z]{3}$", cover_path)[0]
                            velog(f"Starting processing for file: {cover_name}")
                            try:
                                if overwrite == "delete":
                                    delog("Entering delete cover function")
                                    doDeleteCover(cbz_file)
                                elif overwrite == True:
                                    delog("Entering overwrite cover function")
                                    data = cover_process_item_info(cbz_file, cover_path, cover_name, cover_format)
                                    updateZip(data)
                                else:
                                    delog("Entering append cover function")
                                    data = cover_process_item_info(cbz_file, cover_path, cover_name, cover_format)
                                    appendZip(data)

                                global label_progress_text
                                label_progress_text.set(f"Processed: {processed_counter}/{total} - {processed_errors} errors")
                                processed_counter +=1

                            except FileExistsError as e:
                                mb.showwarning(f"[ERROR] File already exists",
                                               f"Trying to create:\n`{e.filename2}` but already exists\n\nException:\n{e}")
                                processed_errors += 1
                                continue
                            except PermissionError as e:
                                mb.showerror("Can't access the file because it's being used by a different process", f"Exception:{e}")
                                processed_errors += 1
                                continue
                            except FileNotFoundError as e:
                                mb.showerror("Can't access the file because it's being used by a different process",
                                             f"Exception:{e}")
                                processed_errors += 1
                                continue
                            except Exception as e:
                                mb.showerror("Something went wrong","Error processing. Check logs.")
                                logging.critical("Exception Processing",exc_info=e,)
                            undoJson2[item].append(file)
                    with open(undoJsonFile, "w") as f:
                        print(undoJson)
                        json.dump(undoJson, f)


                elif self.select_tool_old =="Volume Setter":
                    timestamp = time.time()
                    undoJson["Rename"] = {}
                    undoJson["Rename"][timestamp] = []
                    # print("date and time:",date_time)
                    for item in self.list_filestorename:

                        velog(f"Renaming {item.name}")
                        newFile_Name = item.complete_new_name
                        oldPath = item.fullpath
                        newPath = f"{os.path.dirname(item.fullpath)}\{newFile_Name}"
                        # print("####\n")
                        undoJson["Rename"][timestamp].append({"oldPath": oldPath, "newPath": newPath})
                        try:
                            os.rename(oldPath, newPath)
                        except PermissionError as e:
                            mb.showerror("Can't access the file because it's being used by a different process",
                                         f"Exception:{e}")
                        velog(f"Renamed {item.name}")

                else:
                    delog("Error No tool selected")
                # self.function(self.function_args)


            #     with open(undoJsonFile, "w") as f:
            #         json.dump(undoJson, f)
            #     print(undoJson)
            #
                self.covers_path_in_confirmation = {}  # clear queue
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
                self_progress.pb = ttk.Progressbar(self_progress.pb_root, length=400, mode="indeterminate")  # create progress bar

                # global label_progress_text
                self_progress.pb_text = tk.Label(self_progress.pb_root, textvariable=self_progress.label_progress_text, anchor=tk.W)
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
        if self.select_tool_old =="Cover Setter":
            Selected_tool = "Cover"
            FrameToProcess: tk.Frame = self.frame_coversetter
        elif self.select_tool_old == "Volume Setter":
            Selected_tool = "Volume"
            FrameToProcess: tk.Frame = self.frame_volumesetter

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
            if Selected_tool == "Cover":
                self.treeview1.delete(*self.treeview1.get_children())
                # self.treeview1.grid_forget()
            elif Selected_tool == "Volume":
                self.treeview2.delete(*self.treeview2.get_children())
                self.treeview2.grid_forget()
        except AttributeError:
            delog("Can't clear treeview. -> doesnt exist yet")
        except Exception as e:
            delog("Can't clear treeview", exc_info=e)
        velog("All done")

        self.enableButtons(FrameToProcess)
        self.button4_proceed.config(relief=tk.RAISED, text="Proceed")

    def enableButtons(self,thisframe):
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
                                # print(w.winfo_class())
                                w3.configure(state="normal")
    def disableButtons(self,thisframe):
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
    def askopen_cbz(self):
        self.cbzs_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                filetypes=(("CBZ Files", "cbz"),)
                                )

if __name__ == "__main__":

    app = SetVolumeCover()
    app.mainloop()

