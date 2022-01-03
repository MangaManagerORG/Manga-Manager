
import os
import re
# os.walk
import sys
import threading
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from threading import *
from tkinter import *
from tkinter import DoubleVar, filedialog, font, ttk
import tkinter
from tkinter.constants import BOTH, BOTTOM, CENTER, COMMAND, TOP, X
from tkinter.filedialog import askopenfilename
import pathlib
from functools import partial
from typing import Counter, List
import json


import praw, time, datetime, os, requests, shutil, ffmpeg

# from ASCRIPT_REDDIT_MANAGER.Descargador_Reddit.download_1step import step_1
font_H1 = ("BOLD",23)
font_H2 = ("BOLD",16)

# os.chdir(os.path.dirname(sys.argv[1]))

import tkinter as tk

#
##################### CHANGELOG #################################################################################   
#                                                                                                               #    
#                                                                                                               #    
#   12/11/2021                                                                                                  #    
#       <DIRECT DOWNLOAD>.                                                                                      #    
#           added Feature                                                                                       #    
#           TODO: some links still download 4kb only                                                            #    
#       TODO: Rename by order not renaming but displaying correctly                                             #    
#   16/11/2021                                                                                                  #     
#       <DIRECT DOWNLOAD>                                                                                       #       
#           Added Multi link (separated by /n) supoort                                                          #       
#   17/11/2021                                                                                                  #    
#       <ALL>                                                                                                   #    
#           Default open right clicked folder                                                                   #    
#   20/11/2021                                                                                                  #    
#       <ImageOrganizer_Date>                                                                                   #    
#         Fixed order by date not using create time. Error in code always selected modified                     #    
#   21/11/2021                                                                                                  #    
#       <RedditDownloader>                                                                                      #    
#           Added 1st part of fetching upvotes and saved                                                        #    
#           Fetched posts are saved in 2 json: "ol_upvoted_by_user" and "saved_by_user"                         #    
#                                                                                                               #    
#   23/11/2021                                                                                                  #
#       <RedditDownloader>                                                                                      #
#           Added 1st workign version of downloader seems to work fine for now                                  #    
#################################################################################################################   



class ScriptIndex:
    def __init__(self,launch_path = None):
        
        global root
        root = tk.Tk()
        self.root = root
        my_str = tk.StringVar()
        self.my_str = my_str
        self.root.title("Python Scripts Helper")
        self.selected = ""
        

        self.contentFrame = tk.Frame(root,width=1000,)#,highlightbackground="black",highlightthickness=0.5,padx=5
        self.contentFrame.grid(row=0)
        
        self.HeaderFrame = tk.Frame(self.contentFrame)
        self.HeaderFrame.grid(row=0)
        self.BodyFrame = tk.Frame(self.contentFrame)
        self.BodyFrame.grid(row=1)
        self.FooterFrame = tk.Frame(self.contentFrame)
        self.FooterFrame.grid(row=2)
        
        self.ExitFrame = tk.Frame(root)
        self.ExitFrame.grid(row=1)
        quit_button = tk.Button(self.ExitFrame, text = 'Salir', command=self.quit)
        quit_button.grid(row=0)

        
        self.FooterButton =self.FooterFrame

        #### LAYOUT ROOT
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        


        self.Script_Selection()
        self.root.mainloop()
    def Script_Selection(self):
        
        self.BodyFrame.configure(width=1000,highlightbackground="black",highlightthickness=0.5,padx=5)
        #### LABEL 1 TOP HEADER
        header_label1 = tk.Label(self.HeaderFrame, text=f"SELECT SCRIPT {launch_path}",font=("Arial",15))
        # header_label1 = tk.Label(HeaderFrame, text=f"SELECT SCRIPT {launch_path}")#",font=("Arial",15))
        header_label1.pack()
        #### SELECTOR 
        
        btn = tk.Button(self.BodyFrame, text="[NinjinAnime] Remover", command=lambda :self.show_script("NinjinAnime_Remover"))
        btn.grid(row=0,column=1)

        btn = tk.Button(self.BodyFrame, text="RENAME ITEMS BY ORDER", command=lambda :self.show_script("RENAME_ITEMS_BY_ORDER"))
        btn.grid(row=1,column=1)

        btn = tk.Button(self.BodyFrame, text="FolderFileExtractor", command=lambda :self.show_script("FolderFileExtractor"))
        btn.grid(row=2,column=1)

        btn = tk.Button(self.BodyFrame, text="Organizador de imagenes por fecha", command=lambda :self.show_script("ImageOrganizer_Date"))
        btn.grid(row=3,column=1)
        btn = tk.Button(self.BodyFrame, text="Descarga con Enlace Directo", command=lambda :self.show_script("DirectLinkDownload"))
        btn.grid(row=4,column=1)
        btn = tk.Button(self.BodyFrame, text="Descarga Todo Reddit", command=lambda :self.show_script("RedditDownloader"))
        btn.grid(row=5,column=1)
        btn = tk.Button(self.BodyFrame, text="Comprime carptetas individualmente", command=lambda :self.show_script("MangaFolderZipper"))
        btn.grid(row=6,column=1)
        # btn = tk.Button(self.BodyFrame, text="Modifiica primer archivo de cada cbz", command=lambda :self.show_script("MangaCoverModifier"))
        # btn.grid(row=7,column=1)

        # button = tk.Button(self.FooterFrame, text = 'Salir', command=self.fexit)
        # button.grid(row=0,column=0)
    def show_script(self,script):
        self.BodyFrame.configure(width=1000,highlightthickness=0)
        self.clear_frame(self.HeaderFrame)
        self.clear_frame(self.BodyFrame)
        self.clear_frame(self.FooterFrame)
        
        # self.clear_frame(self.Confirm_SelectionFrame)
        

        if script == "NinjinAnime_Remover":
            self.my_str.set("NinjinAnime_Remover")
            
            self.NinjinAnime_Remover(self.root,self.HeaderFrame,self.BodyFrame,self.FooterFrame)

        elif script == "RENAME_ITEMS_BY_ORDER":
            self.my_str.set("RENAME_ITEMS_BY_ORDER")
            self.RENAME_ITEMS_BY_ORDER(self.root,self.HeaderFrame,self.BodyFrame,self.FooterFrame)

        elif script == "FolderFileExtractor":
            self.my_str.set("FolderFileExtractor")
            self.FolderFileExtractor(self.root,self.HeaderFrame,self.BodyFrame,self.FooterFrame)
        elif script == "ImageOrganizer_Date":
            self.my_str.set("Organizador de imagenes por fecha")
            self.ImageOrganizer_Date(self.root)
        elif script == "DirectLinkDownload":
            self.my_str.set("Descarga con Enlace Directo")
            self.DirectLinkDownload(self.root,self.HeaderFrame,self.BodyFrame,self.FooterFrame)
        elif script == "RedditDownloader":
            self.my_str.set("Descarga todo tu Reddit")
            self.RedditDownloader(self.root)
        elif script == "MangaFolderZipper":
            self.my_str.set("MangaFolderZipper")
            self.MangaFolderZipper(self.root)
        # elif script == "MangaCoverModifier":
        #     self.my_str.set("MangaCoverModifier")
        #     self.MangaCoverModifier(self.root)
    def clear_frame(self,frame):
        for widgets in frame.winfo_children():
            widgets.destroy()
    def fexit(self):
        self.root.destroy()
        exit()
    def quit(self):
        self.root.destroy()       
    def donothing(self):
        # print ('IT WORKED')
        pass
    def run_test(self):
        inp = input("input test >")
        #print("run")
        #print(inp)
    class NinjinAnime_Remover:
        def __init__(self,root,HeaderFrame,BodyFrame,FooterFrame):
            
            self.root = root
            SelDir = tk.StringVar()
            self.SelDir = SelDir
            self.HeaderFrame = HeaderFrame
            self.BodyFrame = BodyFrame
            self.FooterButton = FooterFrame

            SelectionFrame = tk.Frame(self.BodyFrame,width=1000,highlightbackground="black",highlightthickness=0.5,padx=5)
            SelectionFrame.grid(row=1,ipady=4,padx=20)
            self.SelectionFrame = SelectionFrame
            
            Confirm_SelectionFrame = tk.Frame(self.BodyFrame)
            Confirm_SelectionFrame.grid(row=2,ipady=4)
            self.Confirm_SelectionFrame = Confirm_SelectionFrame

            
            self.SelectionFrame = SelectionFrame
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.FooterButton = FooterFrame
            
            #### LAYOUT ROOT

            

            #### LABEL 1 TOP HEADER
            header_label1 = tk.Label(HeaderFrame, text="SELECT FOLDER TO RENAME RECURSIVELY ,REMOVING [NINJINANIME]",font=font_H1)
            header_label1.pack()

            #### SELECTOR 
            # root2 = tix.Tk()
            
            #### FOOTER
            
            def select_folder():
                global fdir
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                if fdir:
                    select_folder_button.destroy()
                    self.print_selected(fdir)
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=select_folder)
                    select_folder_button2.grid(row=1)
                    Confirm_btn.grid(row=1,column=2)
            

            select_folder_button = tk.Button(SelectionFrame,text="ABRIR CARPETA",command=select_folder)
            
            select_folder_button.grid(row=0)
            l0 = tk.Label(SelectionFrame,  text="SELECTED FOLDER:")
            
            l1 = tk.Label(SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            
            # #print(fdir)
            Confirm_btn = tk.Button(Confirm_SelectionFrame, text="CONFIRMAR", command=self.process_recursive)


            self.root.mainloop()
        def print_selected(self,seldir):
            self.SelDir.set(seldir)
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()

        def quit(self):
            self.root.destroy()
        def donothing(self):
            # print ('IT WORKED')
            pass

        def process_recursive(self):
            global fdir
            rootdir = fdir
            self.clear_frame(self.HeaderFrame)
            self.clear_frame(self.SelectionFrame)
            self.clear_frame(self.Confirm_SelectionFrame)
            
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, secs=0):
                    Thread.__init__(self)  # Override the __init__
                    self.secs = secs
                    self.i_waited_for_this = ""

                def run(self):
                    global pb_flag  # this tells the progress bar to stop
                    formats = []
                    for subdir, dirs, files in os.walk(rootdir):
                        for file in files:
                            try:
                                video_formats = ('mkv','webp','mp4','mka','txt')
                                if file.endswith(video_formats):
                                    if re.match(r".*\[.*\].*",file):
                                        pass
                                # link.rsplit(".",1)[1]
                                    old_file_path = os.path.join(subdir, file)
                                    file = file.replace("[NinjinAnime] ","")
                                    file = file.replace("[NinjinAnime]","")
                                    file = file.replace("(1080p Mkv BD-Rip)","")
                                    file = file.replace(" (1080p Mkv)","")
                                    new_path = os.path.join(subdir, file)
                                    # os.rename(old_file_path,new_path)
                            except:
                                pass

                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
                    
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    self.pb_root = Tk()  # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    self.pb_text = Label(self.pb_root, text=self.text, anchor="w")

                def startup(self):
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()


            def my_function():
                global pb_flag
                pb_flag = True
                t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Renombrando archivos...")
                t2 = WaitUp(secs=5)  # pass the progress bar object
                t2.start()  # use start() instead of run() for threading module
                t1.startup()  # start the progress bar
                t2.join()  # wait for WaitUp to finish before proceeding
                t1.stop()  # destroy the progress bar object
                return t2.i_waited_for_this

            global pb_flag  # this tells the progress bar to stop
            self.quit()
            my_function()
            return
    class RENAME_ITEMS_BY_ORDER:
        def __init__(self,root,HeaderFrame,BodyFrame,FooterFrame):
            self.root = root
            self.HeaderFrame = HeaderFrame
            self.BodyFrame = BodyFrame
            self.FooterFrame = FooterFrame

            self.clear_frame(self.HeaderFrame)
            self.clear_frame(self.BodyFrame)
            self.clear_frame(self.FooterFrame)


            SelectionFrame = tk.Frame(self.BodyFrame,width=1000,highlightbackground="black",highlightthickness=0.5,padx=5)
            SelectionFrame.grid(row=1,ipady=4,padx=20)
            self.SelectionFrame = SelectionFrame
            
            Confirm_SelectionFrame = tk.Frame(self.BodyFrame)
            Confirm_SelectionFrame.grid(row=2,ipady=4)
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.SelectionFrame = SelectionFrame
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.FooterButton = FooterFrame

            SelDir = tk.StringVar()
            self.SelDir = SelDir
            
            #### LAYOUT ROOT

            #### SELECT FOLDER
            header_label1 = tk.Label(HeaderFrame, text="SELECCIONA CARPETA DONDE ESTAN LOS OBJETOS A RENOMBRAR",font=font_H1)
            header_label1.pack()
            
            # global requested_input
            # requested_input = {}
            # self.root.update_idletasks()
            # self.root.update()
            
            def select_folder():
                global fdir
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                if fdir:
                    select_folder_button.destroy()
                    self.print_selected(fdir)
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=select_folder)
                    select_folder_button2.grid(row=1)
                    Confirm_btn.grid(row=1,column=2)  
            select_folder_button = tk.Button(SelectionFrame,text="ABRIR CARPETA",command=select_folder)           
            select_folder_button.grid(row=0)
            l0 = tk.Label(SelectionFrame,  text="SELECTED FOLDER:")
            l1 = tk.Label(SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(Confirm_SelectionFrame, text="CONFIRMAR", command=self.input_baseName)
            
            # requested_input["dir"] = dir
        def print_selected(self,seldir):
                self.SelDir.set(seldir)
        def clear_frame(self,frame):
                        for widgets in frame.winfo_children():
                            widgets.destroy()
        def input_baseName(self):
            self.clear_frame(self.HeaderFrame)
            self.clear_frame(self.SelectionFrame)
            self.clear_frame(self.Confirm_SelectionFrame)

            #print("next input called")

            def retrieve_input():
                global base_name
                inputValue=textBox.get("1.0","end-1c") # Get basename str() from textbox
                base_name=inputValue # Save BaseName in global var for further use
                self.clear_frame(self.HeaderFrame)
                self.clear_frame(self.SelectionFrame)
                self.clear_frame(self.Confirm_SelectionFrame)
                self.input_confirmation() # Next Step
                #print(f"FOLDER DIR ->{fdir}")
                #print(f"Base name ->{base_name}")
                

            #print("packed")
            header_label2 = tk.Label(self.HeaderFrame, text="ESCRiBE EL NOMBRE BASE DEL ARCHIVO:",font=font_H1)
            header_label2.pack()
            #print("packed")
            textBox=tk.Text(self.SelectionFrame,height=1,width=100)
            textBox.grid(row=2)
            buttonCommit=tk.Button(self.SelectionFrame, height=1, width=10, text="Confirmar", 
                                command=retrieve_input) # Fetch User input Base name and runs next step: process_recursive()
            buttonCommit.grid(row=3)
        
        def input_confirmation(self):
            #print("entered recursive processing")

                # this tells the progress bar to stop
            #print("running")
            # old_self.root.title("Confirm action")
            HeaderFrame = self.HeaderFrame
            HeaderFrame.grid(row=0)

            SelectionFrame = self.SelectionFrame
            SelectionFrame.config(highlightthickness=0)
            SelectionFrame.grid(row=1)
            

            Confirm_SelectionFrame = self.Confirm_SelectionFrame
            Confirm_SelectionFrame.grid(row=2)

            FooterButton = self.FooterButton
            FooterButton.grid(row=3)

            #print(f"Inside Run_Custom\nFOLDER DIR ->{fdir}")
            #print(f"Base name ->{base_name}")
            
            Item_ID_appender = 1
            self.Item_ID_appender = Item_ID_appender
            first_name =""
            first_modified = ""
            last_name = ""
            last_modified = ""
            rootdir = fdir
            # confirmation_label10 = tk.Label(SelectionFrame1,  text="El nombre del primer archivo pasara de",font=font_H1)
            # confirmation_label10.grid(row=0,columnspan=3) 
            header_label1 = tk.Label(HeaderFrame, text="Confirmacion",font=font_H1)
            header_label1.grid(row=0)
            rowsFrame = tk.Frame(SelectionFrame)
            rowsFrame.pack(expand=True)
            
            table = ttk.Treeview(rowsFrame)
            table['columns'] = ('old_name', 'to', 'new_name')

            table.column("#0", width=0,  stretch=NO)
            table.column("old_name",anchor=W,stretch=YES,width=250)
            table.column("to",width=30,anchor=W,stretch=NO)
            table.column("new_name",anchor=W,stretch=YES,width=250)
            
            table.heading("#0",text="",anchor=W)
            table.heading("old_name",text="OLD NAME",anchor=CENTER)
            table.heading("to",text="",anchor=W)
            table.heading("new_name",text="NEW NAME",anchor=CENTER)
            
            import tkinter.ttk
            for subdir, dirs, files in os.walk(rootdir):
                for file in files:
                    video_formats = ('py','txt')
                    if not file.endswith(video_formats):
                        #print(file)
                        global fformat
                        fformat = file.split(".")
                        fformat = fformat[::-1]
                        fformat = fformat[0]
                        
                        old_file_path = os.path.join(subdir, file)
                        old_name = file
                        file = '{} {:02}.{}'.format(base_name,self.Item_ID_appender,fformat)
                        # print(self.Item_ID_appender)
                        # print(file)
                        new_path = os.path.join(subdir, file)
                        self.Item_ID_appender +=1


                        table.insert(parent='',index='end',iid=self.Item_ID_appender,text='',values=(old_name," -> ",file))
                    
            table.pack(fill=BOTH,expand=True)        
                    

            #print("confirm button")
            Confirm_btn = tk.Button(Confirm_SelectionFrame, text=' SI', command=self.process_renaming)
            Confirm_btn.grid(row=0,column=0)

            Confirm_btn_no = tk.Button(Confirm_SelectionFrame, text='NO', command=self.input_baseName)
            # try:
            Confirm_btn_no.grid(row=0,column=1)
            #print("after confirm")

        def process_renaming(self):
            for widgets in self.HeaderFrame.winfo_children():
                widgets.destroy()
            for widgets in self.SelectionFrame.winfo_children():
                widgets.destroy()
            for widgets in self.Confirm_SelectionFrame.winfo_children():
                widgets.destroy()
            for widgets in self.FooterButton.winfo_children():
                widgets.destroy()
            
            Previus_Total_appended = self.Item_ID_appender 
            Item_ID_appender = 1
            #print("starting countdown")
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, secs=0):
                    Thread.__init__(self)  # Override the __init__
                    self.secs = secs
                    self.i_waited_for_this = ""
                    
                    
                def run(self):
                    
                    #print("Running-base_run_thread")
                    #print(f"test dir {fdir}")
                    Item_ID_appender = 1
                    
                    for subdir, dirs, files in os.walk(fdir):
                        for file in files:
                            try:
                                video_formats = ('py','txt')
                                if not file.endswith(video_formats):
                                    old_file_path = os.path.join(subdir, file)
                                    old_name = file
                                    file = '{} {:02}.{}'.format(base_name,Item_ID_appender,fformat)
                                    new_path = os.path.join(subdir, file)
                                    label_progress_text.set(f"{old_name} -> {file} -> {Item_ID_appender} / {Previus_Total_appended}    -    {round(Item_ID_appender/Previus_Total_appended*100,0)}%")
                                    #print(file)
                                    os.rename(old_file_path,new_path)
                                    Item_ID_appender +=1
                            except Exception as e:
                                print("e")
                                pass
                        # break 
                    global pb_flag


                    pb_flag = False

                    ##print("Done")
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass

                        
                        # except:pass

                        # button = tk.Button(Confirm_SelectionFrame, text = 'NO', command=self.quit)
                        # button.grid(row=0,column=1)
                        # quit_button = tk.Button(Footer, text = 'Salir', command=self.old_self.quit)
                        # quit_button.grid(row=2)
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    global label_progress_text
                    label_progress_text = tk.StringVar()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text
                    

                def startup(self):
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    
                    self.pb_text = Label(self.pb_root, textvariable=self.label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            def my_function():
                global pb_flag
                global ready
                global t1
                global t2
                
                
                ready = False
                t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Renombrando archivos...")
                t2 = WaitUp(secs=5)  # pass the progress bar object
                t2.start()  # use start() instead of run() for threading module
                t1.startup()  # start the progress bar
                t2.join()  # wait for WaitUp to finish before proceeding
                t1.stop()  # destroy the progress bar object
                return t1.return_msg

            global pb_flag  # this tells the progress bar to stop
            pb_flag = True
            
            my_function()
            

        def quit(self):
            self.root.destroy()
        def donothing(self):
            # print ('IT WORKED')
            pass
            # def quit(self):
            #     self.root.destroy()
    class FolderFileExtractor:
        def __init__(self,root,HeaderFrame,BodyFrame,FooterFrame):
            self.root = root
            self.HeaderFrame = HeaderFrame
            self.BodyFrame = BodyFrame
            self.FooterFrame = FooterFrame

            self.clear_frame(self.HeaderFrame)
            self.clear_frame(self.BodyFrame)
            self.clear_frame(self.FooterFrame)


            SelectionFrame = tk.Frame(self.BodyFrame,width=1000,highlightbackground="black",highlightthickness=0.5,padx=5)
            SelectionFrame.grid(row=1,ipady=4,padx=20)
            self.SelectionFrame = SelectionFrame
            
            Confirm_SelectionFrame = tk.Frame(self.BodyFrame)
            Confirm_SelectionFrame.grid(row=2,ipady=4)
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.SelectionFrame = SelectionFrame
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.FooterButton = FooterFrame

            SelDir = tk.StringVar()
            self.SelDir = SelDir
            
            Sel_To_Dir = tk.StringVar()
            self.Sel_To_Dir = Sel_To_Dir
            
            #### LAYOUT ROOT

            #### SELECT FOLDER
            
            print("init folderfile extractor")
            self.input_1_From_folder()
            

        def input_1_From_folder(self):
            header_label1 = tk.Label(self.HeaderFrame, text="SELECCIONA CARPETA DONDE ESTAN LOS SUBCARPETAS A EXTRAER EN UNA",font=font_H1)
            header_label1.pack()
            def select_folder(Event=None):
                global fdir
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                if fdir:
                    select_folder_button.destroy()
                    self.SelDir.set(fdir) 
                    self.fdir = fdir
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=select_folder)
                    select_folder_button2.grid(row=1)
                    self.root.bind('<Return>', self.input_2_TO_folder)
                    Confirm_btn.grid(row=1,column=2)  
            self.root.bind('<Return>', select_folder)
            select_folder_button = tk.Button(self.SelectionFrame,text="ABRIR CARPETA",command=select_folder)           
            select_folder_button.grid(row=0)
            l0 = tk.Label(self.SelectionFrame,  text="CARPETA SELECCIONADA")
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.input_2_TO_folder)
            # requested_input["dir"] = dir
        
        def input_2_TO_folder(self,Event=None):
            self.clear_all_frames()
            header_label1 = tk.Label(self.HeaderFrame, text="SELECCIONA CARPETA DONDE QUIERES GUARDAR LOS ARCHIVOS EXTRAIDOS",font=font_H1)
            header_label1.pack()

            def select_folder(Event=None):
                global new_path_destiny
                if launch_path:
                    new_path_destiny = filedialog.askdirectory(initialdir=launch_path)
                else:
                    new_path_destiny = filedialog.askdirectory()
                if new_path_destiny:
                    select_folder_button.destroy()
                    self.Sel_To_Dir.set(new_path_destiny)       

                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=select_folder)
                    select_folder_button2.grid(row=1)
                    self.root.bind('<Return>', self.process_extractor)
                    Confirm_btn.grid(row=1,column=2)  
            self.root.bind('<Return>', select_folder)
            select_folder_button = tk.Button(self.SelectionFrame,text="ABRIR CARPETA",command=select_folder)           
            select_folder_button.grid(row=0)
            l0 = tk.Label(self.SelectionFrame,  text="CARPETA SELECCIONADA")
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.process_extractor)

            



        # print('NEW path:\n C:\\Users\\galla\\Google Drive\\Programacion\\Python\\FOLDER_FILE_EXTRACTOR\\new_path_files')
        # formats = []
        def process_extractor(self,Event=None):
            self.clear_all_frames()
            # button = Button(self.Confirm_SelectionFrame, text="CONTINUAR", command=input_format)
            # button.grid(row=2)
            # def extract_files(self,format_list = None):
            #     self.clear_all_frames()
                


                
                #THIS EXTRACTS FILES FROM ./FOLDER1/FILES OR /FOLDER2/FILES TO SPECIFIED FOLDER
            def include(Includes):
                pass
                    # global fdir
                    # print(fdir)
                    # for subdir, dirs, files in os.walk(fdir):
                    #     print(subdir)
                    #     print(dirs)
                    #     print(files)
                    #     print("\n\n\n")
                    #     for file in files:
                            
                    #         print(file)
                    #         print("\n")
                    #         try:
                    #             if not Includes or Includes == "*":
                    #                 print("NO includes everything counts")
                    #                 # if file.endswith(include_formats):
                    #                 old_file_path = os.path.join(subdir, file)
                    #                 new_path = os.path.join(new_path_destiny, file)
                    #                 print("OLD",old_file_path)
                    #                 print("NEW",new_path_destiny,"\n")
                    #             if file.endswith(Includes):
                    #                 print("ends with included file")
                    #                 # if file.endswith(include_formats):
                    #                 old_file_path = os.path.join(subdir, file)
                    #                 new_path = os.path.join(new_path_destiny, file)
                    #                 print("OLD",old_file_path)
                    #                 print("NEW",new_path_destiny,"\n")
                    #             # os.rename(old_file_path,new_path)

                                
                    #         except Exception as e:
                                

                    #             print(e,"\n\n\n")
            def extract_all():
                SelectionFrame = self.SelectionFrame
                SelectionFrame.config(highlightthickness=0)
                SelectionFrame.grid(row=1)
                self.clear_all_frames()
                self.clear_frame(self.FooterButton)
                global fdir
                print(fdir)
                isfile = os.path.isfile
                join = os.path.join
                number_of_files = sum([len(files) for r, d, files in os.walk(fdir)])
                # number_of_files = sum(1 for item in os.listdir(fdir) if isfile(join(fdir, item)))
                print(f"NUMBER OF FILESS {number_of_files}")
                # input("xconritunre")
                class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                    def __init__(self, secs=0):
                        Thread.__init__(self)  # Override the __init__
                        self.secs = secs
                        self.i_waited_for_this = ""
                        
                        
                    def run(self):
                        
                        #print("Running-base_run_thread")
                        #print(f"test dir {fdir}")
                        Item_ID_appender = 1
                        for subdir, dirs, files in os.walk(fdir):
                            # print(subdir)
                            # print(dirs)
                            # print(files)
                            # print("\n\n\n")
                            # for file in files:
                            #     print(f"file in subdir:{subdir} file:{file}")
                            #     print(f"file in subdir:{dirs} file:{file}")
                            for file in files:
                                
                                print(file)
                                print("\n")
                                try:

                                    label_progress_text.set(f"{file} -> {Item_ID_appender} / {number_of_files}    -    {round(Item_ID_appender/number_of_files*100,0)}%")
                                    
                                    old_file_path = os.path.join(subdir, file)
                                    new_path = os.path.join(new_path_destiny, file)
                                    print("OLD",old_file_path)
                                    print("NEW",new_path,"\n")
                                    Item_ID_appender+=1
                                    os.rename(old_file_path,new_path)

                                    
                                except Exception as e:
                                    

                                    print(e,"\n\n\n")
                        global pb_flag


                        pb_flag = False

                        ##print("Done")
                        self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass

                            
                            # except:pass

                            # button = tk.Button(Confirm_SelectionFrame, text = 'NO', command=self.quit)
                            # button.grid(row=0,column=1)
                            # quit_button = tk.Button(Footer, text = 'Salir', command=self.old_self.quit)
                            # quit_button.grid(row=2)
                class ProgressBarIn:
                    def __init__(self, title="", label="", text=""):
                        self.title = title  # Build the progress bar
                        self.label = label
                        self.text = text
                        global label_progress_text
                        label_progress_text = tk.StringVar()
                        label_progress_text.set(text)
                        self.label_progress_text = label_progress_text
                        

                    def startup(self):
                        for widgets in root.winfo_children():
                            widgets.destroy()
                        self.pb_root = root # create a window for the progress bar
                        self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                        self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                        
                        self.pb_text = Label(self.pb_root, textvariable=self.label_progress_text, anchor="w")
                        self.pb.start()
                        self.pb_root.title(self.title)
                        self.pb_label.grid(row=0, column=0, sticky="w")
                        self.pb.grid(row=1, column=0, sticky="w")
                        self.pb_text.grid(row=2, column=0, sticky="w")
                        while pb_flag == True:  # move the progress bar until multithread reaches line 19
                            self.pb_root.update()
                            self.pb['value'] += 1
                            #print(self.pb['value'])
                            time.sleep(.1)

                    def stop(self):
                        self.pb.stop()  # stop and destroy the progress bar
                        self.pb_label.destroy()  # destroy the label for the progress bar
                        self.pb.destroy()
                        self.pb_root.destroy()
                        self.return_msg = "back to menu"
                        return 
                def my_function():
                    global pb_flag
                    global ready
                    global t1
                    global t2
                    
                    
                    ready = False
                    t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Renombrando archivos...")
                    t2 = WaitUp(secs=5)  # pass the progress bar object
                    t2.start()  # use start() instead of run() for threading module
                    t1.startup()  # start the progress bar
                    t2.join()  # wait for WaitUp to finish before proceeding
                    t1.stop()  # destroy the progress bar object
                    return t1.return_msg

                global pb_flag  # this tells the progress bar to stop
                pb_flag = True
                
                my_function()
    
            def exclude():
                pass
                    # for subdir, dirs, files in os.walk(self.fdir):
                    #     print(subdir)
                    #     print(dirs)
                    #     print(files)
                    #     print("\n\n\n")
                    #     for file in files:
                            
                    #         print(file)
                    #         print("\n")
                    #         try:
                    #             if not file.endswith(exclude_formats):
                    #             # if file.endswith(include_formats):
                    #                 old_file_path = os.path.join(subdir, file)
                    #                 new_path = os.path.join(new_path_destiny, file)
                    #                 print("OLD",old_file_path)
                    #                 print("NEW",new_path_destiny,"\n")
                    #                 # os.rename(old_file_path,new_path)
                    #             exclude_formats = ('json','py')
                    #             include_formats = ('mp4')
                                
                    #         except Exception as e:
                    #             print(e,"\n\n\n")
                # Confirm_btn = tk.Button(self.SelectionFrame, text="EXCLUIR EXTENSIONES", command=include)
            def input_format():
                def input_confirm_format():
                    print(self.input1_format)
                    l0 = tk.Label(self.SelectionFrame,  text=f"LAS EXTENSIONES {self.input1_format} SERAN:")
                    l0.grid(row=0)
                    # l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
                    button1 = Button(self.Confirm_SelectionFrame, text="INCLUIDAS", command=include)
                    button2 = Button(self.Confirm_SelectionFrame, text="EXCLUIDAS", command=exclude)
                    button3 = Button(self.Confirm_SelectionFrame, text="REINTENTAR", command=self.process_extractor)
                    button1.grid(row=0,column=0)
                    button2.grid(row=0,column=1)
                    button3.grid(row=1)
                self.input1_format = Entry.get().replace(" ","").split(",")
                input_confirm_format()
                
            header_label1 = tk.Label(self.HeaderFrame, text="INDICA FORMATO DE ARCHIVOS A EXTRAER O INCLUIR.",font=font_H1)
            header_label1.pack()
            # entry = Entry(self.SelectionFrame)
            # entry.grid(row=0,column=0)

            
            # button1 = Button(self.SelectionFrame, text="Insertar", command=input_format)
            button4 = Button(self.SelectionFrame, text="TODOS LOS ARCHIVOS", command=extract_all)
            button4.grid(row=0,column=1)
            
            
            



        def clear_all_frames(self):
            self.clear_frame(self.HeaderFrame)
            self.clear_frame(self.SelectionFrame)
            self.clear_frame(self.Confirm_SelectionFrame)
            # self.clear_frame(self.FooterButton)

        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
    class ImageOrganizer_Date:
        def __init__(self,root):
            # HeaderFrame,SelectionFrame,Confirm_SelectionFrame,FooterButton
            for widgets in root.winfo_children():
                widgets.destroy()
                
            self.root = root
            self.contentFrame = tk.Frame(root,width=1000,)#,highlightbackground="black",highlightthickness=0.5,padx=5
            self.ExitFrame = tk.Frame(root)
            self.ExitFrame.grid(row=1)
            quit_button = tk.Button(self.ExitFrame, text = 'Salir', command=self.quit)
            quit_button.grid(row=0)
            self.contentFrame.grid(row=0)

            self.HeaderFrame = tk.Frame(self.contentFrame)
            self.BodyFrame = tk.Frame(self.contentFrame)
            self.FooterButton = tk.Frame(self.contentFrame)

            

            self.HeaderFrame.grid(row=0)
            self.BodyFrame.grid(row=1,padx=20)
            self.FooterButton.grid(row=2)
            
            
            SelectionFrame = tk.Frame(self.BodyFrame,width=1000,highlightbackground="black",highlightthickness=0.5,padx=5)
            self.SelectionFrame = SelectionFrame
            self.SelectionFrame.grid(row=0)

            Confirm_SelectionFrame = tk.Frame(self.BodyFrame)
            self.Confirm_SelectionFrame = Confirm_SelectionFrame
            self.Confirm_SelectionFrame.grid(row=1)
            

            
            SelDir = tk.StringVar()
            self.SelDir = SelDir
            import os
            import re
            from datetime import datetime
        
            self.select_folder()
        def quit(self):
            self.root.destroy()
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
        def select_folder(self):
            global fdir
            def select_folder(Event=None):
                global fdir
                
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                if fdir:
                    self.fdir = fdir
                    select_folder_button.destroy()
                    #print selected:
                    self.SelDir.set(fdir)
                    
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=select_folder)
                    select_folder_button2.grid(row=1,column=0)
                    self.root.bind('<Return>', self.start_processing)
                    Confirm_btn.grid(row=1,column=1)

            self.root.bind('<Return>', select_folder)
            select_folder_button = tk.Button(self.SelectionFrame,text="ABRIR CARPETA",command=select_folder)
            
            select_folder_button.grid(row=0)
            l0 = tk.Label(self.SelectionFrame,  text="SELECTED FOLDER:")
            
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            self.checkbox_custom_String_pattern = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.SelectionFrame, text="Especificar cadena de texto patrón",variable=self.checkbox_custom_String_pattern)
            checkbox.grid(row=2)
            
            
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.start_processing)
            # #print(fdir)
        def start_processign_file_name_date(self) :
            pass

        def start_processing(self,event=None):
            for widgets in self.BodyFrame.winfo_children():
                widgets.destroy()
            global pb_flag  # this tells the progress bar to stop
            pb_flag = True
            # 
                # print(self.checkbox_custom_String_pattern.get())
                # if self.checkbox_custom_String_pattern.get():
                #     pass
                #     custom_string_text_year_label = tk.Label(self.BodyFrame,  text="Copy paste everything before the year on the next field.Then everything after it. Example: 'VID- '2020 '0106-WA0026'")
                #     custom_string_text_year_label.grid(row=0)

                #     custom_string_text_year_pre = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_year_pre.grid(row=1,column=0)

                #     custom_string_text_year_after = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_year_after.grid(row=1,column=1)
                #     year = 
                #     ################################################################################################
                #     custom_string_text_month_label = tk.Label(self.BodyFrame,  text="Copy paste everything before the year on the next field.Then everything after it. Example: 'VID-2020' 01 '06-WA0026'")
                #     custom_string_text_month_label.grid(row=2)

                #     custom_string_text_month_pre = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_month_pre.grid(row=1,column=0)

                #     custom_string_text_month_after = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_month_after.grid(row=1,column=1)
                #     ################################################################################################
                #     custom_string_text_day_label = tk.Label(self.BodyFrame,  text="Copy paste everything before the year on the next field.Then everything after it. Example: 'VID-202001' 06 '-WA0026'")
                #     custom_string_text_day_label.grid(row=2)

                #     custom_string_text_day_pre = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_day_pre.grid(row=1,column=0)

                #     custom_string_text_day_after = tk.Text(self.BodyFrame,height=1)
                #     custom_string_text_day_after.grid(row=1,column=1)
                    
    
                #     Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.start_processing)
                #     Confirm_btn.grid(row=1)

            self.my_function()
        def my_function(self):
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, secs=0):
                    Thread.__init__(self)  # Override the __init__
                    self.secs = secs
                    self.i_waited_for_this = ""
                    
                    
                def run(self):
                    def procesa_path():
                        input_date = "yes"
                        path = fdir
                        print(path)
                        if not re.match(r"(?i)yes|si|s|y",input_date):
                            folders_to_create = ["01_enero","02_febrero","03_marzo", "04_abril","05_mayo","06_junio","07_julio","08_agosto","09_septiembre","10_octubre","11_noviembre","12_diciembre"]
                        
                            os.chdir(path)
                            pattern_image = r"Photo [0-9]*-[0-9]*-[0-9]*.*"
                            root_scan = []
                            for root in os.walk(path):
                                root_scan.append(root)
                            folders_scan = root_scan[0][1]
                            files_scan = root_scan[0][2]
                            images = []
                            for item in files_scan:
                                if re.match(pattern_image,item):
                                    images.append(item)
                            for image in images:
                                
                                f = image
                                f = f.split(" ")
                                f_name = f[0]
                                f_date = f[1].split(",")[0]
                                f_date = f_date.split("-")
                                f_day = f_date[0]
                                f_month = f_date[1]
                                f_year = f_date[2]
                                f_month = int(f_month)
                                f_month -= 1
                                global label_progress_text
                                label_progress_text.set(f"Procesando imagen:{f_name}")
                                print(f_name)
                                if f_year in folders_scan:
                                    # print(image)
                                    # print("{} .\\{}\\{}\\{}".format(image,f_year,folders_to_create[f_month],image))
                                    os.makedirs(".\\{}\\{}".format(f_year,folders_to_create[f_month]),exist_ok=True)
                                    os.system('move "{}" ".\\{}\\{}\\{}"'.format(image,f_year,folders_to_create[f_month],image))
                                else:
                                    os.makedirs(f_year)
                                    for folder in folders_to_create:
                                        os.system('cd {}'.format(f_year))
                                        os.system('mkdir {}'.format(f_year + "\\" + folder))
                                    # print(image)
                                    os.system('move "{}" ".\\{}\\{}\\{}"'.format(image,f_year,folders_to_create[f_month],image))
                                    folders_scan.append(f_year)
                                delete_folders_scan = []
                                for root in os.walk(path):
                                    delete_folders_scan.append(root)
                                for folder in delete_folders_scan:
                                    if len(folder[1]) == 0 and len(folder[2]) == 0:
                                        os.rmdir(folder[0])
                                    else:pass
                                print("La operacion ha finalizado")
                        else:

                            # print("else")
                            folders_to_create = ["01_enero","02_febrero","03_marzo", "04_abril","05_mayo","06_junio","07_julio","08_agosto","09_septiembre","10_octubre","11_noviembre","12_diciembre"]
                            os.chdir(path)
                            
                            root_scan = []
                            for root in os.walk(path):
                                root_scan.append(root)
                            folders_scan = root_scan[0][1]
                            files_scan = root_scan[0][2]
                            images = []
                            number_of_files = sum([len(files) for r, d, files in os.walk(fdir)])
                            # number_of_files = sum(1 for item in os.listdir(fdir) if isfile(join(fdir, item)))
                            Item_ID_appender = 1
                            print(f"NUMBER OF FILESS {number_of_files}")
                            for item in files_scan:
                                if item.endswith(".py") or item.endswith(".db"):
                                    continue
                                # print(item)
                                img_path = "{}\\{}".format(path.replace("/","\\\\"),item)
                                # print(img_path)
                                try:
                                    S_date = self.imgdate().ImageDate(img_path)
                                    # print(S_date = self.imgdate().ImageDate(img_path))
                                    # self.imgdate
                                
                                except Exception as e:
                                    print(e)
                                    S_date = None
                                # os.system("pause")
                                # return
                                c_time = os.path.getctime(item)
                                m_time = os.path.getmtime(item)
                                # print(f"ctime:{c_time}\nmtime:{m_time}\nsdate:{S_date}")
                                # S_time = os.path.getatime(item)
                                if S_date:
                                    time = S_date
                                    # print("S_date",S_date)
                                else:
                                    # print(c_time)
                                    # print(datetime.fromtimestamp(c_time))
                                    # print(m_time)
                                    # print(datetime.fromtimestamp(m_time))
                                    # os.system("pause")
                                    # return
                                    if c_time >= m_time:
                                        time = m_time
                                        time = datetime.fromtimestamp(time)
                                    else:
                                        time = c_time
                                        time = datetime.fromtimestamp(time)
                                time = str(time)
                                # print("Final_time",time,"\n")
                                time  = time.split(" ")[0].split("-")
                                time_year = time[0]
                                time_month = str(int(time[1]) -1)
                                time_day = time[2]
                                # print("year",time_year)
                                # print("month",time_month)
                                # print("day",time_day)
                                # input("CONTINUE")
                                image = item
                                if not str(time_year) in folders_scan:
                                    os.makedirs(time_year)
                                    folders_scan.append(time_year)
                                if str(time_year) in folders_scan:
                                    os.makedirs(".\\{}\\{}".format(time_year,folders_to_create[int(time_month)]),exist_ok=True)
                                    os.system('move "{}" ".\\{}\\{}\\{}"'.format(image,time_year,folders_to_create[int(time_month)],image))

                                try:
                                    
                                    label_progress_text.set(f"{image} -> {Item_ID_appender} / {number_of_files}    -    {round(Item_ID_appender/number_of_files*100,0)}%")
                                    Item_ID_appender+=1
                                except Exception as e:
                                    print(e,"\n\n\n")

                    procesa_path()
                    time.sleep(5)


                    global pb_flag


                    pb_flag = False

                    ##print("Done")
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass

                        
                        # except:pass

                        # button = tk.Button(Confirm_SelectionFrame, text = 'NO', command=self.quit)
                        # button.grid(row=0,column=1)
                        # quit_button = tk.Button(Footer, text = 'Salir', command=self.old_self.quit)
                        # quit_button.grid(row=2)
                class imgdate():
                    def __init__(self):
                        from datetime import datetime
                        self.datetime = datetime
                        from PIL import Image
                        self.Image = Image
                        from PIL.ExifTags import TAGS
                        self.TAGS = TAGS
                    def get_exif(self,fn):
                        ret = {}
                        i = self.Image.open(fn)
                        info = i._getexif()
                        # print(info)
                        for tag, value in info.items():
                            decoded = self.TAGS.get(tag, tag)
                            ret[decoded] = value
                        return ret
                    def ImageDate(self,fn):
                        "Returns the date and time from image(if available)\nfrom Orthallelous"
                        TTags = [('DateTimeOriginal', 'SubsecTimeOriginal'),  # when img taken
                        ('DateTimeDigitized', 'SubsecTimeDigitized'),  # when img stored digitally
                        ('DateTime', 'SubsecTime')]  # when img file was changed
                        # for subsecond prec, see doi.org/10.3189/2013JoG12J126 , sect. 2.2, 2.3
                        exif = self.get_exif(fn)
                        for i in TTags:
                            # print(i)
                            dat, sub = exif.get(i[0]), exif.get(i[1], 0)
                            dat = dat[0] if type(dat) == tuple else dat  # PILLOW 3.0 returns tuples now
                            sub = sub[0] if type(sub) == tuple else sub
                            if dat != None: break  # got valid time
                        # input()
                        if dat == None: return  # found no time tags
                        T = self.datetime.strptime('{}.{}'.format(dat, sub), '%Y:%m:%d %H:%M:%S.%f')
                        #T = time.mktime(time.strptime(dat, '%Y:%m:%d %H:%M:%S')) + float('0.%s' % sub)
                        return T
            

            
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    global label_progress_text
                    label_progress_text = tk.StringVar()
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text
                    

                def startup(self):
                    global label_progress_text
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            global ready
            global t1
            global t2
            self.clear_frame(root)
            
            ready = False
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Procesando archivos...")
            t2 = WaitUp(secs=5)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg
    class DirectLinkDownload:
        def __init__(self,root,HeaderFrame,SelectionFrame,Confirm_SelectionFrame,FooterButton):
            
            
            for widgets in root.winfo_children():
                widgets.destroy()
            self.root = root
            self.contentFrame = tk.Frame(root,width=1000,)#,highlightbackground="black",highlightthickness=0.5,padx=5
            self.ExitFrame = tk.Frame(root)
            self.ExitFrame.grid(row=1)
            quit_button = tk.Button(self.ExitFrame, text = 'Salir', command=self.quit)
            quit_button.grid(row=0)
            
            self.HeaderFrame = tk.Frame(self.contentFrame)
            self.BodyFrame = tk.Frame(self.contentFrame)
            self.FooterButton = tk.Frame(self.contentFrame)
            self.HeaderFrame.grid(row=0)
            self.BodyFrame.grid(row=1,padx=20)
            self.FooterButton.grid(row=2)
            self.contentFrame.grid(row=0)

            
            
            SelDir = tk.StringVar()
            self.SelDir = SelDir
            import os
            import re
            from datetime import datetime
        
            self.select_folder()
        def quit(self):
            self.root.destroy()
        
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()

        def select_folder(self):
            global fdir
            
            def pselect_folder(event=None):
                print("inside pselect")
                global fdir
                
                self.root.unbind('<Return>')
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                
                if fdir:
                    print(fdir)
                    self.fdir = fdir
                    select_folder_button.destroy()
                    #print selected:
                    self.SelDir.set(fdir)
                    
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=pselect_folder)
                    select_folder_button2.grid(row=1,column=0)
                    
                    Confirm_btn.grid(row=1,column=1)
                self.root.bind('<Return>', self.add_direct_links)
                    
            self.SelectionFrame = Frame(self.BodyFrame)
            self.SelectionFrame.grid(row=0)
            self.Confirm_SelectionFrame = Frame(self.BodyFrame)
            self.Confirm_SelectionFrame.grid(row=1)
            self.urls = []
            select_folder_button = tk.Button(self.SelectionFrame,text="SELECCIONAR CARPETA DE DESCARGA",command=pselect_folder)
            select_folder_button.grid(row=0)
            self.root.bind('<Return>', pselect_folder)
            
            l0 = tk.Label(self.SelectionFrame,  text="CARPETA SELECCIONADA:")
            
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.add_direct_links)
            
            # Confirm_btn.bind('<Return>', self.add_direct_links)
            # #print(fdir)

            # print("""Instructions:
            # 1. Are you going to download from multiple links?
            # 2. Base name of the file to rename. This is: NEW_FILE_LOCATION + \\ + final name (AUTO ADDS ->appended 0N)
            # 3. Format of the file you are downloading

            # 1.2 If there are multiple links paste them one by one + Enter

            # """)
            # bulk_download = input("Bulk link download?")
            # multiple = input("Multiple downloads? >")
            # base_name = input("base_name_00n >")
            # fformat = input("Format >")
            #https://descarga-directa.fukou-da.net/0:/Anime/D/Death%20Note/%5BWZF%5DDeath_Note_Capitulo_01%5BTVRip%5D%5Bx264-AAC%5D%5B848x480%5D%5BSub-Esp%5D.avi
            
            id = 0
            adding = True

            # if bulk_download == "yes" or multiple == "y":
            #     bulk_links = input("bulk links (separated by \n\n) >")
            #     for link_url in bulk_links.split("\n\n"):
            #         urls.append(link_url)
            # else:
            
        def add_direct_links(self,event=None):
            self.clear_frame(self.BodyFrame)
            try:
                self.buttonBack.grid_forget()
                #TODO THE BUTTON ABOVE LEAVES A BAD SPACE
            except:
                pass
            
            
            # print(f"inside add_direct_link")
            

            # def delete():
                
            # def func(event):
            #     print("You hit return.")
                
            # def onclick(event=None):
            #     print("You clicked the button")
            #     inputValue=textBox.get("1.0","end-1c") # Get basename str() from textbox

                # self.urls.append(url)
                # add_label = 

            # root.bind('<Return>', onclick)
            # def retrieve_input():
                # global base_name
                # inputValue=textBox.get("1.0","end-1c") # Get basename str() from textbox
                # base_name=inputValue # Save BaseName in global var for further use
                # textBox=tk.Text(self.TagFrame,height=1,width=100)
                # textBox.insert(tk.END,base_name)
            def del_entry(btn):
                print(btn)
                if isinstance(self.entry_rows[int(btn)],Entry):
                    self.entry_rows[int(btn)].delete('0',tk.END)
                else:
                    self.entry_rows[int(btn)][0].grid_forget()
                    self.entry_rows[int(btn)][1].grid_forget()
                    self.entry_rows[int(btn)] = None
                    self.url_list[btn] = None
                # for i in len(frame.winfo_children())
                
                    # print(widgets.get(".!frame5.!frame2.!entry2"))
                    # for widget in widgets:
                    #     print(widget)
                    #     print(f'has value "{widgets.get(widget)}"')
                # for widget in self.winfo_children():
                #     for i, subwidget in enumerate(widget.winfo_children()):
                #         if isinstance(subwidget, tk.Entry):
                #             print(f'child {i} of widget', subwidget.get())
                # for widgets in frame.winfo_children():
                #     # for widget in widgets:
                #     #     if 
                #     print(widgets)
                #     try:
                #         print(widgets.get("frame5"))
                #     except:
                #         print("no")
                #     try:
                #         print(widgets.get(".!frame2"))
                #     except:
                #         print("no")

            def add_entry(event=None):
                if isinstance(self.textBox,Entry):
                    self.url_list.append(self.textBox.get())
                else:
                    self.url_list.append(self.textBox.get())
                # global root, n_array
                self.row_n_id +=1
                
                # n_array.append(row_array)
                # y=len(n_array)           
                
                
                self.textBox=Entry(self.listFrame,textvariable=self.var)
                self.textBox.grid(row=self.row_n_id,column=0)
                self.textBox.focus()
                
                delete_entry = tk.Button(self.listFrame,text="Eliminar",command=partial(del_entry,self.row_n_id))
                delete_entry.grid(row=self.row_n_id,column=1)
                
                self.entry_rows.append([self.textBox,delete_entry])
                # row_array.append(tbn)
                # tb
                # row_array[x].grid(row=y, column=x,sticky="nsew", padx=2,pady=2)
                # new_textBox = tk.Text(self.SelectionFrame,height=1,width=100)
            def bulkInput():
                def load_bulk():
                    input_bulk= textBox.get("1.0","end-1c")
                    url_bulk = []
                    for url in input_bulk.split("\n"):
                        if url:
                            # print(url)
                            self.url_list.append(url)
                    self.textBox = self.url_list
                    self.start_processing()
                self.clear_frame(self.BodyFrame)
                # buttonBulk_input=tk.Button(self.BodyFrame, text="Multiple lista separada por \\n",command=bulkInput)
                textBox=tk.Text(self.BodyFrame,height=20,width=200)
                textBox.focus()
                textBox.grid(row=0)

                self.buttonBack =tk.Button(self.FooterButton, text="Atras",command=self.add_direct_links)
                self.buttonBack.grid(row=1,column=1)
                self.buttonBack =tk.Button(self.FooterButton, text="Continuar",command=load_bulk)
                self.buttonBack.grid(row=1,column=1)
                
            # RETRIEVE TEX BOXES
            # for col in range(4):
                # print(n_array[row][col].get())
                 
                #print(f"FOLDER DIR ->{fdir}")
                #print(f"Base name ->{base_name}")
            self.entry_rows = []
            self.row_n_id = 0
            lbl = Label(self.HeaderFrame,text="INPUT URLS")
            self.listFrame = Frame(self.BodyFrame)
            self.listFrame.grid(row=0)
            self.var = StringVar
            self.textBox=Entry(self.listFrame,textvariable=self.var)
            
            self.textBox.grid(row=self.row_n_id,column=0)
            self.textBox.focus()
            self.root.bind('<Return>', add_entry)
            self.entry_rows.append(self.textBox)
            delete_entry = tk.Button(self.listFrame,text="Eliminar",command=partial(del_entry,self.row_n_id))
            delete_entry.grid(row=self.row_n_id,column=1)
            self.url_list = []

            buttonBulk_input=tk.Button(self.BodyFrame, text="Introducir multiples URL",command=bulkInput)
            buttonBulk_input.grid(row=3,column=0)
            
            buttonCommit=tk.Button(self.BodyFrame, height=1, width=10, text="Confirmar",command=self.start_processing) # Fetch User input Base name and runs next step: process_recursive()
            buttonCommit.grid(row=3,column=1)






            # BackSpace
            # button = tk.Button(root, text="Enter", command=onclick)
            # button.bind('<Button-1>', onclick)
            # button.pack()





            # if multiple == "yes" or multiple == "y":
            #     while adding == True:
            #         url = input(f"url-{id}")
            #         if "done" in url:
            #             adding = False
            #             continue
            #         id+=1
            #         self.urls.append(url)
            
            # print(self.urls)
            # print("Starting_Requests")
        
        def start_processing(self):
            if isinstance(self.textBox,Entry):
                self.url_list.append(self.textBox.get())
            elif isinstance(self.textBox,list):
                pass
            else:
                self.url_list.append(self.textBox.get())
            for widgets in self.contentFrame.winfo_children():
                widgets.destroy()
            global pb_flag  # this tells the progress bar to stop
            pb_flag = True
            
            self.my_function()


        def my_function(self):
            print("inside myfunc")
            self.clear_frame(root)
            print(self.url_list)
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, ulrs):
                    Thread.__init__(self)  # Override the __init__
                    
                    self.i_waited_for_this = ""
                    self.urls = ulrs
                    
                    
                def run(self):
                    def procesa(self):
                        import requests
                        urln = 0
                        last_url = None
                        for url in self.urls:
                            try:
                                urln +=1
                                try:
                                    last_url = base_name
                                except:
                                    pass

                                
                                
                                base_name = url.split("/")
                                base_name = base_name[-1]
                                if "." not in base_name:
                                    raise Exception
                                fformat = base_name.split(".")
                                fformat = fformat[::-1]
                                fformat = fformat[0]
                                base_name = base_name.replace(fformat,"")
                                base_name = base_name.replace(".","_")
                                # file_name = '{}\\{} {:02}.{}'.format(fdir.replace("/","\\"),base_name,urln,fformat)
                                file_name = '{}\\{}.{}'.format(fdir.replace("/","\\"),base_name,fformat)
                                print(f"Requesting {file_name}")
                                global label_progress_text
                                
                                label_progress_text.set(f"Descargando archivos...  {urln}/{len(self.urls)} | {last_url} Completado")
                                 
                                r = requests.get(url)
                                print(f"Saving {file_name}")
                                with open(file_name,'wb') as outfile:
                                    outfile.write(r.content)
                                print(f"Done {file_name}")
                            
                            except Exception as e:
                                
                                print(f"error: {url}\n{e}")
                                continue

                    procesa(self)
                    time.sleep(5)
                        # print(f"file {urln}")
                        # time.sleep(20)


                    global pb_flag


                    pb_flag = False

                    ##print("Done")
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass

                        
                        # except:pass

                        # button = tk.Button(Confirm_SelectionFrame, text = 'NO', command=self.quit)
                        # button.grid(row=0,column=1)
                        # quit_button = tk.Button(Footer, text = 'Salir', command=self.old_self.quit)
                        # quit_button.grid(row=2)

            
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    
                    
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Descargando archivos...")
            t2 = WaitUp(self.url_list)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg
    class RedditDownloader:
        def __init__(self,root):
            
            for widgets in root.winfo_children():
                widgets.destroy()
            self.root = root
            #Initialize Window
            self.contentFrame = tk.Frame(self.root,width=1000,)#,highlightbackground="black",highlightthickness=0.5,padx=5
            self.contentFrame.grid(row=0)
            self.ExitFrame = tk.Frame(self.root)
            self.ExitFrame.grid(row=1)
            quit_button = tk.Button(self.ExitFrame, text = 'Salir', command=self.quit)
            quit_button.grid(row=0)

            self.HeaderFrame = tk.Frame(self.contentFrame)
            self.HeaderFrame.grid(row=0)
            self.BodyFrame = tk.Frame(self.contentFrame)
            self.BodyFrame.grid(row=1)
            self.FooterFrame = tk.Frame(self.contentFrame)
            self.FooterFrame.grid(row=2)
            
            self.select_folder()
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
        def clear_ContentFrame(self):
            for widgets in self.HeaderFrame.winfo_children():
                widgets.destroy()
            for widgets in self.BodyFrame.winfo_children():
                widgets.destroy()
            for widgets in self.FooterFrame.winfo_children():
                widgets.destroy()
        def quit(self):
            self.root.destroy()
        def select_folder(self):
            global fdir
            def pselect_folder(event=None):
                print("inside pselect")
                global fdir
                
                self.root.unbind('<Return>')
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                
                if fdir:
                    print(fdir)
                    self.fdir = fdir
                    select_folder_button.destroy()
                    #print selected:
                    self.SelDir.set(fdir)
                    
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=pselect_folder)
                    select_folder_button2.grid(row=1,column=0)
                    
                    Confirm_btn.grid(row=1,column=1)
                self.root.bind('<Return>', self.input_auth)
                    
            self.SelectionFrame = Frame(self.BodyFrame)
            self.SelectionFrame.grid(row=0)
            self.Confirm_SelectionFrame = Frame(self.BodyFrame)
            self.Confirm_SelectionFrame.grid(row=1)
            self.urls = []
            select_folder_button = tk.Button(self.SelectionFrame,text="SELECCIONAR CARPETA DE DESCARGA",command=pselect_folder)
            select_folder_button.grid(row=0)
            self.root.bind('<Return>', pselect_folder)
            self.SelDir = StringVar()
            l0 = tk.Label(self.SelectionFrame,  text="CARPETA SELECCIONADA:")
            
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.input_auth)
            
            # Confirm_btn.bind('<Return>', self.add_direct_links)
            # #print(fdir)

            # print("""Instructions:
            # 1. Are you going to download from multiple links?
            # 2. Base name of the file to rename. This is: NEW_FILE_LOCATION + \\ + final name (AUTO ADDS ->appended 0N)
            # 3. Format of the file you are downloading

            # 1.2 If there are multiple links paste them one by one + Enter

            # """)
            # bulk_download = input("Bulk link download?")
            # multiple = input("Multiple downloads? >")
            # base_name = input("base_name_00n >")
            # fformat = input("Format >")
            #https://descarga-directa.fukou-da.net/0:/Anime/D/Death%20Note/%5BWZF%5DDeath_Note_Capitulo_01%5BTVRip%5D%5Bx264-AAC%5D%5B848x480%5D%5BSub-Esp%5D.avi
            
            id = 0
            adding = True

            # if bulk_download == "yes" or multiple == "y":
            #     bulk_links = input("bulk links (separated by \n\n) >")
            #     for link_url in bulk_links.split("\n\n"):
            #         urls.append(link_url)
            # else:
        def input_auth(self,Event=None):

            self.clear_ContentFrame()
            self.client_id = StringVar()
            client_id_Label = Label(self.BodyFrame,text="Client ID:")
            client_id_Label.grid(row=0)
            client_id = Entry(self.BodyFrame,textvariable=self.client_id)
            client_id.grid(row=1)

            self.client_secret = StringVar()
            client_secret_Label = Label(self.BodyFrame,text="Client Secret:")
            client_secret_Label.grid(row=2)
            client_secret = Entry(self.BodyFrame,textvariable=self.client_secret)
            client_secret.grid(row=3)

            self.Username = StringVar()
            Username_Label = Label(self.BodyFrame,text="Username")
            Username_Label.grid(row=4)
            Username = Entry(self.BodyFrame,textvariable=self.Username)
            Username.grid(row=5)
            
            self.Password = StringVar()
            Password_Label = Label(self.BodyFrame,text="Password")
            Password_Label.grid(row=6)
            Password = Entry(self.BodyFrame,textvariable=self.Password)
            Password.grid(row=7)
            
            selectionFrame = Frame(self.BodyFrame,highlightthickness=1)
            selectionFrame.grid(row=8)
            self.checkbox_get_saved = tk.BooleanVar()
            self.checkbox_get_saved.set(1)
            checkbox = ttk.Checkbutton(selectionFrame, text="Download Saved Posts",variable=self.checkbox_get_saved)
            checkbox.grid(row=0)
            self.checkbox_get_upvoted = tk.BooleanVar()
            self.checkbox_get_upvoted.set(1)
            checkbox = ttk.Checkbutton(selectionFrame, text="Download Upvoted Posts",variable=self.checkbox_get_upvoted)
            checkbox.grid(row=1)

            self.onlyDownload = tk.BooleanVar()
            checkbox = ttk.Checkbutton(selectionFrame, text="Select if Json already adquired; ONLY DOWNLOAD",variable=self.onlyDownload)
            checkbox.grid(row=2)




            
            self.root.bind('<Return>', self.get_input_data)
            
            continue_Button = Button(self.FooterFrame,text="CONTINUAR",command=self.get_input_data)
            continue_Button.grid(row=0)
        
        def get_input_data(self,Event=None):
            
            print("\n\n\n\n\nGet input data\n\n\n\n\n")
            self.reddit = praw.Reddit(
                client_id = self.client_id.get(),
                client_secret = self.client_secret.get(),
                username = self.Username.get(),
                password = self.Password.get(),
                redirect_uri = 'http://localhost:8080/',
                user_agent = 'testscript by /u/jeunpeun99')
            global pb_flag
            pb_flag = True
            self.mode_selector_fetching_downloader()

        def mode_selector_fetching_downloader(self):
            if self.onlyDownload.get():
                self.downloader_2nd_Step()
                print("skip fetching")
            else:
                self.my_function()          
        def my_function(self):
            print("inside myfunc")
             
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, reddit,download_upvoted=None,download_saved=None):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.reddit = reddit
                    self.download_upvoted = download_upvoted
                    self.download_saved = download_saved
                def run(self):
                    print(f"\n##########################\nDownload Upvoted:{self.download_upvoted.get()}\nUpload Saved:{self.download_saved.get()}\n##########################")
                    def step_1_upvoted(reddit,Event=None):
                        print("Fetching Upvoted")
                        #install ffmpeg via pip install --user ffmpeg-python #also state the path via environment variables
                        #from pytube import YouTube
                        # reddit = self.reddit
                        #instance

                        # THE FOLLOWING IS COMMENTED. THE USER chrono_h Has access to the client id app from thepromidius "extractor"
                        # reddit = praw.Reddit(client_id = 'AQZDR40_sCGOvw',
                        #     client_secret = 'H_t-ejfeHM9wtMcLJSIgMYS1p6WBEg',
                        #     username = 'chrono_h',
                        #     password = 'v00001111',
                        #     redirect_uri = 'http://localhost:8080/',
                        #     user_agent = 'testscript by /u/jeunpeun99')

                        # reddit = praw.Reddit(client_id = 'BCxe8PHbJ9JdbH2TlMS3Kg',
                        #     client_secret = 'ZaiC3Zrl_8B_rYf9MQ6SzHv25QqvBw',
                        #     username = 'thepromidius',
                        #     password = 'mq8y2d3YMD0Q',
                        #     redirect_uri = 'http://localhost:8080/',
                        #     user_agent = 'testscript by /u/jeunpeun99')
                        
                        """making a directory with the subreddits as keys, and the data as values"""
                        #safe each comment in a text document called subreddit_month.txt and give the title of each comment, and the body of the comment
                        #safe for each submission the whole page with the first 1000 comments via pushshift and save it in the specific subreddit folder
                        #if the submission only contains a youtube link, download the video and place it in the specific subreddit folder
                        #if the submission only contains an image, download the image, and give it the title and the name of the user
                        #if the submission only contains a video, download the video, and give it the title and name of the user
                        #make a document with links
                        
                        class objectview(object):
                            """to access dictionary items as object attributes"""
                            def __init__(self, d):
                                self.__dict__ = d
                        # counter = 0
                        
                        def collecting_upvoted_data(after):
                            for data in reddit.user.me().upvoted(limit=25, params={"after" : after}):
                                # print(counter)
                                
                                # print(dir(data))
                                fullnames.append(data.fullname)
                                # Self comment faster
                                print(data.fullname)
                                print(data.subreddit, data.author)
                                # global label_progress_text
                                # label_progress_text.set(f"Processing post:{data.fullname}       Subreddit:{data.subreddit}       Author:{data.author}")
                                if data.author:
                                    author = data.author.name
                                else:
                                    author = "unknown"
                                
                                if getattr(data, 'crosspost_parent_list', None):
                                    data = objectview(data.crosspost_parent_list[0]) #put the crosspost_parent_list dict within the data dict
                                    data.fullname = data.name #it is called differently between the two dicts
                                    subreddit = data.subreddit
                                else:
                                    subreddit = data.subreddit.display_name
                                    
                                if data.fullname[:3] == "t1_": #Reddit comments
                                    if saved_by_user.get(subreddit):
                                        saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body])
                                    else:
                                        saved_by_user[subreddit] = []
                                        saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body]) #data.replies ])
                                if data.fullname[:3] == "t3_":
                                    if "reddit.com/r/" in data.url: #normal Reddit post
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
                                        else:
                                            saved_by_user[subreddit] = [] 
                                            saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
                                    elif "youtu.be/" in data.url: #youtube, download later
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                    elif "v.redd" in data.url:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
                                    elif "i.redd" in data.url:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                    else:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])

                            return fullnames, saved_by_user
                        
                        saved_by_user = {}
                        fullnames = []
                        
                        fullnames, saved_by_user = collecting_upvoted_data(None)
                        collected = []
                        Contador = 0
                        
                        while fullnames[-1] not in collected:
                            Contador +=1
                            global label_progress_text
                            label_progress_text.set(f"Processed: {Contador*25} Posts")
                            collected.append(fullnames[-1])
                            fullnames, saved_by_user = collecting_upvoted_data(fullnames[-1])
                            # time.sleep(1)
                        
                        print(len(fullnames))
                        print(saved_by_user)
                        
                        date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
                        with open(f'{fdir}/upvoted_by_user.json', 'w+') as datafile: 
                            json.dump(saved_by_user, datafile)
                        
                        
                        date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
                        with open(f'{fdir}/upvoted_by_user.json', 'r') as datafile: 
                            saved_by_user = json.load(datafile)
                    def step_1_saved(reddit,Event=None):
                        print("Fetching Saved")
                        #install ffmpeg via pip install --user ffmpeg-python #also state the path via environment variables
                        #from pytube import YouTube
                        # reddit = self.reddit
                        #instance

                        # THE FOLLOWING IS COMMENTED. THE USER chrono_h Has access to the client id app from thepromidius "extractor"
                        # reddit = praw.Reddit(client_id = 'AQZDR40_sCGOvw',
                        #     client_secret = 'H_t-ejfeHM9wtMcLJSIgMYS1p6WBEg',
                        #     username = 'chrono_h',
                        #     password = 'v00001111',
                        #     redirect_uri = 'http://localhost:8080/',
                        #     user_agent = 'testscript by /u/jeunpeun99')

                        # reddit = praw.Reddit(client_id = 'BCxe8PHbJ9JdbH2TlMS3Kg',
                        #     client_secret = 'ZaiC3Zrl_8B_rYf9MQ6SzHv25QqvBw',
                        #     username = 'thepromidius',
                        #     password = 'mq8y2d3YMD0Q',
                        #     redirect_uri = 'http://localhost:8080/',
                        #     user_agent = 'testscript by /u/jeunpeun99')
                        
                        """making a directory with the subreddits as keys, and the data as values"""
                        #safe each comment in a text document called subreddit_month.txt and give the title of each comment, and the body of the comment
                        #safe for each submission the whole page with the first 1000 comments via pushshift and save it in the specific subreddit folder
                        #if the submission only contains a youtube link, download the video and place it in the specific subreddit folder
                        #if the submission only contains an image, download the image, and give it the title and the name of the user
                        #if the submission only contains a video, download the video, and give it the title and name of the user
                        #make a document with links
                        
                        class objectview(object):
                            """to access dictionary items as object attributes"""
                            def __init__(self, d):
                                self.__dict__ = d
                        # counter = 0
                        
                        def collecting_saved_data(after):
                            for data in reddit.user.me().saved(limit=25, params={"after" : after}):
                                # print(counter)
                                
                                # print(dir(data))
                                fullnames.append(data.fullname)
                                # Self comment faster
                                print(data.fullname)
                                print(data.subreddit, data.author)
                                # global label_progress_text
                                # label_progress_text.set(f"Processing post:{data.fullname}       Subreddit:{data.subreddit}       Author:{data.author}")
                                if data.author:
                                    author = data.author.name
                                else:
                                    author = "unknown"
                                
                                if getattr(data, 'crosspost_parent_list', None):
                                    data = objectview(data.crosspost_parent_list[0]) #put the crosspost_parent_list dict within the data dict
                                    data.fullname = data.name #it is called differently between the two dicts
                                    subreddit = data.subreddit
                                else:
                                    subreddit = data.subreddit.display_name
                                    
                                if data.fullname[:3] == "t1_": #Reddit comments
                                    if saved_by_user.get(subreddit):
                                        saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body])
                                    else:
                                        saved_by_user[subreddit] = []
                                        saved_by_user[subreddit].append(["comment", data.fullname, data.permalink, author, data.created, data.score, data.link_title, data.body]) #data.replies ])
                                if data.fullname[:3] == "t3_":
                                    if "reddit.com/r/" in data.url: #normal Reddit post
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
                                        else:
                                            saved_by_user[subreddit] = [] 
                                            saved_by_user[subreddit].append(["post", data.fullname, data.permalink, author, data.created, data.score, data.title, data.selftext])
                                    elif "youtu.be/" in data.url: #youtube, download later
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["youtube", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                    elif "v.redd" in data.url:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["video", data.fullname, data.permalink, author, data.created, data.score, data.title, data.media["reddit_video"]["fallback_url"]])
                                    elif "i.redd" in data.url:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["image", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                    else:
                                        if saved_by_user.get(subreddit):
                                            saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])
                                        else:
                                            saved_by_user[subreddit] = []
                                            saved_by_user[subreddit].append(["link", data.fullname, data.permalink, author, data.created, data.score, data.title, data.url])

                            return fullnames, saved_by_user
                        
                        saved_by_user = {}
                        fullnames = []
                        
                        fullnames, saved_by_user = collecting_saved_data(None)
                        collected = []
                        Contador = 0
                        
                        while fullnames[-1] not in collected:
                            Contador +=1
                            global label_progress_text
                            label_progress_text.set(f"Processed: {Contador*25} Posts")
                            collected.append(fullnames[-1])
                            fullnames, saved_by_user = collecting_saved_data(fullnames[-1])
                            # time.sleep(1)
                        
                        print(len(fullnames))
                        print(saved_by_user)
                        
                        date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
                        with open(f'{fdir}/saved_by_user.json', 'w+') as datafile: 
                            json.dump(saved_by_user, datafile)
                        
                        
                        date_file = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y-%m')
                        with open(f'{fdir}/saved_by_user.json', 'r') as datafile: 
                            saved_by_user = json.load(datafile)
                    
                    if self.download_saved.get():
                        step_1_saved(self.reddit)
                    
                    if self.download_upvoted.get():
                        step_1_upvoted(self.reddit)
                    

                    #whatever wants to run here

                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    
                    
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Descargando archivos...")
            t2 = WaitUp(self.reddit,download_upvoted=self.checkbox_get_upvoted,download_saved=self.checkbox_get_saved)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg

        def downloader_2nd_Step(self):
            import requests # to get image from the web
            import shutil # to save it locally
            
            import unicodedata
            import time
            import re
            import string
            import os
            
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, reddit,download_upvoted=None,download_saved=None):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.reddit = reddit
                    self.download_upvoted = download_upvoted
                    self.download_saved = download_saved
                def run(self):
                    def format_filename(s):
                        """Take a string and return a valid filename constructed from the string.
                        Uses a whitelist approach: any characters not present in valid_chars are
                        removed. Also spaces are replaced with underscores.
                        
                        Note: this method may produce invalid filenames such as ``, `.` or `..`
                        When I use this method I prepend a date string like '2009_01_15_19_46_32_'
                        and append a file extension like '.txt', so I avoid the potential of using
                        an invalid filename.
                        
                        """
                        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
                        filename = ''.join(c for c in s if c in valid_chars)
                        filename = filename.replace(' ','_') # I don't like spaces in filenames.
                        if filename.endswith("."):
                            filename = filename[:(len(filename)-1)]
                        return filename

                    def analyse_web(url):
                        try:
                            r = requests.get(url)
                        except:
                            return
                        match = re.findall('http[s]?://(?:youtu|[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(r.content))
                        file_extensions = ["mp4","gif"]
                        link_matches = []
                        link_mp4 = []
                        link_image = []
                        print(match)
                        if match:
                            for link in match:
                                try:
                                    link_test = link.rsplit(".",1)[1]
                                except:
                                    print("error")
                                    return
                                if link_test in ["mp4"]:
                                    link_mp4.append(link)
                                    break
                                elif link.rsplit(".",1)[1] in ["gif"]:
                                    
                                    link_matches.append(link)
                                    break
                                elif link.rsplit(".",1)[1] in ["jpg"]:
                                    link_matches.append(link)
                                    break
                            if "mp4" and "gif" in link_matches:
                                extension = "mp4"
                            print("VIDEOOO")
                            print(link_mp4)
                            if not link_mp4:
                                print("Matches",link_matches)
                                if not link_matches:
                                    return "no matches multimedia file"
                                return link_matches[0]
                            print("Link mp4 out")
                            return link_mp4[0]
                            # print(match)
                            # print(r.content)
                        else:
                            return "No link"
                    
                    root_scan = []
                    for root in os.walk(fdir):
                        root_scan.append(root)
                        folders_scan = root_scan[0][1]
                        files_scan = root_scan[0][2]
                                
                    print(files_scan,"\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                    errors = []

                    def procesa(filename):
                        item_counter = 0
                        with open(filename,"r") as f:
                            # print(json.load(f))
                            # import json
                            import errno
                            json_data = json.load(f)
                            # print(json)
                            item_count_total = 0
                            for json_entry in json_data:
                            # print(json_entry)
                                for json_entry_sub in json_data[json_entry]:
                                    item_count_total +=1

                            
                            for json_entry in json_data:
                                
                                # print(json_entry)
                                for json_entry_sub in json_data[json_entry]:
                                    item_counter +=1
                                    print(item_counter)
                                    test_json = json_entry_sub
                                    # if re.match("2b",str(json[json_entry])):
                                    #     print("222222 b")

                                    # print("run",json_entry_sub)
                                    # print(json_entry_sub)
                                    name = json_entry_sub[6]
                                    print("Name sub entry:         -",name)
                                    link = json_entry_sub[7]
                                    print("Link sub entry:         -",link)
                                    if len(link) > 60:
                                        continue
                                    if not link:
                                        continue
                                    try:
                                        
                                        extension1 = link.rsplit("/",1)[1]
                                        extension2 = extension1.rsplit(".",1)[1]
                                        print(extension2)
                                        if re.match(r"\.com",extension2 ):
                                            # raise Exception
                                            print("\n\nPOssible error 1:",link,"\n",name,"\n")
                                            link = analyse_web(link)
                                            if link in ["no matches multimedia file","No link"]:
                                                print("out already",link)
                                            if link:
                                                extension = link.rsplit("/",1)[1].rsplit(".",1)[1]
                                                extension =  "." + link.rsplit(".",1)[1]
                                            else:
                                                print("error")
                                                errors.append([name,link])
                                                continue
                                            extension =  "." + extension2
                                    except:
                                        # raise Exception
                                        print("\n\nPOssible error 2\n\n",link)
                                        link = analyse_web(link)
                                        print("out already",link)
                                        if link:
                                            try:
                                                extension = link.rsplit("/",1)[1].rsplit(".",1)[1]
                                                extension =  "." + link.rsplit(".",1)[1]
                                            except:
                                                print("error")
                                                errors.append([name,link])
                                                continue    
                                        else:
                                            print("error")
                                            errors.append([name,link])
                                            continue
                                        # extension =  ".mp4" 
                                        # print("VIDEOO")
                                        
                                    # print("real continue")
                                    # if len(name)<60:
                                    #     continue
                                    # filename = 
                                # if re.match("2b",str(json_entry_sub)):
                                #     print("222222 b")
                        # # image_url = "https://cdn.pixabay.com/photo/2020/02/06/09/39/summer-4823612_960_720.jpg"
                        # filename = image_url.split("/")[-1]

                                    # Open the url image, set stream to True, this will return the stream content.
                                    time.sleep(1)
                                    try:
                                        r = requests.get(link, stream = True)
                                    except Exception as e:
                                        print(e)
                                        continue

                                    # Check if the image was retrieved successfully
                                    if r.status_code == 200:
                                        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                                        r.raw.decode_content = True

                                        #
                                        print(link)
                                        name = format_filename(name)
                                        try:
                                            
                                            extension = link.rsplit("/",1)[1].rsplit(".",1)[1]
                                            extension =  "." + link.rsplit(".",1)[1]
                                        # raise Exception
                                        except:
                                            print("\n\nPOssible error 3\n\n",link)
                                            link = analyse_web(link)
                                            print("out already",link)
                                            if link:
                                                extension = link.rsplit("/",1)[1].rsplit(".",1)[1]
                                                extension =  "." + link.rsplit(".",1)[1]
                                                
                                            else:
                                                print("error")
                                                errors.append([name,link])
                                                continue
                                            # extension =  ".mp4" 
                                            print("VIDEOO")
                                                    
                                        print(name)
                                        if name.endswith("."):
                                            name = name[:(len(name)-1)]
                                        name = name + extension
                                        print(name)
                                        # Open a local file with wb ( write binary ) permission.
                                        try:
                                            if filename == "saved_by_user.json":
                                                file_group = "Saved"
                                                filename_path = f"saved\\{name}"
                                                print(f"\n\n\nFInal filename\n{filename_path}\n\n\n\n\n\n")
                                            elif filename == "upvoted_by_user.json":
                                                file_group = "Upvoted"
                                                filename_path = f"upvoted\\{name}" 
                                                print(f"\n\n\nFInal filename\n{filename_path}\n\n\n\n\n\n")
                                            if not os.path.exists(os.path.dirname(filename_path)):
                                                try:
                                                    os.makedirs(os.path.dirname(filename_path))
                                                except OSError as exc: # Guard against race condition
                                                    if exc.errno != errno.EEXIST:
                                                        raise
                                            with open(filename_path,'wb') as f:
                                                shutil.copyfileobj(r.raw, f)
                                            # global label_progress_text
                                            
                                            label_progress_text.set(f'Downloaded {item_counter}/{item_count_total} {file_group} Posts ')
                                            print(f'Downloaded {item_counter}/{item_count_total} {file_group} Posts ',name)
                                        except:
                                            errors.append([name,link])
                                            continue

                                    else:
                                        print('Image Couldn\'t be retreived')
                        print("ERRORS:\n",errors)
                    if self.download_saved.get():
                        procesa("saved_by_user.json")
                    
                    if self.download_upvoted.get():
                        procesa("upvoted_by_user.json")            
                    

                    #whatever wants to run here

                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    
                    
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Descargando archivos...")
            t2 = WaitUp(self.reddit,download_upvoted=self.checkbox_get_upvoted,download_saved=self.checkbox_get_saved)  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg
    class MangaFolderZipper:
        def __init__(self,root):
            
            for widgets in root.winfo_children():
                widgets.destroy()
            self.root = root
            #Initialize Window
            self.contentFrame = tk.Frame(self.root,width=1000,)#,highlightbackground="black",highlightthickness=0.5,padx=5
            self.contentFrame.grid(row=0)
            self.ExitFrame = tk.Frame(self.root)
            self.ExitFrame.grid(row=1)
            quit_button = tk.Button(self.ExitFrame, text = 'Salir', command=self.quit)
            quit_button.grid(row=0)

            self.HeaderFrame = tk.Frame(self.contentFrame)
            self.HeaderFrame.grid(row=0)
            self.BodyFrame = tk.Frame(self.contentFrame)
            self.BodyFrame.grid(row=1)
            self.FooterFrame = tk.Frame(self.contentFrame)
            self.FooterFrame.grid(row=2)
            
            self.select_folder()
            
        def clear_frame(self,frame):
            for widgets in frame.winfo_children():
                widgets.destroy()
        def clear_ContentFrame(self):
            for widgets in self.HeaderFrame.winfo_children():
                widgets.destroy()
            for widgets in self.BodyFrame.winfo_children():
                widgets.destroy()
            for widgets in self.FooterFrame.winfo_children():
                widgets.destroy()
        def quit(self):
            self.root.destroy()
        def select_folder(self):
            global fdir
            def pselect_folder(event=None):
                print("inside pselect")
                global fdir
                
                self.root.unbind('<Return>')
                if launch_path:
                    fdir = filedialog.askdirectory(initialdir=launch_path)
                else:
                    fdir = filedialog.askdirectory()
                
                if fdir:
                    print(fdir)
                    self.fdir = fdir
                    select_folder_button.destroy()
                    #print selected:
                    self.SelDir.set(fdir)
                    
                    l0.grid(row=0) 
                    l1.grid(row=1) 
                    select_folder_button2 = tk.Button(self.Confirm_SelectionFrame,text="SELECCIONAR OTRA CARPETA",command=pselect_folder)
                    select_folder_button2.grid(row=1,column=0)
                    
                    Confirm_btn.grid(row=1,column=1)
                self.root.bind('<Return>', self.start_processing)
                    
            self.SelectionFrame = Frame(self.BodyFrame)
            self.SelectionFrame.grid(row=0)
            self.Confirm_SelectionFrame = Frame(self.BodyFrame)
            self.Confirm_SelectionFrame.grid(row=1)
            self.urls = []
            select_folder_button = tk.Button(self.SelectionFrame,text="SELECCIONAR CARPETA DE DESCARGA",command=pselect_folder)
            select_folder_button.grid(row=0)
            self.root.bind('<Return>', pselect_folder)
            self.SelDir = StringVar()
            l0 = tk.Label(self.SelectionFrame,  text="CARPETA SELECCIONADA:")
            
            l1 = tk.Label(self.SelectionFrame,  textvariable=self.SelDir,borderwidth=2,relief="groove")
            Confirm_btn = tk.Button(self.Confirm_SelectionFrame, text="CONFIRMAR", command=self.start_processing)
            
            
            
            id = 0
            adding = True
        def start_processing(self,event=None):
            self.my_function()
                 
        def my_function(self):
            import shutil
            
            print("inside myfunc")
             
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                def run(self):
                    print("fdir",fdir)
                    print("\nInside Folder:")
                    def make_archive(source, destination):
                        print("Destination:",destination)
                        base = os.path.basename(destination)
                        print("base",base)
                        name = base[:-4]
                        print("name",name)
                        format = base.split('.')[-1]
                        print("format",format)
                        archive_from = os.path.dirname(source)
                        archive_to = os.path.basename(source.strip(os.sep))

                        print("t")
                        shutil.make_archive(name, format, archive_from, archive_to)
                        destination = f"{destination[:-4]}.cbz"
                        print(destination)
                        shutil.move('%s.%s'%(name,format), destination)
                        

                        # make_archive('/path/to/folder', '/path/to/folder.zip')
                    series = os.listdir(fdir)
                    for serie in series:
                        if re.match(r"(?i).*\.[a-z]{3}",serie):
                            print("serie Skipped")
                            continue
                        print(serie)
                        seriePath = Path(f"{fdir}\\{serie}")
                        os.chdir(seriePath)
                        chapters = os.listdir(f"{fdir}\\{serie}")
                        
                        for chapterFolderName in chapters:
                            print(chapterFolderName)
                            chapter = chapterFolderName.split("_")[-1]
                            print("nEwChaptername",chapter)
                            chapterFolderPath = f"{fdir}\\{serie}\\{chapterFolderName}"
                            newchapterPath = f"{fdir}\\{serie}\\{chapter}.zip"
                            
                            print("final path",Path(f"{fdir}\\{serie}\\"))
                            # make_archive(chapter, "zip", chapterPath , ))
                            make_archive(chapterFolderPath,newchapterPath)
                            # make_archive(f"{fdir}\\{serie}",f"{fdir}\\{serie}\\{chapter}.zip")

                    # for subdir, dirs, files in os.walk(fdir):
                    #     print(subdir)
                    #     print(dirs)
                    #     # print(files)
                    #     print("\n\n")

                        # print(folder)
                        # new_path = os.path.join(fdir, folder)
                        # print(new_path)
                        # print(f"Result: {folder}.zip")
                        # make_archive(new_path,f"{fdir}\\{folder}\\{folder}.zip")
                    

                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    
                    
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    for widgets in root.winfo_children():
                        widgets.destroy()
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
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
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Comprimiendo archivos...")
            t2 = WaitUp()  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg
    # date = imgdate.ImageDate(r"C:\Users\galla\Google Drive\Programacion\Python\ORGANIZADOR_IMAGENES 2.0\Copia de 130809 sella 5.JPG")
    # print(date)


# If launched the .py from the windows contextual menu, get the folder where the menu was oppened.
# When one script requires to select a directory it will default choose that gets retrieved here:
# python.exe somescript.py "c:/this is / Some / directory / and file.py"
print(sys.argv)
fn = sys.argv[1::]
print(fn)
fn = " ".join(fn)
print(fn)
launch_path = None
if os.path.exists(fn):
    # folder_launch_path = os.path.dirname(fn)
    print(fn)
    launch_path = fn
    # file exists
    app = ScriptIndex(launch_path)

else:
    app = ScriptIndex(launch_path)

# HELPER
def HELPER_my_function(self):
            print("inside myfunc")
            class WaitUp(Thread):  # Define a new subclass of the Thread class of the Thread Module.
                def __init__(self, ulrs):
                    Thread.__init__(self)  # Override the __init__
                    self.i_waited_for_this = ""
                    self.urls = ulrs
                def run(self):
                    

                    #whatever wants to run here

                    global pb_flag
                    pb_flag = False
                    self.i_waited_for_this = "it is done"  # result of the task / replace with object or variable you want to pass
            class ProgressBarIn:
                def __init__(self, title="", label="", text=""):
                    self.title = title  # Build the progress bar
                    self.label = label
                    self.text = text
                    
                    
                    label_progress_text.set(text)
                    self.label_progress_text = label_progress_text

                    

                def startup(self):
                    
                    self.pb_root = root # create a window for the progress bar
                    self.pb_label = Label(self.pb_root, text=self.label)  # make label for progress bar
                    self.pb = ttk.Progressbar(self.pb_root, length=400, mode="indeterminate")  # create progress bar
                    global label_progress_text
                    self.pb_text = Label(self.pb_root, textvariable=label_progress_text, anchor="w")
                    self.pb.start()
                    self.pb_root.title(self.title)
                    self.pb_label.grid(row=0, column=0, sticky="w")
                    self.pb.grid(row=1, column=0, sticky="w")
                    self.pb_text.grid(row=2, column=0, sticky="w")
                    while pb_flag == True:  # move the progress bar until multithread reaches line 19
                        self.pb_root.update()
                        self.pb['value'] += 1
                        #print(self.pb['value'])
                        time.sleep(.1)

                def stop(self):
                    self.pb.stop()  # stop and destroy the progress bar
                    self.pb_label.destroy()  # destroy the label for the progress bar
                    self.pb.destroy()
                    self.pb_root.destroy()
                    self.return_msg = "back to menu"
                    return 
            
            global pb_flag
            global ready
            global t1
            global t2
            
            global label_progress_text
            label_progress_text = tk.StringVar()
                # print(item)
            ready = False
            t1 = ProgressBarIn(title="Procesando", label="Por favor espera", text="Descargando archivos...")
            t2 = WaitUp()  # pass the progress bar object
            t2.start()  # use start() instead of run() for threading module
            t1.startup()  # start the progress bar
            t2.join()  # wait for WaitUp to finish before proceeding
            t1.stop()  # destroy the progress bar object
            return t1.return_msg


# app = ScriptIndex()
# app = ScriptIndex()
