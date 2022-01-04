import os
from pathlib import Path
import tkinter
from tkinter import font
import zipfile
import tempfile
from tkinter import * 
from tkinter import ttk
from tkinter.ttk import *
from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askopenfile
from tkinter import messagebox as mb
from PIL import ImageTk,Image
from dataclasses import dataclass
import re
import sys
import time
from threading import *
tk = tkinter
from datetime import datetime
import json
from collapsiblepane import CollapsiblePane as cp

print('__file__:    ', __file__)
print('dir:    ', os.path.dirname(__file__))

ScriptDir = os.path.dirname(__file__)
undoJson = {}
undoJsonFile = f"{ScriptDir}/undo.json"
print(sys.argv)
fn = sys.argv[1::]
print(fn)
fn = " ".join(fn)
print(fn)
launch_path = None
if os.path.exists(fn):
    launch_path = fn 
class CoverDoesNotExist(Exception):
    pass
def checkCoverExists(new_zipFilePath,tmpname,coverFileName,CoverFileFormat,mode):
    with zipfile.ZipFile(new_zipFilePath, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment
            for item in zin.infolist():
                print(item.filename,coverFileName)
                if item.filename != coverFileName:
                    if item.filename.startswith("OldCover"):
                        # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))
                        continue
                    if re.findall(r"0+1\.[a-z]{3}$",item.filename) and mode:
                        zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                        continue
                    if re.findall(r"0+0\.[a-z]{3}$",item.filename) and not mode:
                        zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                        continue
                    zout.writestr(item, zin.read(item.filename))
                else:
                    zout.writestr(f"OldCover{item.filename}.bak",zin.read(item.filename))
def resetCover(new_zipFilePath,tmpname,mode):
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
                    onholdCover = item.filename.replace("OldCover","").replace(".bak","")
                    if re.findall(r"0+0\.[a-z]{3}$",item.filename):
                        coverIsZero = True
                        rawCovername = item
                    elif re.findall(r"0+1\.[a-z]{3}$",item.filename):
                        coverIsZero = False
                        rawCovername = item
                    elif onholdCover.startswith("."):
                        rawCovername= item
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
                    if item.filename.startswith("OldCover"): #and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                        continue
                    if re.findall(r"0+0\.[a-z]{3}$",item.filename):
                        # zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                        # zout.writestr(onholdCover, zin.read(rawCovername.filename))
                        coverIsZero = True
                        continue
            for item in zin.infolist():
                # time.sleep(2)
                if re.findall(r"0+0\.[a-z]{3}$",item.filename) and coverIsZero:
                    zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                    zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    coverIsZero = True
                if item.filename.startswith("OldCover"): #and item.filename == isinstance(rawCovername,zipfile.ZipInfo):
                    continue
                if re.findall(r"0+1\.[a-z]{3}$",item.filename):
                    if onholdCover:
                        onholdCover = f"0001{rawholdCover}"
                    zout.writestr(f"OldCover_{item.filename}.bak",zin.read(item.filename))
                    zout.writestr(onholdCover, zin.read(rawCovername.filename))
                    continue
                else:
                    zout.writestr(item, zin.read(item.filename))
                    # zout.writestr(f"OldCover{CoverFileFormat}.bak",zin.read(item.filename))

def doResetCover(zipFilePath):
    oldZipFilePath=zipFilePath
    new_zipFilePath =  '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$",zipFilePath)[0])

    os.rename(zipFilePath,new_zipFilePath)
    
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    resetCover(new_zipFilePath,tmpname,True)
    
    # checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)

    os.remove(new_zipFilePath)
    os.rename(tmpname,new_zipFilePath)
    os.rename(new_zipFilePath,oldZipFilePath)
def updateZip(zipFilePath, coverFilePath,coverFileName,coverFileFormat):
    oldZipFilePath=zipFilePath
    new_zipFilePath =  '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$",zipFilePath)[0])
    try:
        os.rename(zipFilePath,new_zipFilePath)
    except PermissionError as e:
        mb.showerror("Can't access the file becuase it's being used by a different process",f"Exception:{e}")
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipFilePath))
    os.close(tmpfd)
    new_coverFileName = f"0001{coverFileFormat}"
    checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,True)

    os.remove(new_zipFilePath)
    os.rename(tmpname,new_zipFilePath)
    
    basenameFile = os.path.basename(coverFilePath)
    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(coverFilePath,new_coverFileName)
    os.rename(new_zipFilePath,oldZipFilePath)
def appendZip(zipFilePath, coverFilePath,coverFileName,coverFileFormat):
    new_zipFilePath =  "{}.zip".format(re.findall(r'(?i)(.*)(?:\.[a-z]{3})$',zipFilePath)[0])
    try:
        os.rename(zipFilePath,new_zipFilePath)
    except PermissionError as e:
        mb.showerror("Can't access the file becuase it's being used by a different process",f"Exception:{e}")
    
    oldZipFilePath=zipFilePath

    
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(new_zipFilePath))
    os.close(tmpfd)

    new_coverFileName = f"0000{coverFileFormat}" 

    checkCoverExists(new_zipFilePath,tmpname,new_coverFileName,coverFileFormat,False)
    
    os.remove(new_zipFilePath)
    os.rename(tmpname,new_zipFilePath)

    with zipfile.ZipFile(new_zipFilePath, mode='a', compression=zipfile.ZIP_STORED) as zf:
        zf.write(coverFilePath,new_coverFileName)
    os.rename(new_zipFilePath,oldZipFilePath)

def formatTimestamp(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime("%Y/%m/%d %H:%M:%S")

font_H0 = ("BOLD",20)   
font_H1 = ("BOLD",18)
font_H2 = ("BOLD",15)
font_H3 = ("BOLD",12)


MainWindow = Tk()
MainWindow.geometry('1200x300')
MainWindow.maxsize(height=650)
MainWindow.configure(bg='#c1c1c1',padx=30,pady=30)


MainLabelVar = StringVar()
MainLabelFrame = Frame(MainWindow)
MainLabelFrame.pack(fill="none", expand=True)
CurrentModeVar = StringVar()
IntroFrame = Frame(MainWindow)
IntroFrame.pack(fill="none", expand=True)

root = Frame(MainWindow)    
root.pack(fill="none", expand=True)

class MangaManager:
    def __init__(mainSelf):
        MainLabelVar.set("What do you want to do?")
        mainSelf.MainLabel = Label(MainLabelFrame,textvariable=MainLabelVar,font=font_H1)
        mainSelf.MainLabel.grid(row=0,columnspan=2)
        mainSelf.RenameBtn = Button(IntroFrame, text ='Add Volumes', command=mainSelf.AddVolumes)
        mainSelf.RenameBtn.grid(row=0,column=0,sticky=tkinter.W+tkinter.E)
        mainSelf.ChangeCover = Button(IntroFrame, text ='Change cover', command=mainSelf.SetCover)
        mainSelf.ChangeCover.grid(row=0,column=1,sticky=tkinter.E+tkinter.W)
        
        mainSelf.CurrentMode = Label(MainLabelFrame,textvariable=CurrentModeVar,font=font_H1)
        
        MainLabelVar.set("Manga Manager")
        mainloop()

    def AddVolumes(mainSelf):
        # IntroFrame.destroy()
        CurrentModeVar.set("Add Volumes")
        mainSelf.CurrentMode.grid(row=1,columnspan=2)
        mainSelf.AddMangasVolumes(mainSelf,launch_path)
    def SetCover(mainSelf):
        # IntroFrame.destroy()
        CurrentModeVar.set("Set cover")
        mainSelf.CurrentMode.grid(row=1,columnspan=2)
        mainSelf.MangasCoverSetter(mainSelf,launch_path)
    class MangasCoverSetter():
        def __init__(self,mainSelf,launch_path = None,done=False):
            self.root = root
            self.clear_frame(root)
            self.mainSelf = mainSelf
            print("init")
            self.overwriteFirstFileLabel = tkinter.StringVar()
            self.instructionsLabel = tkinter.StringVar()
            self.overwriteFirstFileValue = tkinter.BooleanVar()
            if done:
                if done == "Error":
                    MainLabelVar.set("Manga Manager\nProcessing failed!")
                else:
                    MainLabelVar.set("Manga Manager\nProcessing done!")
                self.instructionsLabel.set("Overwrite existing '0001.ext' file?")
                done=False
            else:
                self.instructionsLabel.set("Overwrite existing '0001.ext' file?")
            helpButton = Button(root,text="HELP",command=lambda:mb.showinfo("INFO","Overwrite existing '0001.ext'\n\nIf set to YES, it will replace the file currenly named 0001.ext with the new image (cover)\n\nIf set to NO the new image (cover) will be named 0000.ext\n\nIn both situations the original file is saved in a file named OldCover.001.ext.bak\nIf this file is deleted, undoing modifications won't be possible."))
            helpButton.grid(row=1,column=1)
            label = tkinter.Label(root, textvariable=self.instructionsLabel,font=font_H1,)
            label.grid(row=0,columnspan=2)
            self.label_status = tkinter.Label(root,textvariable=self.overwriteFirstFileLabel,font=font_H2)
            self.label_status.grid(row=1,columnspan=2)

            self.btn_yes = Button(root, text ='YES', command = lambda:self.setOverwriteLabel(True))
            self.btn_yes.grid(row=3,column=0,sticky=tkinter.W+tkinter.E)
            self.btn_no = Button(root, text ='NO', command = lambda:self.setOverwriteLabel(False))
            self.btn_no.grid(row=3,column=1,sticky=tkinter.W+tkinter.E)

            self.btn_undo = Button(root, text ='UNDO', command = self.resetCover)
            self.btn_undo.grid(row=4,sticky=tkinter.W+tkinter.E,columnspan=2)

            label = Label(root,text="Select CBZ files now")
            
            
            mainloop()
        def setOverwriteLabel(self,enable):
            
            if enable:
                self.overwriteFirstFileValue.set(1)
                self.overwriteFirstFileLabel.set("YES")
            else:
                self.overwriteFirstFileValue.set(0)
                self.overwriteFirstFileLabel.set("NO")
            self.btn_yes.destroy()
            self.btn_no.destroy()
            self.btn_undo.destroy()
            self.instructionsLabel.set(f"Overwrite:{self.overwriteFirstFileLabel.get()}\n Now select the CBZ that you want this change applied to")
            self.btn = Button(root, text ='Open', command = self.open_file)
            self.btn.grid(row=1,columnspan=2)
            self.label_status.destroy()
            # self.instructionsLabel.set("Select the CBZ that you want this change applied to")
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
        def process_setCover(self):
            print("processRenaming")
            
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self,files,covername,overwriteFirstFileValue):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.files = files
                    self.covername = covername
                    self.overwriteFirstFileValue = overwriteFirstFileValue

                def run(self):
                    print("run2")
                    # self.btn.destroy()
                    for cbzFile in self.files:
                        # pathdir = os.path.basename(cbzFile)
                        pathdir = cbzFile
                        # print("value"+self.overwriteFirstFileValue.get())
                        msg = 'This data did not exist in a file before being added to the ZIP file'
                        coverFilePath = self.covername
                        coverFileName = os.path.basename(coverFilePath)
                        coverFileFormat = re.findall(r"(?i)\.[a-z]{3}$",coverFilePath)[0]

                        try:
                            if self.overwriteFirstFileValue.get():
                                updateZip(cbzFile,coverFilePath,coverFileName,coverFileFormat)
                            else:
                                appendZip(cbzFile,coverFilePath,coverFileName,coverFileFormat)
                        except FileExistsError as e:
                            mb.showwarning(f"[ERROR] File already exists",f"Trying to create:\n`{e.filename2}` but already exists\n\nException:\n{e}")
                            continue


                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = tkinter.StringVar()
                    self.text = text
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, textvariable=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    MainLabelVar.set("Manga Manager\nProcessing...")
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.label.set("Done")
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    # self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            pb_flag = True
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            self.mainSelf.RenameBtn.config(state="disabled")
            self.mainSelf.ChangeCover.config(state="disabled")
            t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
            t2 = WaitUp(self.files,self.cover.name,self.overwriteFirstFileValue)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            # self.instructionsLabel.set("Done\nThis script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
            time.sleep(5)
            self.mainSelf.RenameBtn.config(state="enabled")
            self.mainSelf.ChangeCover.config(state="enabled")
            self.instructionsLabel.set("Done!")
            self.__init__(mainSelf = self.mainSelf,done=False)
        def open_file(self):
            self.btn.destroy()
            print("openfile")
            self.files = askopenfilenames(filetypes =[('Compressed Comic Files', '*.cbz')])
            self.instructionsLabel.set("Choose the cover image")
            self.btn = Button(root, text ='Open', command = self.open_cover)
            self.btn.grid(row=1,columnspan=2)
            print(self.files)
        def open_cover(self):
            print("opencover")
            self.cover = askopenfile(filetypes =[('Image Files', '*jpg')])
            print(self.cover.name)
            # os.chdir(os.path.dirname(self.cover.name))
                
            # canvas = Canvas(root, width = 300, height = 445)  
            # canvas.grid(row=1,column=2)  
            # img = Image.open(self.cover.name)
            # resized_img = img.resize((300,445),Image.ANTIALIAS)  
            # new_image = ImageTk.PhotoImage(resized_img)
            # canvas.create_image(20, 20, anchor=NW, image=new_image) 
            self.process_setCover()
            # root.mainloop()


        def resetCover(self):
            
            self.btn_yes.destroy()
            self.btn_no.destroy()
            self.btn_undo.destroy()
            self.files = askopenfilenames(filetypes =[('Compressed Comic Files', '*.cbz')])
            self.process_resetCover()
        def process_resetCover(self):
            global ThreadException
            ThreadException = None
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self,files):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.files = files
                def run(self):
                    global pb_flag
                    for cbzFile in self.files:
                        # pathdir = os.path.basename(cbzFile)
                        pathdir = cbzFile
                        # print("value"+self.overwriteFirstFileValue.get())
                        msg = 'This data did not exist in a file before being added to the ZIP file'

                        try:
                            try:
                                try:
                                    doResetCover(cbzFile)
                                except CoverDoesNotExist as e:
                                    mb.showerror("Can't undo changes. Files does not have old cover","The script never deletes the old cover instead it is be saved in a file called OldCover000.ext.bak\nFile not found: can't undo modifications.\nFile did not save correctly. Manually rename it back to .CBZ\n\nAttempting to fix file...")
                                    pb_flag = False
                                    global ThreadException
                                    ThreadException = CoverDoesNotExist
                                    oldZipFilePath=cbzFile
                                    new_zipFilePath =  '{}.zip'.format(re.findall(r"(?i)(.*)(?:\.[a-z]{3})$",oldZipFilePath)[0])
                                    try:
                                        os.rename(new_zipFilePath,oldZipFilePath)
                                        mb.showinfo("Successfully recovered file","File recovery was successfull no other actions required.")
                                    except:
                                        mb.showerror("Failed to recover file","Failed to recover file. You need to manually rename it with the CBZ extension.")
                                        
                                    raise Exception
                                    
                            except PermissionError as e:
                                mb.showerror("Can't access the file because it's being used by a different process",f"Exception:{e}")
                                continue
                        except FileExistsError as e:
                            mb.showwarning(f"[ERROR] File already exists",f"Trying to create:\n`{e.filename2}` but already exists\n\nException:\n{e}")
                            continue


                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = tkinter.StringVar()
                    self.text = text
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, textvariable=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    MainLabelVar.set("Manga Manager\nProcessing...")
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.label.set("Done")
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    # self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            pb_flag = True
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            
            ready = False
            self.mainSelf.RenameBtn.config(state="disabled")
            self.mainSelf.ChangeCover.config(state="disabled")
            t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
            t2 = WaitUp(self.files)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            # self.instructionsLabel.set("Done\nThis script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
            time.sleep(5)
            self.mainSelf.RenameBtn.config(state="enabled")
            self.mainSelf.ChangeCover.config(state="enabled")
            # .set("Done!")
            if ThreadException:
                MainLabelVar.set("Manga Manager\nSome error occured")
                self.__init__(mainSelf = self.mainSelf,done="Error")
            else:
                MainLabelVar.set("Manga Manager\nProcessing done!")
                self.__init__(mainSelf = self.mainSelf,done=True)
        

    class AddMangasVolumes():
        def __init__(self,mainSelf,launch_path = None,done = False,):
            self.root = root
            self.clear_frame(self.root)
            print("init")
            # self.root = Tk()
            self.mainSelf = mainSelf
            
            self.instructionsLabel = tkinter.StringVar()
            self.subinstructionsLabel = tkinter.StringVar()
            
            if done:
                MainLabelVar.set("Manga Manager\nProcessing done!")
                self.instructionsLabel.set("This script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
                done = False
            else:
                self.done=False
                self.instructionsLabel.set("This script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
            self.subinstructionsLabel.set("This naming convention must be followed for the script to work properly")
            
            self.label = tkinter.Label(self.root, textvariable=self.instructionsLabel,font=font_H2)
            self.label.grid(row=0)
            self.sublabel = tkinter.Label(self.root, textvariable=self.subinstructionsLabel,font=font_H3)
            self.sublabel.grid(row=1)

            self.btn_yes = Button(self.root, text ='OK', command = self.SelectFilesToRename)
            self.btn_yes.grid(row=2,sticky=tkinter.W+tkinter.E)
            self.btn_undo = Button(self.root, text ='UNDO', command = self.undo_renaming)
            self.btn_undo.grid(row=3,sticky=tkinter.W+tkinter.E)

            
            label = Label(self.root,text="Select CBZ files now")
            mainloop()
        def SelectFilesToRename(self):
            self.btn_yes.destroy()
            self.sublabel.destroy()
            self.btn_undo.destroy()

            self.instructionsLabel.set(f"Now select the files you want to rename")
            self.btn = Button(self.root, text ='Open', command = self.open_file)
            self.btn.grid(row=2)
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
        @dataclass
        class ChapterFileNameData:
            """Class to keep title data chapter and anything after chapter to join together after adding vol info"""
            name:str
            chapterinfo:str
            afterchapter:str
            fullpath:str

            def __init__(self, name: str, chapterinfo: str, afterchapter: str,fullpath:str):
                self.name = name
                self.chapterinfo = chapterinfo
                self.afterchapter = afterchapter
                self.fullpath = fullpath
        def initFrames(self):
            self.HeaderFrame = tk.Frame(self.root)
            self.HeaderFrame.grid(row=0)
            self.FooterButton = tk.Frame(self.root)
            self.FooterButton.grid(row=2)
        def open_file(self):
            self.btn.destroy()
            print("openfile")
            self.files = askopenfilenames()
            
            print(self.files)
            self.setup_volumeInt()
        def setup_volumeInt(self):
            print("opencover")
            self.instructionsLabel.set("Write the volume number you wish to apply. (Default 0)")
            self.volNumber = tkinter.IntVar()
            self.VolEntry = Entry(self.root,textvariable=self.volNumber)
            self.VolEntry.grid(row=1)

            self.volConfirmation = Button(self.root, text ='Continue', command = self.process)
            self.volConfirmation.grid(row=2,sticky=tkinter.W+tkinter.E)
        def process(self):
            try:
                if not self.VolEntry.get():
                    self.setup_volumeInt()
            except:
                self.instructionsLabel.set("Input a valid number\nWrite the volume number you wish to apply")
                self.setup_volumeInt()
            
            self.volConfirmation.destroy()
            self.VolEntry.destroy()
            print("run2")
            self.filesToRename_data = []
            for file in self.files:
                filepath = file
                filename = os.path.basename(filepath)
                regexSearch = re.findall(r"(?i)(.*)(Ch[0-9]*|Chapter\s[0-9]*|Ch\.[0-9]*|Ch\s[0-9]*)(\.[a-z]{3}$)",filename)
                if regexSearch:
                    self.instructionsLabel.set("Please check the following is correct")
                    r = regexSearch[0]
                    print(r)
                    self.filesToRename_data.append(self.ChapterFileNameData(r[0],r[1],r[2],filepath))
                else:
                    self.instructionsLabel.set("Did not find Ch/Chapter.\n Using last integer instead...\nPlease check the following is correct")
                    regexSearch = re.findall(r"(?i)(.*)\s([0-9]*)(\.[a-z]{3}$)",filename)
                    if regexSearch:
                        r = regexSearch[0]
                        self.filesToRename_data.append(self.ChapterFileNameData(r[0],r[1],r[2],filepath))
            self.initFrames()
            HeaderFrame = self.HeaderFrame
            HeaderFrame.grid(row=0)
            FooterButton = self.FooterButton
            FooterButton.grid(row=3)
            Item_ID_appender = 1
            self.Item_ID_appender = Item_ID_appender
            MainWindow.geometry('1000x600')
            s = Style()
            tableframe = tkinter.Frame(self.root,pady=20,padx=20,bg="#2a2c2d")
            tableframe.grid(row=1)
            tableframe.grid_propagate(True)
            table = ttk.Treeview(tableframe,padding=5)
            table.grid_propagate(True)
            table['columns'] = ('old_name', 'to', 'new_name')
            table.column("#0", width=0,stretch=NO)
            table.column("old_name",stretch=YES,width=400,anchor=W)
            table.column("to",width=20,anchor=W,stretch=NO)
            table.column("new_name",stretch=YES,width=425,anchor=E)

            table.heading("#0",text="",anchor=W)
            table.heading("old_name",text="OLD NAME",anchor=CENTER)
            table.heading("to",text="",anchor=W)
            table.heading("new_name",text="NEW NAME",anchor=CENTER)
            table.pack(expand=True,anchor=CENTER,fill=BOTH,padx=2,pady=5)     
            
            for chapterinfoFileName in self.filesToRename_data:
                old_file_path = f"{chapterinfoFileName.name} {chapterinfoFileName.chapterinfo}{chapterinfoFileName.afterchapter}"
                self.newFile_Name = f"{chapterinfoFileName.name} Vol.{self.volNumber.get()} {chapterinfoFileName.chapterinfo}{chapterinfoFileName.afterchapter}"
                self.Item_ID_appender +=1
                table.insert(parent='',index='end',iid=self.Item_ID_appender,text='',values=("..."+old_file_path[12:]," -> ","..."+self.newFile_Name[12:]))
            table.grid(row=1)        

            Confirm_btn = tk.Button(FooterButton, text='YES', command=self.process_renaming)
            Confirm_btn.grid(row=5,column=0,sticky=W)
            Confirm_btn_no = tk.Button(FooterButton, text='NO',command=self.__init__)
            Confirm_btn_no.grid(row=5,column=1,sticky=E)

        def process_renaming(self):
            print("processRenaming")
            
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self,filesToDrename_data,volNumber):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.filesToRrename_data = filesToDrename_data
                    self.volNumber = volNumber
                def run(self):
                    
                    timestamp = time.time()
                    
                    
                    undoJson["Rename"] = {}
                    undoJson["Rename"][timestamp] = []
                    # print("date and time:",date_time)
                    for chapterinfoFileName in self.filesToRrename_data:
                        newFile_Name = f"{chapterinfoFileName.name} Vol.{self.volNumber} {chapterinfoFileName.chapterinfo}{chapterinfoFileName.afterchapter}"
                        oldPath = chapterinfoFileName.fullpath
                        newPath = f"{os.path.dirname(chapterinfoFileName.fullpath)}\{newFile_Name}"
                        print("####\n")
                        undoJson["Rename"][timestamp].append({"oldPath":oldPath,"newPath":newPath})

                        print(oldPath)
                        print(newPath)
                        os.rename(oldPath,newPath)
                    #whatever wants to run here
                    with open(undoJsonFile,"w") as f:
                        json.dump(undoJson,f)
                    print(undoJson)

                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = tkinter.StringVar()
                    self.text = text
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text
                def startup(self):
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, textvariable=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    MainLabelVar.set("Manga Manager\nProcessing...")
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        time.sleep(.1)

                def stop(self):
                    self.label.set("Done")
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    # self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            pb_flag = True
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            self.mainSelf.RenameBtn.config(state="disabled")
            self.mainSelf.ChangeCover.config(state="disabled")
            t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
            t2 = WaitUp(self.filesToRename_data,self.volNumber.get())  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            time.sleep(3)
            MainLabelVar.set("Manga Manager\nDone")
            self.mainSelf.RenameBtn.config(state="enabled")
            self.mainSelf.ChangeCover.config(state="enabled")
            self.__init__(mainSelf=self.mainSelf,done=True)

        def undo_renaming(self):
            self.sublabel.destroy()
            self.btn_yes.destroy()
            self.btn_undo.destroy()
            print("undo")
            with open(undoJsonFile,"r") as f:
                global undoJson
                undoJson = json.load(f)
                
            eventsList = Frame(self.root)
            eventsList.grid(row=1)
            
            print(undoJson)
            w, h = root.winfo_screenwidth(), root.winfo_screenheight()
            MainWindow.geometry("%dx%d+0+0" % (w-30, 600))
            if not undoJson["Rename"]:
                self.instructionsLabel.set("This is the renaming log.\nThis list is empty right now")
            else:
                self.instructionsLabel.set("This is the renaming log. Select the one you want to revert")
        
            counter = 0
            for events in undoJson["Rename"]:

                date_time = formatTimestamp(float(events))
                
                cpane = cp(eventsList, f'Expanded - {date_time}', f'Collapsed - {date_time}')
                cpane.grid(row = counter, column = 0)
                counter+=1
                
                # print(undoJson["Rename"][events])
                eventFrame = tkinter.Frame(cpane.frame,highlightbackground="black",highlightthickness=0.5,pady=10)
                eventFrame.grid(row=counter)
                counter2 = 0
                for event in undoJson["Rename"][events]:
                    # print(event)
                    # print(undoJson["Rename"][events])
                    
                    label_old = Label(eventFrame, text="OLD: " +event["oldPath"]).grid(row=counter2,sticky=W)
                    counter2 +=1
                    
                    label_new = Label(eventFrame,text="NEW: " +event["newPath"]).grid(row=counter2,sticky=W)
                    counter2 +=1
                    sep = ttk.Separator(eventFrame,orient="horizontal").grid(row=counter2,sticky=E+W,padx=20)

                    counter2 +=1
                btnSelect = Button(eventFrame,text="Revert",command=lambda var=events:self.confirmUndo(var)).grid(row=counter2)
                # counter2 +=1
        
        
        def confirmUndo(self,somth):
            self.instructionsLabel.set("Confirm you want to do these ")
            self.initFrames()
            HeaderFrame = self.HeaderFrame
            HeaderFrame.grid(row=0)
            FooterButton = self.FooterButton
            FooterButton.grid(row=3)
            Item_ID_appender = 1
            self.Item_ID_appender = Item_ID_appender
            MainWindow.geometry('1000x600')
            s = Style()
            tableframe = tkinter.Frame(self.root,pady=20,padx=20,bg="#2a2c2d")
            tableframe.grid(row=1)
            tableframe.grid_propagate(True)
            table = ttk.Treeview(tableframe,padding=5)
            table.grid_propagate(True)
            table['columns'] = ('old_name', 'to', 'new_name')
            table.column("#0", width=0,stretch=NO)
            table.column("old_name",stretch=YES,width=400)
            table.column("to",width=30,anchor=CENTER,stretch=NO)
            table.column("new_name",stretch=YES,width=400,anchor=E)

            table.heading("#0",text="",anchor=W)
            table.heading("old_name",text="OLD NAME",anchor=CENTER)
            table.heading("to",text="",anchor=W)
            table.heading("new_name",text="NEW NAME",anchor=CENTER)
            table.pack(expand=True,anchor=CENTER,fill=BOTH,padx=5,pady=5)     
            self.somthEventTimestamp = somth
            for event in undoJson["Rename"][somth]:
                old_file_path = event["newPath"]
                self.newFile_Name = event["oldPath"]
                self.Item_ID_appender +=1
                table.insert(parent='',index='end',iid=self.Item_ID_appender,text='',values=(old_file_path," -> ",self.newFile_Name))
            table.grid(row=1)        
            self.filesToProcess = undoJson["Rename"][somth]
            Confirm_btn = tk.Button(FooterButton, text='YES', command=self.process_UndoRenaming)
            Confirm_btn.grid(row=5,column=0,sticky=W)
            Confirm_btn_no = tk.Button(FooterButton, text='NO',command=self.__init__)
            Confirm_btn_no.grid(row=5,column=1,sticky=E)
        def process_UndoRenaming(self):
            self.initFrames()
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self,filesToProcess,somthEventTimestamp):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.filesToProcess = filesToProcess
                    self.somthEventTimestamp = somthEventTimestamp
                def run(self):
                    try:
                        for file in self.filesToProcess:
                            os.rename(file["newPath"],file["oldPath"])
                        del undoJson["Rename"][self.somthEventTimestamp]
                        with open(undoJsonFile,"w") as f:
                            json.dump(undoJson,f)
                    except FileNotFoundError as e:
                        mb.showerror("File not found:",f"The file {e.filename} was not found\n\nException:{e}")
                    
                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = tkinter.StringVar()
                    self.text = text
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text
                def startup(self):
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, textvariable=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    MainLabelVar.set("Manga Manager\nProcessing...")
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        time.sleep(.1)

                def stop(self):
                    self.label.set("Done")
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    # self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            pb_flag = True
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            self.mainSelf.RenameBtn.config(state="disabled")
            self.mainSelf.ChangeCover.config(state="disabled")
            t1 = ProgressBarIn(title="Processing", label="Please wait", text="Processing files")
            t2 = WaitUp(self.filesToProcess,self.somthEventTimestamp)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            time.sleep(3)
            # self.instructionsLabel.set("Done\nThis script will append Vol.XX just before any Ch X.ext/Chapter XX.ext to the files you select")
            MainWindow.geometry('1200x300')
            MainLabelVar.set("Manga Manager\nDone")
            self.mainSelf.RenameBtn.config(state="enabled")
            self.mainSelf.ChangeCover.config(state="enabled")
            self.__init__(mainSelf=self.mainSelf,done=True)
           


app = MangaManager().AddMangasVolumes.undo_renaming()