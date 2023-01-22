import logging
import time
import tkinter as tk
from tkinter import ttk

from src.CommonLib.HelperFunctions import get_elapsed_time
from src.CommonLib.HelperFunctions import get_estimated_time

logger = logging.getLogger(__name__)


def printProgressBar(total, _last_print_lenght, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r",
                     last=False, iteration=0, start_time=0.0):
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
    msg = f'{prefix} |{bar}| {percent}% - {iteration}/{total} {suffix} | Elapsed: {get_elapsed_time(start_time)} | Estimated: {get_estimated_time(start_time, processed_files=iteration, total_files=total)}'
    print(' ' * _last_print_lenght, end='\r')
    print("\r" + msg, end=printEnd)
    _last_print_lenght = len(msg)
    # Print New Line on Complete

    if iteration == total:
        print(msg)
        print("Processing Finished")
    return _last_print_lenght


class ProgressBar:
    def __init__(self, UI_isInitialized: bool, pb_root: tk.Frame, total: int):

        self.UI_isInitialized = UI_isInitialized
        self.pb_root = pb_root
        self.total = total

        self.start_time = time.time()
        self.processed_counter = 0
        self.processed_errors = 0

        if UI_isInitialized:
            self.label_progress_text = tk.StringVar()
            self.init_ui_initialized()
        else:
            self.init_nogui()

            return

    def init_nogui(self):
        self.last_print_length = 0
        self.last_print_length = printProgressBar(self.total, self.last_print_length, start_time=self.start_time)

    def init_ui_initialized(self):
        self.style = ttk.Style(self.pb_root)
        self.style.layout('text.Horizontal.TProgressbar',
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
        self.style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')

        self.pb = ttk.Progressbar(self.pb_root, length=400, style='text.Horizontal.TProgressbar',
                                  mode="determinate")  # create progress bar
        self.pb.grid(row=0, column=0, sticky=tk.E + tk.W)
        self.pb_text = tk.Label(self.pb_root, textvariable=self.label_progress_text, anchor=tk.W, justify="right")
        self.pb_text.grid(row=1, column=0, sticky=tk.E)

        logger.info("Initialized progress bar")

        # self.convert_images = self.checkbox2_settings_val.get()
        self.label_progress_text.set(
            f"Processed: {(self.processed_counter + self.processed_errors)}/{self.total} files - {self.processed_errors} errors\n"
            f"Elapsed time  : {get_elapsed_time(self.start_time)}\n"
            f"Estimated time: {get_estimated_time(self.start_time, self.processed_counter, self.total)}")

    def increaseCount(self):
        if self.processed_counter >= self.total:
            return
        self.processed_counter += 1
        self.updatePB()

    def increaseError(self):
        if self.processed_counter >= self.total:
            return
        self.processed_counter += 1
        self.processed_errors += 1
        self.updatePB()

    def updatePB(self):

        if self.UI_isInitialized:
            self.pb_root.update()
            percentage = ((self.processed_counter + self.processed_errors) / self.total) * 100
            self.style.configure('text.Horizontal.TProgressbar',
                                 text='{:g} %'.format(round(percentage, 2)))  # update label
            self.pb['value'] = percentage
            self.label_progress_text.set(
                f"Processed: {(self.processed_counter + self.processed_errors)}/{self.total} files - {self.processed_errors} errors\n"
                f"Elapsed time  : {get_elapsed_time(self.start_time)}\n"
                f"Estimated time: {get_estimated_time(self.start_time, self.processed_counter, self.total)}")
        else:
            self.last_print_length = printProgressBar(self.total, self.last_print_length, start_time=self.start_time,
                                                      iteration=self.processed_counter)
