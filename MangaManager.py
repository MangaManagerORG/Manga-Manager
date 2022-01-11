import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
from PIL import ImageTk, Image, UnidentifiedImageError
from itertools import cycle
from tkinter import ttk
import os
import zipfile
import tempfile
import sys
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
velog = logging.info
ScriptDir = os.path.dirname(__file__)
undoJson = {}
undoJsonFile = f"{ScriptDir}/undo.json"


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



def checkCoverExists(new_zipFilePath, tmpname, coverFileName, CoverFileFormat, mode):
    with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                print(item.filename, coverFileName)
                if item.filename != coverFileName:
                    if item.filename.startswith("OldCover"):
                        # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))
                        continue
                    if re.findall(r"0+1\.[a-z]{3}$", item.filename) and mode:
                        zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                        continue
                    if re.findall(r"0+0\.[a-z]{3}$", item.filename) and not mode:
                        zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                        continue
                    zout.writestr(item, zin.read(item.filename))
                else:
                    zout.writestr(f"OldCover{item.filename}.bak", zin.read(item.filename))


def resetCover(new_zipFilePath, tmpname, mode):
    with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            onholdCover = ""
            rawCovername = ""
            rawholdCover = ""
            coverIsZero = False
            oldCoverExists = False
            for item in zin.infolist():
                if item.filename.startswith("OldCover"):
                    print("found oldCover")
                    onholdCover = item.filename.replace("OldCover", "").replace(".bak", "")
                    if re.findall(r"0+0\.[a-z]{3}$", item.filename):
                        coverIsZero = True
                        rawCovername = item
                    elif re.findall(r"0+1\.[a-z]{3}$", item.filename):
                        coverIsZero = False
                        rawCovername = item
                    elif onholdCover.startswith("."):
                        rawCovername = item
                        rawholdCover = onholdCover
                        onholdCover = f"0000{onholdCover}"
                        coverIsZero = "None"
                    # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))
                    oldCoverExists = True
                    break
            if not oldCoverExists:
                raise CoverDoesNotExist("Old Cover not found")
            if coverIsZero == "None":
                for item in zin.infolist():
                    # time.sleep(2)
                    if item.filename.startswith(
                            "OldCover"):  # and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                        continue
                    if re.findall(r"0+0\.[a-z]{3}$", item.filename):
                        # zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                        # zout.writestr(onholdCover, zin.read(rawCovername.filename))
                        coverIsZero = True
                        continue
            for item in zin.infolist():
                # time.sleep(2)
                if re.findall(r"0+0\.[a-z]{3}$", item.filename) and coverIsZero:
                    zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                    zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    coverIsZero = True
                if item.filename.startswith(
                        "OldCover"):  # and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                    continue
                if re.findall(r"0+1\.[a-z]{3}$", item.filename):
                    if onholdCover:
                        onholdCover = f"0001{rawholdCover}"
                    zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                    zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    continue
                else:
                    zout.writestr(item, zin.read(item.filename))
                    # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))


def deleteCover(new_zipFilePath, tmpname):
    with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            onholdCover = ""
            rawCovername = ""
            rawholdCover = ""
            coverIsZero = False
            oldCoverExists = False
            for item in zin.infolist():
                if item.filename.startswith("OldCover"):
                    print("found oldCover")
                    onholdCover = item.filename.replace("OldCover", "").replace(".bak", "")
                    if re.findall(r"0+0\.[a-z]{3}$", item.filename):
                        coverIsZero = True
                        rawCovername = item
                    elif re.findall(r"0+1\.[a-z]{3}$", item.filename):
                        coverIsZero = False
                        rawCovername = item
                    elif onholdCover.startswith("."):
                        rawCovername = item
                        rawholdCover = onholdCover
                        onholdCover = f"0000{onholdCover}"
                        coverIsZero = "None"
                    # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))
                    oldCoverExists = True
                    break
            if coverIsZero == "None":
                for item in zin.infolist():
                    # time.sleep(2)
                    if item.filename.startswith(
                            "OldCover"):  # and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                        continue
                    if re.findall(r"0+0\.[a-z]{3}$", item.filename):
                        # zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                        # zout.writestr(onholdCover, zin.read(rawCovername.filename))
                        coverIsZero = True
                        continue
            for item in zin.infolist():
                # time.sleep(2)
                if re.findall(r"0+0\.[a-z]{3}$", item.filename) and coverIsZero:
                    zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                    # zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    continue

                if re.findall(r"0+1\.[a-z]{3}$", item.filename):
                    zout.writestr(f"OldCover_{item.filename}.bak", zin.read(item.filename))
                    # zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    continue

                if item.filename.startswith(
                        "OldCover"):  # and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                    continue
                else:
                    zout.writestr(item, zin.read(item.filename))
                    # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))


def doResetCover(zipFilePath):
    oldZipFilePath = zipFilePath
    new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", zipFilePath)[0])

    os.rename(zipFilePath, new_zipFilePath)

    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    resetCover(new_zipFilePath, tmpname, True)

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
        mb.showerror("Can't access the file becuase it's being used by a different process", f"Exception:{e}")
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(v.zipFilePath))
    os.close(tmpfd)
    new_coverFileName = f"0001{v.coverFileFormat}"
    checkCoverExists(new_zipFilePath, tmpname, new_coverFileName, v.coverFileFormat, True)

    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)

    basenameFile = os.path.basename(v.coverFilePath)
    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(v.coverFilePath, new_coverFileName)
    os.rename(new_zipFilePath, oldZipFilePath)
    velog("Finished processign of file")


def appendZip(values: cover_process_item_info):
    velog("Append file (append 0001.ext)")
    v = values
    new_zipFilePath = "{}.zip".format(re.findall(r'(?i)(.*)(?:\.[a-z]{3})$', v.zipFilePath)[0])
    try:
        os.rename(v.zipFilePath, new_zipFilePath)
    except PermissionError as e:
        mb.showerror("Can't access the file becuase it's being used by a different process", f"Exception:{e}")

    oldZipFilePath = v.zipFilePath

    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(new_zipFilePath))
    os.close(tmpfd)

    new_coverFileName = f"0000{v.coverFileFormat}"

    checkCoverExists(new_zipFilePath, tmpname, new_coverFileName, v.coverFileFormat, False)

    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)

    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(v.coverFilePath, new_coverFileName)
    os.rename(new_zipFilePath, oldZipFilePath)
    velog("Finished processign of file")


def doDeleteCover(zipFilePath):
    oldZipFilePath = zipFilePath
    new_zipFilePath = '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$", zipFilePath)[0])

    os.rename(zipFilePath, new_zipFilePath)

    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    deleteCover(new_zipFilePath, tmpname)

    # checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)

    os.remove(new_zipFilePath)
    os.rename(tmpname, new_zipFilePath)
    os.rename(new_zipFilePath, oldZipFilePath)


def formatTimestamp(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%Y/%m/%d %H:%M:%S")


class SetVolumeCover(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.debug("Initializing UI")
        self.title('Theme Demo')
        self.covers_path_in_confirmation = {}
        self.covers_path_list = None
        s = ttk.Style()
        s.configure('Treeview', rowheight=65, rowpady=5, rowwidth=360)

        self.frame1 = ttk.Frame(self)
        self.frame1.rowconfigure(0, minsize=0, weight=1)
        self.frame1.rowconfigure(1)
        self.frame1.rowconfigure(2, pad=40)

        # First column from top to bottom:

        # Column 0 - Row 0
        # Join Canvas and image name together in same grid row
        self.canvas_frame = ttk.Frame(self.frame1)
        self.canvas_frame.grid(row=0, column=0)
        self.canvas1_coverimage = tk.Canvas(self.canvas_frame)
        self.canvas1_coverimage.configure(background='red', height=442, state='normal', width=296)
        self.canvas1_coverimage.grid(column=0, row=0, padx="10 30")
        self.button3_load_images = tk.Button(self.canvas_frame,text="Select covers",command=self.opencovers)
        self.button3_load_images.grid(column=0,row=0,pady=20)
        self.cover_image_name_label_var = tk.StringVar(value='OPEN ONE OR MORE IMAGES')
        self.label1_coverimagetitle = ttk.Label(self.canvas_frame)
        self.label1_coverimagetitle.configure(textvariable=self.cover_image_name_label_var)
        self.label1_coverimagetitle.grid(column=0, row=1, sticky='n')

        self.button1_next = tk.Button(self.canvas_frame)
        self.button1_next.configure(cursor='arrow', default='disabled', justify='center', text='Next',width=20)
        self.button1_next.grid(column=0, row=2)
        # self.button1_next.grid_propagate(0)
        self.button1_next.configure(command=self.display_next_cover)

        # Column 0 Frame
        self.column_0_frame = tk.Frame(self.canvas_frame)
        # self.column_0_frame.columnconfigure(0, weight=1)
        # self.column_0_frame.columnconfigure(1, weight=1,pad=30)
        # self.column_0_frame.rowconfigure(2, pad=0)


        self.do_overwrite_first = tk.BooleanVar()
        self.do_overwrite_first_label = tk.Label(self.column_0_frame,text="Overwrite 0001.ext or create 0000.ext file?")
        self.do_overwrite_first_label.grid(column=0, row=1, columnspan=2)
        self.overwrite_yes_button = tk.Button(self.column_0_frame, text='YES', command=lambda: self.set_do_overwrite_first_label(True))
        self.overwrite_yes_button.grid(row=2, column=0, sticky=tk.W+tk.E)
        self.overwrite_no_button = tk.Button(self.column_0_frame, text='NO', command=lambda: self.set_do_overwrite_first_label(False))
        self.overwrite_no_button.grid(row=2, column=1, sticky=tk.E+tk.W)

        self.do_overwrite_first_label_value = tk.StringVar(value="Selected: None")
        self.do_overwrite_first_label = tk.Label(self.column_0_frame, textvariable=self.do_overwrite_first_label_value)
        self.do_overwrite_first_label.grid(column=0, row=3, columnspan=2)


        #Todo
        # self.btn_undo = tk.Button(self.canvas_frame, text='UNDO', command=self.resetCover)
        # self.btn_undo.grid(row=4, sticky=tk.W + tk.E, columnspan=2)

        self.button2_openfile = tk.Button(self.column_0_frame)
        self.button2_openfile.configure(font='TkDefaultFont', justify='center', text='Open File to Apply this cover')
        self.button2_openfile.grid(column=0, row=4,columnspan=2, pady="15 0")
        self.button2_openfile.configure(command=self.add_file_to_list)

        self.column_0_frame.grid(row=3,pady=20)


        # This is the 2d column of Frame
        # Column 1 - Row 0
        self.treeview1 = ttk.Treeview(self.frame1)
        self.treeview1_cols = ['column3', 'overwrite']
        self.treeview1_dcols = ['column3', 'overwrite']
        self.treeview1.configure(columns=self.treeview1_cols, displaycolumns=self.treeview1_dcols)
        self.treeview1.column('#0', anchor='center', stretch=False, width=65)
        self.treeview1.column('column3', anchor='w', stretch=True, width=300, minwidth=260)
        self.treeview1.column('overwrite', anchor='center', stretch=True, width=60)

        self.treeview1.heading('column3', anchor='center', text='Queue')
        self.treeview1.heading('overwrite', anchor='center', text='Overwrite')
        self.treeview1.grid(column=1, row=0)
        # Column 1 - Row 1
        self.button3_proceed = tk.Button(self.frame1)
        self.button3_proceed.configure(text='Proceed')
        self.button3_proceed.grid(column=1, row=1)
        self.button3_proceed.configure(command=self.process)

        # Column 1 - Row 2

        self.progressbar_frame = tk.Frame(self.frame1,background="green",width=60,height=90)
        self.progressbar_frame.grid(column=1, row=2, rowspan=2, sticky=tk.W+tk.E,padx=30)

        # End frame
        self.frame1.configure(height='500', padding='20', width='400')
        self.frame1.grid(column=1, row=1)

        # Process first cover
        # self.opencovers()
        # try:
        #     self.show_first_cover()
        # except UnidentifiedImageError as e:
        #     print(f"Errrrrrror {e}")
        #     logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}",e)
        self.disableButtons()
        self.button3_load_images.config(state="normal")
    def set_do_overwrite_first_label(self, enable):

        if enable:
            self.do_overwrite_first.set(True)
            self.do_overwrite_first_label_value.set("Selected: Overwrite 0001.ext")
            self.overwrite_yes_button.config(relief=tk.SUNKEN)
            self.overwrite_no_button.config(relief=tk.RAISED)
        else:
            self.do_overwrite_first.set(False)
            self.do_overwrite_first_label_value.set("Selected: Append 0001.ext")
            self.overwrite_yes_button.config(relief=tk.RAISED)
            self.overwrite_no_button.config(relief=tk.SUNKEN)

    def opencovers(self):
        """
        Open tki nter.askopenfilename all covers that are going to be placed inside each chapter and loads iter cycle
        """

        velog("Selecting covers in opencovers")
        self.button3_load_images.destroy()
        covers_path_list = filedialog.askopenfiles(initialdir=launch_path,
                                                   title="Open all covers you want to work with:")
        self.licycle = cycle(covers_path_list)

        self.nextelem = next(self.licycle)
        self.prevelem = None
        self.enableButtons()
        try:
            self.show_first_cover()

        except UnidentifiedImageError as e:
            print(f"Errrrrrror {e}")
            logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}",e)

    def show_first_cover(self):
        velog("Printing first image in canvas")
        self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        image = Image.open(self.thiselem.name)
        image = image.resize((300, 445), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(image)
        self.canvas_image = self.canvas1_coverimage.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.cover_image_name_label_var.set(os.path.basename(self.thiselem.name))

    def reset_overwrite_status(self):
        if self.do_overwrite_first_label_value.get() == "Selected: None":
            print(self.do_overwrite_first_label_value.get())
            mb.showwarning(title="Select overwrite mode", message="You need to choose to append the cover to the file or overwrite 0001.ext file")
            raise NoOverwriteSelected("No Overwrite mode Selected")
        self.do_overwrite_first_label_value.set("Selected: None")
        self.overwrite_yes_button.config(relief=tk.RAISED)
        self.overwrite_no_button.config(relief=tk.RAISED)

    def display_next_cover(self):
        velog("Printing next cover in canvas")
        self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        print(self.thiselem)
        try:
            rawimage: Image = Image.open(self.thiselem.name)
        except UnidentifiedImageError as e:
            logging.critical(f"UnidentifiedImageError - Image file: {self.thiselem.name}",e)
            print(f"Errrrrrror {e}")
        image = rawimage.resize((300, 445), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(image)
        # print(self.label.gettags("IMG10"))
        self.canvas1_coverimage.itemconfig(self.canvas_image, image=self.image)
        self.cover_image_name_label_var.set(os.path.basename(self.thiselem.name))

    def add_file_to_list(self):
        velog("Adding files to processing list")
        try:
            self.reset_overwrite_status()
        except NoOverwriteSelected:
            return

        covers_path_list = filedialog.askopenfiles(initialdir=launch_path,
                                                  title="Select file to apply cover",
                                                  filetypes=(("CBZ Files", "cbz"),
                                                             ("All types", "*"))
                                                  )

        image = Image.open(self.thiselem.name)
        image = image.resize((40, 60), Image.ANTIALIAS)
        self.image_in_confirmation = ImageTk.PhotoImage(image)

        self.covers_path_in_confirmation[str(self.image_in_confirmation)] = []
        for iterated_file_path in covers_path_list:
            iterated_file_path = iterated_file_path.name
            tmp_dic = dict(imagepath=self.thiselem.name,
                           filepath=iterated_file_path,
                           overwrite=self.do_overwrite_first.get(),
                           image_not_garbage_collected=self.image_in_confirmation)

            self.covers_path_in_confirmation[str(self.image_in_confirmation)].append(tmp_dic)
            displayed_file_path = f"...{os.path.basename(iterated_file_path)[-46:]}"

            self.treeview1.insert(parent='', index='end', image=self.image_in_confirmation,
                                  values=(displayed_file_path, self.do_overwrite_first.get()))
            velog(f"Added {os.path.basename(iterated_file_path)} to the processing queue")

    def process(self):
        velog("Starting processing of files.")
        self.button3_proceed.config(relief=tk.SUNKEN, text="Processing")

        total = len(self.covers_path_in_confirmation)

    # def process_and_bar(self,function,function_args,counter):
        print("PROCESS_AND_BAR")

        class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
            def __init__(self_waitup):
                Thread.__init__(self_waitup)  # Override the __init__
                self_waitup.i_waited_for_this = ""

            def run(self_waitup):
                processed_counter = 1
                processed_errors = 0

                for item in self.covers_path_in_confirmation:
                    pathdict = self.covers_path_in_confirmation
                    for file in self.covers_path_in_confirmation[item]:


                        print(pathdict[item])
                        print(file)
                        print()
                        cover_path = file["imagepath"]
                        cbz_file = file["filepath"]
                        cover_name = os.path.basename(cover_path)
                        cover_format = re.findall(r"(?i)\.[a-z]{3}$", cover_path)[0]
                        velog(f"Starting processing for file: {cover_name}")
                        try:
                            if self.do_overwrite_first.get():
                                data = cover_process_item_info(cbz_file, cover_path, cover_name, cover_format)
                                updateZip(data)
                            else:
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

                # self.function(self.function_args)
            #     timestamp = time.time()
            #
            #     undoJson["Rename"] = {}
            #     undoJson["Rename"][timestamp] = []
            #     # print("date and time:",date_time)
            #     for chapterinfoFileName in self.filesToRrename_data:
            #         newFile_Name = f"{chapterinfoFileName.name} Vol.{self.volNumber} {chapterinfoFileName.chapterinfo}{chapterinfoFileName.afterchapter}"
            #         oldPath = chapterinfoFileName.fullpath
            #         newPath = f"{os.path.dirname(chapterinfoFileName.fullpath)}\{newFile_Name}"
            #         print("####\n")
            #         undoJson["Rename"][timestamp].append({"oldPath": oldPath, "newPath": newPath})
            #
            #         print(oldPath)
            #         print(newPath)
            #         os.rename(oldPath, newPath)
            #     # whatever wants to run here
            #     with open(undoJsonFile, "w") as f:
            #         json.dump(undoJson, f)
            #     print(undoJson)
            #
                global pb_flag
                pb_flag = False
                self_waitup.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
                print("Done")
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
                self_progress.pb_text = tk.Label(self_progress.pb_root, textvariable=self_progress.label_progress_text, anchor="w")
                self_progress.pb.start()
                velog("Started progress bar")

                # self_progress.pb_label.grid(row=0, column=0, sticky=tk.W)
                self_progress.pb.grid(row=0, column=0, sticky=tk.W+tk.E)
                self_progress.pb_text.grid(row=1, column=0, sticky=tk.W+tk.E)
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

                print("File processed")

                # for widget in self_progress.pb_root.winfo_children():
                #     widget.destroy()
                return

        global pb_flag
        pb_flag = True
        global t1
        global t2

        self.disableButtons()
        # t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
        #
        # t2 = WaitUp()
        #
        # t2.start()  # use start() instead of run() for threading module
        # t1.startup()  # start the progress bar
        # t2.join()  # wait for WaitUp to finish before proceeding
        # t1.stop()  # destroy the progress bar object
        velog("Clearing queue")
        self.treeview1.delete(*self.treeview1.get_children())
        velog("All done")


        self.enableButtons()
        self.button3_proceed.config(relief=tk.RAISED, text="Proceed")

    def enableButtons(self):
        for w in self.frame1.winfo_children():
            if w.winfo_class() == "Button":
                print(w.winfo_name())

                # print(w.winfo_class())
                w.configure(state="normal")
            if w.winfo_children():
                for w2 in w.winfo_children():
                    print(w2.winfo_name())

                    if w2.winfo_class() == "Button":
                        # print(w.winfo_class())
                        w2.configure(state="normal")
                    if w2.winfo_children():
                        for w3 in w2.winfo_children():
                            print(w3.winfo_name())

                            if w3.winfo_class() == "Button":
                                # print(w.winfo_class())
                                w3.configure(state="normal")
    def disableButtons(self):
        for w in self.frame1.winfo_children():
            if w.winfo_class() == "Button":
                print(w.winfo_name())

                # print(w.winfo_class())
                w.configure(state="disabled")
            if w.winfo_children():
                for w2 in w.winfo_children():
                    print(w2.winfo_name())

                    if w2.winfo_class() == "Button":
                        # print(w.winfo_class())
                        w2.configure(state="disabled")
                    if w2.winfo_children():
                        for w3 in w2.winfo_children():
                            print(w3.winfo_name())

                            if w3.winfo_class() == "Button":
                                # print(w.winfo_class())
                                w3.configure(state="disabled")

0
if __name__ == "__main__":

    app = SetVolumeCover()
    app.mainloop()

