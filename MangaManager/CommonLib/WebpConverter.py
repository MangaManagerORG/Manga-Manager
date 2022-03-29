#!/usr/bin/env python3
import logging
import os
import re
import tempfile
import time
import tkinter as tk
import zipfile
from io import BytesIO
from tkinter import filedialog
from tkinter.ttk import Style, Progressbar

from PIL import Image

logger = logging.getLogger(__name__)
from CommonLib.HelperFunctions import get_estimated_time, get_elapsed_time

supportedFormats = (".png", ".jpeg", ".jpg")


class App:
    # TODO: Add UI
    def __init__(self, master: tk.Tk, overrideSupportedFormat=supportedFormats):
        """
        :param master: tkinter integration
        :param overrideSupportedFormat: Override these formats to include any that is supported by PIL
        """
        if not master:
            self.master = tk.Tk()
        else:
            self.master = master
        self.cbzFilePathList = list[str]()
        self.overrideSupportedFormat = overrideSupportedFormat

    def start(self):

        if not self.cbzFilePathList:
            return
        logger.info(f"Loaded file list: \n" + "\n".join(self.cbzFilePathList))
        total = len(self.cbzFilePathList)
        # _printProgressBar(0, l, prefix='Progress:', suffix='Complete', length=50)
        logger.debug("Starting processing of files.")

        label_progress_text = tk.StringVar()
        start_time = time.time()
        if self._initialized_UI:
            pb_root = self._progressbar_frame

            style = Style(pb_root)
            style.layout('text.Horizontal.TProgressbar',
                         [('Horizontal.Progressbar.trough',
                           {'children': [
                               ('Horizontal.Progressbar.pbar', {
                                   'side': 'left',
                                   'sticky': 'ns'
                               })],
                               'sticky': 'nswe'}),
                          ('Horizontal.Progressbar.label', {
                              'sticky': 'nswe'
                          })])

            pb = Progressbar(pb_root, length=400, style='text.Horizontal.TProgressbar',
                             mode="determinate")  # create progress bar
            style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')

            pb_text = tk.Label(pb_root, textvariable=label_progress_text, anchor=tk.W)
            logger.info("Initialized progress bar")
            pb.grid(row=0, column=0, sticky=tk.E + tk.W)
            pb_text.grid(row=1, column=0, sticky=tk.E)

        processed_counter = 0
        processed_errors = 0
        label_progress_text.set(
            f"Processed: {(processed_counter + processed_errors)}/{total} files - {processed_errors} errors\n"
            f"Elapsed time  : {get_elapsed_time(start_time)}\n"
            f"Estimated time: {get_estimated_time(start_time, processed_counter, total)}")

        for i, cbzFilepath in enumerate(self.cbzFilePathList):
            # print(i)
            # print(cbzFilepath)
            # cbzFilepath in cbzFilePathList:
            logger.info(f"Processing '{cbzFilepath}'")
            self.zipFilePath = cbzFilepath

            tmpfd, self._tmpname = tempfile.mkstemp(dir=os.path.dirname(self.zipFilePath))
            os.close(tmpfd)

            self._supported_formats = self.overrideSupportedFormat
            # logger.info("Processing...")
            try:
                self._process()

                os.remove(self.zipFilePath)
                os.rename(self._tmpname, self.zipFilePath)
                logger.info(f"Done")
                # time.sleep(2)
                logger.info(f"Processed '{os.path.basename(self.cbzFilePathList[i])}'")
                processed_counter += 1
            except zipfile.BadZipfile as e:
                logger.error(f"Error processing '{cbzFilepath}': {str(e)}", exc_info=True)
                os.remove(self._tmpname)
                processed_errors += 1
                continue
            if self._initialized_UI:
                pb_root.update()
                percentage = ((processed_counter + processed_errors) / total) * 100
                style.configure('text.Horizontal.TProgressbar',
                                text='{:g} %'.format(round(percentage, 2)))  # update label
                pb['value'] = percentage
                label_progress_text.set(
                    f"Processed: {(processed_counter + processed_errors)}/{total} files - {processed_errors} errors\n"
                    f"Elapsed time: {get_elapsed_time(start_time)}\n"
                    f"Estimated time: {get_estimated_time(start_time, processed_counter, total)}")
            # _printProgressBar(i + 1, l, prefix=f"Progress:", suffix='Complete', length=50)
        logger.info("Completed processing for all selected files")
    def _process(self):
        with zipfile.ZipFile(self.zipFilePath, 'r') as zin:
            with zipfile.ZipFile(self._tmpname, 'w') as zout:
                for zipped_file in zin.infolist():
                    # logger.debug(f"Processing file {zipped_file.filename}")
                    file_format = re.findall(r"(?i)\.[a-z]+$", zipped_file.filename)
                    if file_format:
                        file_format = file_format[0]
                    else:  # File doesn't have an extension, it is a folder. skip it
                        zout.writestr(zipped_file.filename, zin.read(zipped_file.filename))
                        logger.debug(f"Added '{zipped_file.filename}' to new tempfile. File was not processed")
                        continue
                    file_name = zipped_file.filename.replace(file_format, "")
                    if file_format in self._supported_formats:
                        with zin.open(zipped_file) as open_zipped_file:
                            zout.writestr(file_name + ".webp", convertToWebp(open_zipped_file))
                            logger.debug(f"Converted '{zipped_file.filename}' to webp")
                            # logger.debug(f"Added '{zipped_file.filename}' to new tempfile")
                            continue
                    zout.writestr(zipped_file.filename, zin.read(zipped_file.filename))
                    logger.debug(f"Added '{zipped_file.filename}' to new tempfile. File was not processed")

    def _select_files(self):

        self.epubsPathList = list[str]()
        files_IO = filedialog.askopenfiles(title="Select .cbz files to convert its content to .webp",
                                           filetypes=(("epub Files", ".cbz"),))
        for file in files_IO:
            self.cbzFilePathList.append(file.name)
            displayed_file_path = f"...{file.name[-65:]}"
            self.listbox_1.insert(tk.END, displayed_file_path)
            self.listbox_1.yview_moveto(1)

        # self.run()

    def start_ui(self):
        # build ui
        self.frame_1 = tk.Frame(self.master)

        self.label_1 = tk.Label(self.frame_1)
        self.label_1.configure(font='{Title} 20 {}', text='Webp Converter')
        self.label_1.grid(column='0', row='0')
        self.label_2 = tk.Label(self.frame_1)
        self.label_2.configure(font='{SUBTITLE} 12 {}',
                               text='This script converts the images to .webp format.')
        self.label_2.grid(column='0', row='1')
        self.button_1 = tk.Button(self.frame_1)
        self.button_1.configure(text='Load .cbz files')
        self.button_1.grid(column='0', row='2')
        self.button_1.configure(command=self._select_files)
        self.label_3 = tk.Label(self.frame_1)
        self.label_3.configure(text='Selected files:')
        self.label_3.grid(column='0', row='3')
        self.listbox_1 = tk.Listbox(self.frame_1)
        self.listbox_1.configure(activestyle='dotbox', font='{courier} 12 {}', justify='center', width='69')
        self.listbox_1.grid(column='0', row='4')
        self.button_2 = tk.Button(self.frame_1)
        self.button_2.configure(text='Process')
        self.button_2.grid(column='0', row='5')
        self.button_2.configure(command=self.start)
        self.frame_1.configure(height='200', padx='50', pady='50', width='200')
        self.frame_1.grid(column='0', row='0')
        self.frame_1.rowconfigure('2', pad='20')
        self._progressbar_frame = tk.Frame(self.frame_1)
        self._progressbar_frame.grid(column=0, row=6)
        # self.button_2 = tk.Button(self.frame_1)
        # self.button_2.configure(text='Change output folder')
        # self.button_2.grid(column='0', row=7)
        # self.button_2.configure(command=self._change_out_folder)
        # self.label_4 = tk.Label(self.frame_1)
        # self.label_4.configure(text='Selected folder:\nfile_path/epub2cbz/')
        # self.label_4.grid(column='0', row=8)

        self._initialized_UI = True

    def run(self):
        self.master.mainloop()
# CLI ProgressBar


def _printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def getNewWebpFormatName(currentName: str) -> str:
    file_format = re.findall(r"(?i)\.[a-z]+$", currentName)
    if file_format:
        file_format = file_format[0]
        file_name = currentName.replace(file_format, "")
        return file_name + ".webp"


def convertToWebp(open_zipped_file) -> bytes:
    # TODO: Bulletproof image passed not image
    image = Image.open(open_zipped_file)
    # print(image.size, image.mode, len(image.getdata()))
    converted_image = BytesIO()
    image.save(converted_image, format="webp")
    image.close()
    logger.debug("Successfully converted image to webp")
    return converted_image.getvalue()

#
# if __name__ == '__main__':
#     import pathlib
#     from logging.handlers import RotatingFileHandler
#     import glob
#
#     PROJECT_PATH = pathlib.Path(__file__).parent
#     rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/WebpConverter.log", maxBytes=1025760,
#                                                 backupCount=1)
#
#     logging.getLogger('PIL').setLevel(logging.WARNING)
#     # formatter = logging.Formatter()
#
#     logging.basicConfig(level=logging.INFO,
#                         format='%(asctime)s - WebpConverter - %(levelname)s - %(message)s',
#                         handlers=[rotating_file_handler, ]
#                         # filename='/tmp/myapp.log'
#                         )
#     logger.info("Starting standalone Converter")
#
#     inputStr = input("Write the path to the zip-compatible files you want to convert its images to webp.")
#     if not inputStr:
#         print("No files selected")
#         exit()
#     filenames = glob.glob(inputStr)
#     if not filenames:
#         print("No files found")
#         exit()
#     app = WebpConverter(filenames)
