import logging
import time
import tkinter as tk
from tkinter import ttk

from CommonLib.HelperFunctions import get_elapsed_time, get_estimated_time

logger = logging.getLogger(__name__)


class ProgressBar:
    def __init__(self, UI_isInitialized: bool, pb_root: tk.Frame, total: int):

        self.UI_isInitialized = UI_isInitialized
        self.pb_root = pb_root
        self.total = total
        self.label_progress_text = tk.StringVar()
        self.start_time = time.time()
        self.processed_counter = 0
        self.processed_errors = 0
        if not UI_isInitialized:
            return

        self.style = ttk.Style(pb_root)
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
            f"Processed: {(self.processed_counter + self.processed_errors)}/{total} files - {self.processed_errors} errors\n"
            f"Elapsed time  : {get_elapsed_time(self.start_time)}\n"
            f"Estimated time: {get_estimated_time(self.start_time, self.processed_counter, total)}")

    def increaseCount(self):
        self.processed_counter += 1
        self.updatePB()

    def increaseError(self):
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

