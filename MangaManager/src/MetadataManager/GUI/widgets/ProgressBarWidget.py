import logging
import tkinter
from tkinter.ttk import Progressbar, Style

from src.Common.progressbar import ProgressBar

logger = logging.getLogger()


class ProgressBarWidget(ProgressBar):
    def __init__(self, parent):
        pb_frame = tkinter.Frame(parent)
        pb_frame.pack(expand=False, fill="x")
        super().__init__()

        self.style = Style(pb_frame)
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

        self.progress_bar = Progressbar(pb_frame, length=10, style='text.Horizontal.TProgressbar',
                                        mode="determinate")  # create progress bar
        self.progress_bar.pack(expand=False, fill="x", side="top")
        self.pb_label_variable = tkinter.StringVar(value=self.label_text)
        self.pb_label = tkinter.Label(pb_frame, justify="right", textvariable=self.pb_label_variable)
        self.pb_label.pack(expand=False, fill="x", side="right")
        logger.debug("Initialized progress bar")

    def update_progress_label(self):
        self.pb_label_variable.set(self.label_text)

    def _update(self):

        if not self.timer:
            return
        if self.processed >= self.total:
            self.timer.stop()
        self.update_progress_label()
        self.style.configure('text.Horizontal.TProgressbar',
                             text='{:g} %'.format(round(self.percentage, 2)))  # update label
        self.progress_bar['value'] = self.percentage
        self.progress_bar.update()
