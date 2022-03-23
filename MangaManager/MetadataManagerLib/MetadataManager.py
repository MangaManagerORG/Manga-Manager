#!/usr/bin/env python3
import logging
import os
import pathlib
import re
import time
import tkinter as tk
import tkinter.scrolledtext
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import ttk

from lxml.etree import XMLSyntaxError

from CommonLib.HelperFunctions import get_elapsed_time, get_estimated_time
from . import ComicInfo
from . import models
from .cbz_handler import ReadComicInfo, WriteComicInfo
from .errors import *
from .models import LoadedComicInfo

# logging.getLogger('PIL').setLevel(logger.WARNING)
# TODO:
#   - Add info message if nothing is loaded into UI because comicinfo not exist and one will be created
#   - Add successfully loaded window/message somewhere

launch_path = ""

ScriptDir = os.path.dirname(__file__)
PROJECT_PATH = pathlib.Path(__file__).parent
logger = logging.getLogger(__name__)


# noinspection PyTypeChecker
class App:
    def __init__(self, master: tk.Tk = None, disable_metadata_notFound_warning=False):
        self.master = master
        # self.master.eval('tk::PlaceWindow . center')
        self.initialize_StringVars()
        self.highlighted_changes = []
        self._initialized_UI = False
        self.widgets_obj = []
        self.spinbox_4_chapter_var_isModified = False
        self.spinbox_3_volume_var_isModified = False
        self.warning_metadataNotFound = disable_metadata_notFound_warning

    def initialize_StringVars(self):
        self.highlighted_changes = []
        self.conflict_chapter = False
        self.spinbox_1_year_var = tk.IntVar(value=(-1), name="year")
        self.spinbox_2_month_var = tk.IntVar(value=(-1), name='month')
        self.spinbox_3_volume_var = tk.IntVar(value=(-1), name='volume')
        self.spinbox_3_volume_var_prev = tk.IntVar(value=(-1), name='volume_prev')
        self.spinbox_3_volume_var.trace(mode='w', callback=self.validateIntVar)
        self.spinbox_4_chapter_var = tk.StringVar(value='', name='Number')
        self.entry_10_langIso_var = tk.StringVar(value='', name='langIso')
        # self.spinbox_5_pageCount_var = tk.IntVar(value='', name='pageCount')
        self.spinbox_5_pageCount_var = tk.IntVar(value=0, name='pageCount')
        self.entry_15_format_var = tk.StringVar(value='', name='format')
        self.optionmenu_2_blackWhite_var = tk.StringVar(value=ComicInfo.YesNo.list()[0], name='blackWhite')
        self.optionmenu_3_manga_var = tk.StringVar(value=ComicInfo.Manga.list()[0], name='manga')
        self.entry_1_seriesName_var = tk.StringVar(value='', name='seriesName')
        self.entry_2_title_var = tk.StringVar(value='', name='title')
        self.entry_3_writer_var = tk.StringVar(value='', name='writer')
        self.entry_6_storyArc_var = tk.StringVar(value='', name='storyArc')
        self.entry_7_SeriesGroup_var = tk.StringVar(value='', name='SeriesGroup')
        self.entry_4_penciller_var = tk.StringVar(value='', name='penciller')
        self.entry_5_inker_var = tk.StringVar(value='', name='inker')
        self.entry_8_colorist_var = tk.StringVar(value='', name='colorist')
        self.entry_9_letterer_var = tk.StringVar(value='', name='letterer')
        self.entry_11_coverArtist_var = tk.StringVar(value='', name='coverArtist')
        self.entry_12_editor_var = tk.StringVar(value='', name='editor')
        self.entry_13_publisher_var = tk.StringVar(value='', name='publisher')
        self.entry_14_imprint_var = tk.StringVar(value='', name='imprint')
        self.entry_16_characters_var = tk.StringVar(value='', name='characters')
        self.entry_15_genres_var = tk.StringVar(value='', name='genres')
        self.entry_16_tags_var = tk.StringVar(value='', name='tags')
        self.entry_17_web_var = tk.StringVar(value='', name='web')
        self.entry_20_scanInfo_var = tk.StringVar(value='', name='scanInfo')
        self.optionmenu_1_ageRating_var = tk.StringVar(value='Unknown', name='ageRating')
        self.input_1_summary_obj = models.LongText(name="summary")
        try:
            self.input_1_summary_obj.linked_text_field = self._text_1_summary
        except:
            pass
        self.widgets_var = [
            self.entry_1_seriesName_var,
            self.entry_2_title_var,
            self.entry_3_writer_var,
            self.entry_4_penciller_var,
            self.entry_5_inker_var,
            self.entry_6_storyArc_var,
            self.entry_7_SeriesGroup_var,
            self.entry_8_colorist_var,
            self.entry_9_letterer_var,
            self.entry_10_langIso_var,
            self.entry_11_coverArtist_var,
            self.entry_12_editor_var,
            self.entry_13_publisher_var,
            self.entry_14_imprint_var,
            self.entry_15_format_var,
            self.entry_16_characters_var,
            self.entry_17_web_var,
            self.optionmenu_2_blackWhite_var,
            self.optionmenu_3_manga_var,
            self.entry_20_scanInfo_var,
            self.spinbox_1_year_var,
            self.spinbox_2_month_var,
            self.spinbox_3_volume_var,
            self.spinbox_4_chapter_var,
            self.spinbox_5_pageCount_var,
            self.entry_16_tags_var,
            self.entry_15_genres_var,
            self.input_1_summary_obj
        ]

        self.selected_filenames = []
        self.loadedComicInfo_list = list[LoadedComicInfo]()

    def validateIntVar(self, *args):
        try:
            # if self.spinbox_3_volume_var.get() < -1 or
            if not isinstance(self.spinbox_3_volume_var.get(), int):
                self.master.bell()
                self.spinbox_3_volume_var.set(-1)
            else:
                self.spinbox_3_volume_var_prev.set(self.spinbox_3_volume_var.get())
        except tk.TclError as e:
            print(str(e))
            if str(e) == 'expected floating-point number but got ""' or str(
                    e) == 'expected floating-point number but got "-"':
                return
            elif re.match(r"^(?!.*\/\/)(-?)([0-9]+\.*[0-9]*$)", str(e)):
                return
            self.master.bell()
            if self.spinbox_3_volume_var_prev.get() != (-1):
                self.spinbox_3_volume_var.set(self.spinbox_3_volume_var_prev.get())
                return
            self.spinbox_3_volume_var.set(-1)

    def makeEditable(self, event: tk.Event = None):
        # <Double-Button-1>
        # TODO: Add a better error message to explain that any changes will be overwritten
        if event.widget.cget('state') == "disabled":
            print(str(event.widget))
            if re.match(r".*(entry_volume|spinbox_chapter).*", str(event.widget)):
                answer = mb.askyesno("Warning!", "Warning: This change will be overwritten to all files.\
                Only one file should be selected to change this value.Continue?")
                if answer:
                    event.widget.configure(state="normal", highlightbackground="#00bfff", highlightcolor="#00bfff",
                                           highlightthickness='2')
                    self.highlighted_changes.append(event.widget)
                    self.spinbox_4_chapter_var_isModified = True
                else:
                    return
        else:
            if re.match(r".*(entry_volume).*", str(event.widget)):
                self.spinbox_3_volume_var_isModified = True
            event.widget.configure(state="normal", highlightbackground="#00bfff", highlightcolor="#00bfff",
                                   highlightthickness='2')
            self.highlighted_changes.append(event.widget)

    def start_ui(self):
        master = self.master

        def makeReadOnly(event: tk.Event = None):
            # <Return>
            if event.widget.cget('state') == "disabled":
                return
            if isinstance(event.widget, tk.Entry):
                event.widget.configure(state="readonly")

        def makeFocused(event: tk.Event = None):
            # <Button-1>
            event.widget.focus()

        def onFocusOut(event: tk.Event = None):
            # <FocusOut>
            makeReadOnly(event)

        def ValidateIfNum(s, S):
            dummy = s
            # disallow anything but numbers
            valid = S == '' or S.isdigit() or S == "."
            if not valid:
                self._frame1.bell()
                # logger.info("input not valid")
            return valid

        self._initialized_UI = True
        vldt_ifnum_cmd = (self.master.register(ValidateIfNum), '%s', '%S')
        self._edit_warning = False  # We send warning that changing chapter or volume will be set to all files selected
        self._frame1 = tk.Frame(master)

        self._frame_4_leftColumn = tk.Frame(self._frame1)
        self._frame_2 = tk.Frame(self._frame_4_leftColumn)
        self._frame_2.rowconfigure("all", pad="5", weight=1)
        self._frame_2.columnconfigure("all", pad="5", weight=1)
        self._label_1_year = tk.Label(self._frame_2)
        self._label_1_year.configure(text='Year')
        self._label_1_year.grid(column=0, row='0')

        self._spinbox_1_year = tk.Spinbox(self._frame_2, from_=1800, to=99999,
                                          validate='all', validatecommand=vldt_ifnum_cmd, name="spinbox_year")
        self._spinbox_1_year.configure(justify='center', state='readonly', textvariable=self.spinbox_1_year_var)
        self._spinbox_1_year.grid(column=0, row='1')
        self._spinbox_1_year.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_1_year.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_1_year.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_1_year.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_1_year.bind('<FocusOut>', onFocusOut, add='+')
        self._spinbox_1_year.bind('<Return>', makeReadOnly, add='+')
        self._spinbox_1_year.bind('<Return>', makeReadOnly, add='+')
        self._label_2_month = tk.Label(self._frame_2)
        self._label_2_month.configure(text='Month')
        self._label_2_month.grid(column=0, row='2')
        self._spinbox_2_month = tk.Spinbox(self._frame_2, from_=1, to=12, validate='all',
                                           validatecommand=vldt_ifnum_cmd)
        self._spinbox_2_month.configure(justify='center', state='readonly', textvariable=self.spinbox_2_month_var)
        self._spinbox_2_month.grid(column=0, row='3')
        self._spinbox_2_month.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_2_month.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_2_month.bind('<FocusOut>', onFocusOut, add='+')
        self._spinbox_2_month.bind('<Return>', makeReadOnly, add='+')
        self._label_3_volume = tk.Label(self._frame_2)
        self._label_3_volume.configure(text='Volume')
        self._label_3_volume.grid(column=0, row='4')
        self._spinbox_3_volume = tk.Entry(self._frame_2, validate='all', name="entry_volume")
        self._spinbox_3_volume.configure(justify='center')
        self._spinbox_3_volume.configure(state='readonly', textvariable=self.spinbox_3_volume_var)
        self._spinbox_3_volume.grid(column=0, row='5')
        self._spinbox_3_volume.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_3_volume.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_3_volume.bind('<FocusOut>', onFocusOut, add='+')
        self._spinbox_3_volume.bind('<Return>', makeReadOnly, add='+')
        self._label_4_chapter = tk.Label(self._frame_2)
        self._label_4_chapter.configure(anchor='n', text='Chapter')
        self._label_4_chapter.grid(column=0, row='6')
        self._spinbox_4_chapter = tk.Spinbox(self._frame_2, validate="all", validatecommand=vldt_ifnum_cmd,
                                             name="spinbox_chapter")
        self._spinbox_4_chapter.configure(buttonuprelief='flat', cursor='arrow', justify='center', state='disabled')
        self._spinbox_4_chapter.configure(textvariable=self.spinbox_4_chapter_var)
        self._spinbox_4_chapter.grid(column=0, row='7')
        self._spinbox_4_chapter.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_4_chapter.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_4_chapter.bind('<FocusOut>', onFocusOut, add='+')
        self._spinbox_4_chapter.bind('<Return>', makeReadOnly, add='+')

        self._label_21_pagecount = tk.Label(self._frame_2)
        self._label_21_pagecount.configure(text='Page Count')
        self._label_21_pagecount.grid(column='1', row=0)
        self._spinbox_5_pageCount = tk.Spinbox(self._frame_2, validate='all', validatecommand=vldt_ifnum_cmd)

        self._spinbox_5_pageCount.configure(justify='center', state='readonly',
                                            textvariable=self.spinbox_5_pageCount_var)
        self._spinbox_5_pageCount.grid(column=1, row=1)
        self._spinbox_5_pageCount.bind('<Button-1>', makeFocused, add='+')
        self._spinbox_5_pageCount.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._spinbox_5_pageCount.bind('<FocusOut>', onFocusOut, add='+')
        self._spinbox_5_pageCount.bind('<Return>', makeReadOnly, add='+')

        self._label_14_langIso = tk.Label(self._frame_2)
        self._label_14_langIso.configure(text='Language ISO')
        self._label_14_langIso.grid(column='1', row=2)
        self._label_14_langIso.bind('<Button-1>', makeFocused, add='+')
        self._label_14_langIso.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._label_14_langIso.bind('<FocusOut>', onFocusOut, add='+')
        self._label_14_langIso.bind('<Return>', makeReadOnly, add='+')
        self._entry_10_langIso = tk.Entry(self._frame_2)
        self._entry_10_langIso.configure(justify='center', state='readonly', textvariable=self.entry_10_langIso_var)
        self._entry_10_langIso.grid(column='1', row=3)
        self._entry_10_langIso.bind('<Button-1>', makeFocused, add='+')
        self._entry_10_langIso.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_10_langIso.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_10_langIso.bind('<Return>', makeReadOnly, add='+')

        self._label_22_format = tk.Label(self._frame_2)
        self._label_22_format.configure(text='Format')
        self._label_22_format.grid(column='1', row=4)
        self._entry_15_format = tk.Entry(self._frame_2)
        self._entry_15_format.configure(justify='center', state='readonly', textvariable=self.entry_15_format_var)
        self._entry_15_format.grid(column='1', row=5)
        self._entry_15_format.bind('<Button-1>', makeFocused, add='+')
        self._entry_15_format.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_15_format.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_15_format.bind('<Return>', makeReadOnly, add='+')

        self._inline_BlackWhite = tk.Frame(self._frame_2)
        self._inline_BlackWhite.grid(row=10, column=0)
        self._label_25_blackWhite = tk.Label(self._inline_BlackWhite)
        self._label_25_blackWhite.configure(text='Black and White:')
        self._label_25_blackWhite.grid(column=0, row=0)
        self._optionmenu_2_blackWhite = tk.OptionMenu(self._inline_BlackWhite, self.optionmenu_2_blackWhite_var,
                                                      *ComicInfo.YesNo.list(), command=None)
        self._optionmenu_2_blackWhite.configure(width=16)
        self._optionmenu_2_blackWhite.grid(row=1, column=0, sticky=tk.E + tk.W)

        self._inline_manga = tk.Frame(self._frame_2)
        self._inline_manga.grid(row=10, column=1)
        self._label_26_manga = tk.Label(self._inline_manga)
        self._label_26_manga.configure(text='Manga:')
        self._label_26_manga.grid(column=0, row=0)
        self._optionmenu_3_manga = tk.OptionMenu(self._inline_manga, self.optionmenu_3_manga_var,
                                                 *ComicInfo.Manga.list(), command=None, )
        self._optionmenu_3_manga.configure(width=16)
        self._optionmenu_3_manga.grid(row=1, column=0, sticky=tk.E + tk.W)

        self._frame1.columnconfigure('0', pad='0', weight='0')
        self._frame_1 = tk.Frame(self._frame1)
        self._label_5_serieName = tk.Label(self._frame_1)
        self._label_5_serieName.configure(text='Series Name')
        self._label_5_serieName.grid(column='0', row='0')
        self._entry_1_seriesName = tk.Entry(self._frame_1)
        self._entry_1_seriesName.configure(justify='left', state='readonly', takefocus=False,
                                           textvariable=self.entry_1_seriesName_var)
        self._entry_1_seriesName.grid(row='1', sticky='ew')
        self._entry_1_seriesName.bind('<Button-1>', makeFocused, add='+')
        self._entry_1_seriesName.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_1_seriesName.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_1_seriesName.bind('<Return>', makeReadOnly, add='+')
        self._label_6_title = tk.Label(self._frame_1)
        self._label_6_title.configure(text='Title')
        self._label_6_title.grid(column='0', row='2')
        self._entry_2_title = tk.Entry(self._frame_1)
        self._entry_2_title.configure(font='TkDefaultFont', state='readonly', textvariable=self.entry_2_title_var)
        self._entry_2_title.grid(row='3', sticky='ew')
        self._entry_2_title.bind('<Button-1>', makeFocused, add='+')
        self._entry_2_title.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_2_title.bind('<Enter>', makeReadOnly, add='+')
        self._entry_2_title.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_2_title.bind('<Return>', makeReadOnly, add='+')
        self._label_7_summary = tk.Label(self._frame_1)
        self._label_7_summary.configure(text='Summary')
        self._label_7_summary.grid(column='0', row='4')
        self._text_1_summary = tkinter.scrolledtext.ScrolledText(self._frame_1, wrap=tk.WORD)
        self._text_1_summary.configure(cursor='arrow', height='4', state='normal', width='50')
        self.input_1_summary_obj.linked_text_field = self._text_1_summary
        self._text_1_summary.grid(row='5', sticky=tk.E + tk.W)
        self._label_5_StoryArc = tk.Label(self._frame_1)
        self._label_5_StoryArc.configure(text='Story Arc')
        self._label_5_StoryArc.grid(column='0', row='6')
        self._entry_6_storyArc = tk.Entry(self._frame_1)
        self._entry_6_storyArc.configure(state='readonly', textvariable=self.entry_6_storyArc_var)
        self._entry_6_storyArc.grid(column='0', row='7', sticky='ew')
        self._entry_6_storyArc.bind('<Button-1>', makeFocused, add='+')
        self._entry_6_storyArc.bind('<Button-1>', makeFocused, add='+')
        self._entry_6_storyArc.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_6_storyArc.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_6_storyArc.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_6_storyArc.bind('<Return>', makeReadOnly, add='+')
        self._entry_6_storyArc.bind('<Return>', makeReadOnly, add='+')

        self._inline_AgeRating = tk.Frame(self._frame_1)
        self._inline_AgeRating.grid(row=10, column=0)
        self._label_27_AgeRating = tk.Label(self._inline_AgeRating)
        self._label_27_AgeRating.configure(text='Age Rating:')
        self._label_27_AgeRating.grid(column=0, row=0)
        self._optionmenu_1 = tk.OptionMenu(self._inline_AgeRating, self.optionmenu_1_ageRating_var,
                                           *ComicInfo.AgeRating.list(),
                                           command=None)
        self._optionmenu_1.configure(width=15)
        self._optionmenu_1.grid(column=1, row=0)
        self._label_6_SeriesGroup = tk.Label(self._frame_1)
        self._label_6_SeriesGroup.configure(text='Series Group')
        self._label_6_SeriesGroup.grid(column='0', row='8')
        self._entry_7_SeriesGroup = tk.Entry(self._frame_1)
        self._entry_7_SeriesGroup.configure(state='readonly', textvariable=self.entry_7_SeriesGroup_var)
        self._entry_7_SeriesGroup.grid(column='0', row='9', sticky='ew')
        self._entry_7_SeriesGroup.bind('<Button-1>', makeFocused, add='+')
        self._entry_7_SeriesGroup.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_7_SeriesGroup.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_7_SeriesGroup.bind('<Return>', makeReadOnly, add='+')
        self._frame_1.configure(height='200', width='200')

        self._frame1.columnconfigure('1', pad='400', weight='1')
        self._frame_3_people = tk.Frame(self._frame_4_leftColumn)

        self._label_8_people = tk.Label(self._frame_3_people)
        self._label_8_people.configure(cursor='arrow', font='TkDefaultFont', text='People')
        self._label_8_people.grid(column='0', row='0')
        self._frame_3_people.columnconfigure('0', weight='1')
        self._label_9_writer = tk.Label(self._frame_3_people)
        self._label_9_writer.configure(text='Writer')
        self._label_9_writer.grid(column='0', row='1')
        self._entry_3_writer = tk.Entry(self._frame_3_people)
        self._entry_3_writer.configure(state='readonly', textvariable=self.entry_3_writer_var)
        self._entry_3_writer.grid(column='0', row='2', sticky='ew')
        self._entry_3_writer.bind('<Button-1>', makeFocused, add='+')
        self._entry_3_writer.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_3_writer.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_3_writer.bind('<Return>', makeReadOnly, add='+')
        self._label_10_penciller = tk.Label(self._frame_3_people)
        self._label_10_penciller.configure(cursor='boat', state='disabled', text='Penciller')
        self._label_10_penciller.grid(column='0', row='3')
        self._entry_4_penciller = tk.Entry(self._frame_3_people)
        self._entry_4_penciller.configure(state='readonly', textvariable=self.entry_4_penciller_var)
        self._entry_4_penciller.grid(column='0', row='4', sticky='ew')
        self._entry_4_penciller.bind('<Button-1>', makeFocused, add='+')
        self._entry_4_penciller.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_4_penciller.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_4_penciller.bind('<Return>', makeReadOnly, add='+')
        self._label_11_Inker = tk.Label(self._frame_3_people)
        self._label_11_Inker.configure(compound='top', font='TkFixedFont', text='Inker')
        self._label_11_Inker.grid(column='0', row='5')
        self._entry_5_inker = tk.Entry(self._frame_3_people)
        self._entry_5_inker.configure(state='readonly', textvariable=self.entry_5_inker_var)
        self._entry_5_inker.grid(column='0', row='6', sticky='ew')
        self._entry_5_inker.bind('<Button-1>', makeFocused, add='+')
        self._entry_5_inker.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_5_inker.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_5_inker.bind('<Return>', makeReadOnly, add='+')
        self._label_12_colorist = tk.Label(self._frame_3_people)
        self._label_12_colorist.configure(text='Colorist')
        self._label_12_colorist.grid(column='0', row='7')
        self._entry_8_colorist = tk.Entry(self._frame_3_people)
        self._entry_8_colorist.configure(state='readonly', textvariable=self.entry_8_colorist_var)
        self._entry_8_colorist.grid(column='0', row='8', sticky='ew')
        self._entry_8_colorist.bind('<Button-1>', makeFocused, add='+')
        self._entry_8_colorist.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_8_colorist.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_8_colorist.bind('<Return>', makeReadOnly, add='+')
        self._label_13_letterist = tk.Label(self._frame_3_people)
        self._label_13_letterist.configure(text='Letterer')
        self._label_13_letterist.grid(column='0', row='9')
        self._entry_9_letterer = tk.Entry(self._frame_3_people)
        self._entry_9_letterer.configure(state='readonly', textvariable=self.entry_9_letterer_var)
        self._entry_9_letterer.grid(column='0', row='10', sticky='ew')
        self._entry_9_letterer.bind('<Button-1>', makeFocused, add='+')
        self._entry_9_letterer.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_9_letterer.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_9_letterer.bind('<Return>', makeReadOnly, add='+')
        self._label_14_coverArtist = tk.Label(self._frame_3_people)
        self._label_14_coverArtist.configure(compound='top', text='Cover Artist')
        self._label_14_coverArtist.grid(column='0', row='11')
        self._entry_11_coverArtist = tk.Entry(self._frame_3_people)
        self._entry_11_coverArtist.configure(state='readonly', textvariable=self.entry_11_coverArtist_var)
        self._entry_11_coverArtist.grid(column='0', row='12', sticky='ew')
        self._entry_11_coverArtist.bind('<Button-1>', makeFocused, add='+')
        self._entry_11_coverArtist.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_11_coverArtist.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_11_coverArtist.bind('<Return>', makeReadOnly, add='+')
        self._label_15_editor = tk.Label(self._frame_3_people)
        self._label_15_editor.configure(text='Editor')
        self._label_15_editor.grid(column='0', row='13')
        self._entry_12_editor = tk.Entry(self._frame_3_people)
        self._entry_12_editor.configure(state='readonly', textvariable=self.entry_12_editor_var)
        self._entry_12_editor.grid(column='0', row='14', sticky='ew')
        self._entry_12_editor.bind('<Button-1>', makeFocused, add='+')
        self._entry_12_editor.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_12_editor.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_12_editor.bind('<Return>', makeReadOnly, add='+')
        self._label_16_publisher = tk.Label(self._frame_3_people)
        self._label_16_publisher.configure(text='Publisher')
        self._label_16_publisher.grid(column='0', row='15')
        self._entry_13_publisher = tk.Entry(self._frame_3_people)
        self._entry_13_publisher.configure(state='readonly', textvariable=self.entry_13_publisher_var)
        self._entry_13_publisher.grid(column='0', row='16', sticky='ew')
        self._entry_13_publisher.bind('<Button-1>', makeFocused, add='+')
        self._entry_13_publisher.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_13_publisher.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_13_publisher.bind('<Return>', makeReadOnly, add='+')
        self._label_17_imprint = tk.Label(self._frame_3_people)
        self._label_17_imprint.configure(text='Imprint')
        self._label_17_imprint.grid(column='0', row='17')
        self._entry_14_imprint = tk.Entry(self._frame_3_people)
        self._entry_14_imprint.configure(state='readonly', textvariable=self.entry_14_imprint_var)
        self._entry_14_imprint.grid(column='0', row='18', sticky='ew')
        self._entry_14_imprint.bind('<Button-1>', makeFocused, add='+')
        self._entry_14_imprint.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_14_imprint.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_14_imprint.bind('<Return>', makeReadOnly, add='+')
        self._label_23_characters = tk.Label(self._frame_3_people)
        self._label_23_characters.configure(text='Characters')
        self._label_23_characters.grid(column='0', row='19')
        self._entry_16_characters = tk.Entry(self._frame_3_people)
        self._entry_16_characters.configure(state='readonly', textvariable=self.entry_16_characters_var)
        self._entry_16_characters.grid(column='0', row='20')
        self._entry_16_characters.bind('<Button-1>', makeFocused, add='+')
        self._entry_16_characters.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_16_characters.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_16_characters.bind('<Return>', makeReadOnly, add='+')
        self._frame_3_people.configure(height='200', width='200')

        self._frame1.rowconfigure('1', pad='0')
        self._frame_3 = tk.Frame(self._frame1)
        self._label_18_genres = tk.Label(self._frame_3)
        self._label_18_genres.configure(text='Genres')
        self._label_18_genres.grid(column='0', row='0')
        self._frame_3.columnconfigure('0', weight='1')
        self._entry_15_genres = tk.Entry(self._frame_3)

        self._entry_15_genres.configure(state='readonly', textvariable=self.entry_15_genres_var)
        self._entry_15_genres.grid(column='0', row='1', sticky='ew')
        self._entry_15_genres.bind('<Button-1>', makeFocused, add='+')
        self._entry_15_genres.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_15_genres.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_15_genres.bind('<Return>', makeReadOnly, add='+')
        self._label_19_tags = tk.Label(self._frame_3)
        self._label_19_tags.configure(text='Tags')
        self._label_19_tags.grid(column='0', row='2')
        self._entry_16_tags = tk.Entry(self._frame_3)
        self._entry_16_tags.configure(state='readonly', textvariable=self.entry_16_tags_var)
        self._entry_16_tags.grid(column='0', row='3', sticky='ew')
        self._entry_16_tags.bind('<Button-1>', makeFocused, add='+')
        self._entry_16_tags.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_16_tags.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_16_tags.bind('<Return>', makeReadOnly, add='+')
        self._label_20_web = tk.Label(self._frame_3)
        self._label_20_web.configure(text='Web')
        self._label_20_web.grid(column='0', row='4')
        self._entry_17_web = tk.Entry(self._frame_3)
        self._entry_17_web.configure(state='readonly', textvariable=self.entry_17_web_var)
        self._entry_17_web.grid(column='0', row='5', sticky='ew')
        self._entry_17_web.bind('<Button-1>', makeFocused, add='+')
        self._entry_17_web.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_17_web.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_17_web.bind('<Return>', makeReadOnly, add='+')
        self._label_24_scanInfo = tk.Label(self._frame_3)
        self._label_24_scanInfo.configure(text='Scan Information')
        self._label_24_scanInfo.grid(column='0', row='6')
        self._entry_20_scanInfo = tk.Entry(self._frame_3)
        self._entry_20_scanInfo.configure(state='readonly', textvariable=self.entry_20_scanInfo_var)
        self._entry_20_scanInfo.grid(column='0', row='7', sticky='ew')
        self._entry_20_scanInfo.bind('<Button-1>', makeFocused, add='+')
        self._entry_20_scanInfo.bind('<Double-Button-1>', self.makeEditable, add='+')
        self._entry_20_scanInfo.bind('<FocusOut>', onFocusOut, add='+')
        self._entry_20_scanInfo.bind('<Return>', makeReadOnly, add='+')

        self._frame_1.rowconfigure("all", pad="5", weight=1)
        self._frame_1.columnconfigure("all", weight=1)

        self._frame_1.grid(column='1', ipadx='10', ipady='10', padx='20', pady='20', row='0', sticky='nsew')
        self._frame_4_leftColumn.rowconfigure("all", weight=1, pad="20")
        self._frame_4_leftColumn.columnconfigure("all", weight=1, pad="20")
        self._frame_4_leftColumn.grid(row=0, column=0, sticky="NSEW", rowspan=3)

        self._frame_2.grid(column=0, ipadx='10', ipady='10', padx='10', pady='20', row=0)
        self._frame_3.configure(height='200', width='200')
        self._frame_3.grid(column=1, ipadx='10', ipady='10', padx='20', pady='10', row=1, sticky='ew')
        self._frame_3_people.grid(column=0, ipadx='10', ipady='10', padx='10', row=1, sticky='ew', rowspan=2)

        # MAIN FRAME
        # self._frame_5_statusInfo = tk.Frame(self._frame1,bg="grey")
        self._label_28_statusinfo = tk.Label(self._frame1, text="", anchor="e", bg="lightgrey")
        self._label_28_statusinfo.grid(row=5, column=1, sticky=tk.E)

        # self._frame_5_statusInfo.grid(row=4, column=1, sticky=tk.W)

        self._frame1.configure(height='800', width='1080')
        self._frame1.pack(expand=tk.YES, fill=tk.BOTH)
        # column=0, row=0,sticky="nesw")
        master.rowconfigure('0', minsize='0')
        master.columnconfigure('0', minsize='0', uniform='None')

        # File Controller - Read,Save
        self._files_controller = tk.Frame(self._frame1)
        self.button2_openfile = tk.Button(self._files_controller, text="Open", command=self._open_files, width=15)
        self.button2_openfile.grid(column=0, row=0)
        # self.button3_read = tk.Button(self._files_controller, text="Read",
        # command=self.create_loadedComicInfo_list, width=15)
        # self.button3_read.grid(column=1, row=3, pady="5 10", columnspan=2)
        self.button4_save = tk.Button(self._files_controller, text="Save", command=self.do_save_UI, width=15)
        self.button4_save.grid(column=1, row=0)
        self.button4_save = tk.Button(self._files_controller, text="Remove ComicInfo.xml", command=self.deleteComicInfo,
                                      width=20)
        self.button4_save.grid(column=3, row=0)
        # self.__tkvar.set('Age Rating')
        self._files_controller.configure(pady=5)
        self._files_controller.grid(row=2, column=1)
        # Main widget
        self.mainwindow = self._frame1

        self.widgets_obj = [
            self._entry_1_seriesName,
            self._entry_2_title,
            self._entry_3_writer,
            self._entry_4_penciller,
            self._entry_5_inker,
            self._entry_6_storyArc,
            self._entry_7_SeriesGroup,
            self._entry_8_colorist,
            self._entry_9_letterer,
            self._entry_10_langIso,
            self._entry_11_coverArtist,
            self._entry_12_editor,
            self._entry_13_publisher,
            self._entry_14_imprint,
            self._entry_15_format,
            self._entry_16_characters,
            self._entry_17_web,
            self._optionmenu_2_blackWhite,
            self._optionmenu_3_manga,
            self._entry_20_scanInfo,
            self._spinbox_1_year,
            self._spinbox_2_month,
            self._spinbox_3_volume,
            self._spinbox_4_chapter,
            self._spinbox_5_pageCount,
            self._entry_16_tags,
            self._entry_15_genres,
            self.input_1_summary_obj.linked_text_field

        ]

        # self._frame1.configure(bg="blue")
        # self._frame_2.configure(bg="red")
        # self._frame_3.configure(bg="yellow")
        # self._frame_3_people.configure(bg="purple")
        # self._frame_1.configure(bg="green")

    def _reset_highlightedUI(self):
        for widget in self.highlighted_changes:
            if re.match(r".*(entry_volume|spinbox_chapter).*", str(widget)):
                widget.configure(highlightcolor="#FFF", highlightbackground="#FFF", highlightthickness="0",
                                 state="disabled")
            else:
                widget.configure(highlightcolor="#FFF", highlightbackground="#FFF", highlightthickness="0")
        self._label_28_statusinfo.configure(text="")
        try:
            self.input_1_summary_obj.linked_text_field = self._text_1_summary
        except:
            pass

    def run(self):
        self.mainwindow.mainloop()

    def _open_files(self):
        self._reset_highlightedUI()
        self.initialize_StringVars()

        self.selected_filenames = list[str]()
        covers_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                                   filetypes=(("CBZ Files", ".cbz"),)
                                                   # ("Zip files", ".zip"))
                                                   )
        for file in covers_path_list:
            self.selected_filenames.append(file.name)
        self.create_loadedComicInfo_list()
        self._label_28_statusinfo.configure(text="Successfuly loaded")

    def create_loadedComicInfo_list(self, cli_selected_files: list[str] = None):
        self.conflicts = {}

        def load_comicinfo_xml(cls, cbz_path) -> LoadedComicInfo:
            """
            Accepts a path string
            Returns a LoadedComicInfo with the ComicInfo class generated from the data contained inside ComicInfo file
            which is taken from the zip-like file type

            :param cls: parent self
            :param string cbz_path: the path to the zip-like file
            :return: LoadedComicInfo: LoadedComicInfo
            """
            logger.info(f"loading file: '{cbz_path}'")
            try:
                # raise CorruptedComicInfo(cbz_path)
                comicinfo = ReadComicInfo(cbz_path).to_ComicInfo(False)
            except NoMetadataFileFound:
                logger.warning(f"Metadata file 'ComicInfo.xml' not found inside {cbz_path}\n"
                               f"One will be created when saving changes to file.\n"
                               f"This applies to all future errors")
                if not cls.warning_metadataNotFound:
                    mb.showerror("Error reading ComicInfo",
                                 f"ComicInfo.xml was not found inside: {cbz_path}\n"
                                 f"One will be created when saving changes to file.\n"
                                 f"This applies to all future errors")
                    cls.warning_metadataNotFound = True
                comicinfo = ComicInfo.ComicInfo()
            except XMLSyntaxError as e:
                logger.error(f"There was an error loading ComicInfo.xml from file: {cbz_path}", exc_info=e)
                mb.showerror("Error reading ComicInfo", "Error loading file."
                                                        f"Can't loadComicInfo.xml from file: {cbz_path}\n\n" + str(e))
                raise e

            except CorruptedComicInfo as e:
                logger.error(f"There was an error loading ComicInfo.xml from file: {cbz_path}", exc_info=e)
                if self._initialized_UI:
                    answer = mb.askyesno("Failed to load metadata",
                                         f"Failed to load metadata from file:\n{cbz_path}\n\n"
                                         "ComicInfo.xml file was found but seems corrupted.\n"
                                         "A fix was attempted but it failed.\n\n"
                                         "Continue loading?")
                    if answer:
                        return
                    else:
                        raise CancelComicInfoLoad
                raise CorruptedComicInfo
            loadedInfo = LoadedComicInfo(cbz_path, comicinfo, comicinfo)
            logger.debug("comicinfo was read and a LoadedComicInfo was created")
            #
            # """
            # Loads LoadedComicInfo.comicInfoObj into StringVar, so it can be modified in the UI.
            # Used for cli mode even if there's no UI present.
            #
            # :param LoadedComicInfo loadedInfo:
            # """

            comicinfo_attrib_get = [
                loadedInfo.comicInfoObj.get_Series,
                loadedInfo.comicInfoObj.get_Title,
                loadedInfo.comicInfoObj.get_Writer,
                loadedInfo.comicInfoObj.get_Penciller,
                loadedInfo.comicInfoObj.get_Inker,
                loadedInfo.comicInfoObj.get_StoryArc,
                loadedInfo.comicInfoObj.get_SeriesGroup,
                loadedInfo.comicInfoObj.get_Colorist,
                loadedInfo.comicInfoObj.get_Letterer,
                loadedInfo.comicInfoObj.get_LanguageISO,
                loadedInfo.comicInfoObj.get_CoverArtist,
                loadedInfo.comicInfoObj.get_Editor,
                loadedInfo.comicInfoObj.get_Publisher,
                loadedInfo.comicInfoObj.get_Imprint,
                loadedInfo.comicInfoObj.get_Format,
                loadedInfo.comicInfoObj.get_Characters,
                loadedInfo.comicInfoObj.get_Web,
                loadedInfo.comicInfoObj.get_BlackAndWhite,
                loadedInfo.comicInfoObj.get_Manga,
                loadedInfo.comicInfoObj.get_ScanInformation,
                loadedInfo.comicInfoObj.get_Year,
                loadedInfo.comicInfoObj.get_Month,
                loadedInfo.comicInfoObj.get_Volume,
                loadedInfo.comicInfoObj.get_Number,
                loadedInfo.comicInfoObj.get_PageCount,
                loadedInfo.comicInfoObj.get_Tags,
                loadedInfo.comicInfoObj.get_Genre,
                loadedInfo.comicInfoObj.get_Summary
            ]

            comicinfo_attrib_set = [
                loadedInfo.comicInfoObj.set_Series,
                loadedInfo.comicInfoObj.set_Title,
                loadedInfo.comicInfoObj.set_Writer,
                loadedInfo.comicInfoObj.set_Penciller,
                loadedInfo.comicInfoObj.set_Inker,
                loadedInfo.comicInfoObj.set_StoryArc,
                loadedInfo.comicInfoObj.set_SeriesGroup,
                loadedInfo.comicInfoObj.set_Colorist,
                loadedInfo.comicInfoObj.set_Letterer,
                loadedInfo.comicInfoObj.set_LanguageISO,
                loadedInfo.comicInfoObj.set_CoverArtist,
                loadedInfo.comicInfoObj.set_Editor,
                loadedInfo.comicInfoObj.set_Publisher,
                loadedInfo.comicInfoObj.set_Imprint,
                loadedInfo.comicInfoObj.set_Format,
                loadedInfo.comicInfoObj.set_Characters,
                loadedInfo.comicInfoObj.set_Web,
                loadedInfo.comicInfoObj.set_BlackAndWhite,
                loadedInfo.comicInfoObj.set_Manga,
                loadedInfo.comicInfoObj.set_ScanInformation,
                loadedInfo.comicInfoObj.set_Year,
                loadedInfo.comicInfoObj.set_Month,
                loadedInfo.comicInfoObj.set_Volume,
                loadedInfo.comicInfoObj.set_Number,
                loadedInfo.comicInfoObj.set_PageCount,
                loadedInfo.comicInfoObj.set_Tags,
                loadedInfo.comicInfoObj.set_Genre,
                loadedInfo.comicInfoObj.set_Summary
            ]

            if cls.widgets_obj:  # Initializing UI is optional. If there is no ui then there's no widgets neither.
                widgets_var_zip = zip(cls.widgets_var, comicinfo_attrib_get, comicinfo_attrib_set, cls.widgets_obj)
                cls._initialized_UI = True
            else:
                widgets_var_zip = zip(cls.widgets_var, comicinfo_attrib_get, comicinfo_attrib_set)
                cls._initialized_UI = False

            # Load the comic info into our StringVar and IntVar, so they can be modified in the ui
            cls.conflict_chapter = False
            for widgets_var_tuple in widgets_var_zip:

                widgetvar = widgets_var_tuple[0]
                comicinfo_atr_get = widgets_var_tuple[1]()
                # comicinfo_atr_set = widgets_var_tuple[2]

                # field is empty. Skipping
                if (widgetvar.get() != comicinfo_atr_get) and widgetvar.get() in (-1, 0, "", "Unknown", None):
                    #  If field is chapter skip them.
                    #  We don't want to mess up chapter overwriting the same value to all files
                    if str(widgetvar) == "Number" and cls.conflict_chapter:
                        if self.spinbox_4_chapter_var.get() != widgetvar.get():
                            cls.conflict_chapter = True
                            self.spinbox_4_chapter_var.set("")

                        continue
                    widgetvar.set(comicinfo_atr_get)
                    logger.debug(
                        f"Loaded new value for tag '{widgetvar}'")
                # Conflict. UI and ComicInfo not the same.
                elif widgetvar.get() != comicinfo_atr_get:
                    if str(widgetvar) == "Number" and cls.conflict_chapter:
                        logger.debug("Skipping chapter field due to conflict")
                        continue
                    # Empty variable since they don't match.
                    # This way when saving, original value will be kept.
                    # If user edits in the ui, warning will appear: The field in all selected files will be the same
                    if isinstance(widgetvar, tk.StringVar):
                        widgetvar.set("")
                    elif isinstance(widgetvar, tk.IntVar):
                        if str(widgetvar) == "pageCount":
                            widgetvar.set(0)
                        elif str(widgetvar) == "blackWhite" or str(widgetvar) == "manga" or str(
                                widgetvar) == "ageRating":
                            widgetvar.set("Unknown")
                        else:
                            widgetvar.set(-1)
                    elif isinstance(widgetvar, models.LongText):
                        widgetvar.set("")

                    else:
                        logger.warning(f"Unrecognised type \n{str(widgetvar)}\n{widgetvar}")

                    if cls._initialized_UI:  # For the items that are different, highlight in orane if ui is initialized
                        widgetobj = widgets_var_tuple[3]  # This is the actual widget, not the variable
                        logger.debug("++#############++")
                        logger.debug(comicinfo_atr_get)
                        logger.debug(widgetvar.get())
                        logger.debug("__#############__")
                        widgetobj.configure(highlightbackground='orange', highlightcolor="orange",
                                            highlightthickness='3')
                        cls.highlighted_changes.append(widgetobj)

                    if str(widgetvar) == "Number" and cls.conflict_chapter:
                        cls.conflict_chapter = True
                    logger.debug(
                        f"Conflict betwen comicinfo and UI for tag '{str(widgetvar)}'. Content does not match.")
                else:
                    logger.debug(
                        f"Content in comicinfo and UI for tag '{str(widgetvar)}' is the same, skipping")

            return loadedInfo

        try:
            if not self.selected_filenames:
                if cli_selected_files:
                    for file in cli_selected_files:
                        try:
                            loaded_ComIinf = load_comicinfo_xml(self, file)
                        except XMLSyntaxError:
                            # This is already logged. Exception is raised again so it excepts on CLI mode
                            continue
                        except CorruptedComicInfo:
                            # This is already logged. Exception is raised again so it excepts on CLI mode
                            continue
                        if loaded_ComIinf:
                            self.loadedComicInfo_list.append(loaded_ComIinf)
                        else:
                            continue
                    # self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
                else:
                    raise Exception("No files selected")
            else:
                logger.debug("Selected files UI:" + "".join(self.selected_filenames))
                for file_path in self.selected_filenames:
                    loaded_ComIinf = load_comicinfo_xml(self, file_path)

                    if loaded_ComIinf:
                        self.loadedComicInfo_list.append(loaded_ComIinf)
                    else:
                        continue
                    # self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        except CancelComicInfoLoad:
            self.loadedComicInfo_list = []

    def parseUI_toComicInfo(self, forceVolume=False):
        """
        Modifies every ComicInfo loaded with values from the UI
        """

        def parse_UI_toComicInfo(cls, loadedInfo: LoadedComicInfo, doForceVolume) -> LoadedComicInfo:
            """
            Accepts a path string
            Returns a LoadedComicInfo with the modified ComicInfo from the modified StringVars

            """
            logger.debug(f"parsing UI to file: '{loadedInfo.path}'")

            comicinfo_attrib_get = [
                loadedInfo.comicInfoObj.get_Series,
                loadedInfo.comicInfoObj.get_Title,
                loadedInfo.comicInfoObj.get_Writer,
                loadedInfo.comicInfoObj.get_Penciller,
                loadedInfo.comicInfoObj.get_Inker,
                loadedInfo.comicInfoObj.get_StoryArc,
                loadedInfo.comicInfoObj.get_SeriesGroup,
                loadedInfo.comicInfoObj.get_Colorist,
                loadedInfo.comicInfoObj.get_Letterer,
                loadedInfo.comicInfoObj.get_LanguageISO,
                loadedInfo.comicInfoObj.get_CoverArtist,
                loadedInfo.comicInfoObj.get_Editor,
                loadedInfo.comicInfoObj.get_Publisher,
                loadedInfo.comicInfoObj.get_Imprint,
                loadedInfo.comicInfoObj.get_Format,
                loadedInfo.comicInfoObj.get_Characters,
                loadedInfo.comicInfoObj.get_Web,
                loadedInfo.comicInfoObj.get_BlackAndWhite,
                loadedInfo.comicInfoObj.get_Manga,
                loadedInfo.comicInfoObj.get_ScanInformation,
                loadedInfo.comicInfoObj.get_Year,
                loadedInfo.comicInfoObj.get_Month,
                loadedInfo.comicInfoObj.get_Volume,
                loadedInfo.comicInfoObj.get_Number,
                loadedInfo.comicInfoObj.get_PageCount,
                loadedInfo.comicInfoObj.get_Tags,
                loadedInfo.comicInfoObj.get_Genre,
                loadedInfo.comicInfoObj.get_Summary

            ]
            comicinfo_attrib_set = [
                loadedInfo.comicInfoObj.set_Series,
                loadedInfo.comicInfoObj.set_Title,
                loadedInfo.comicInfoObj.set_Writer,
                loadedInfo.comicInfoObj.set_Penciller,
                loadedInfo.comicInfoObj.set_Inker,
                loadedInfo.comicInfoObj.set_StoryArc,
                loadedInfo.comicInfoObj.set_SeriesGroup,
                loadedInfo.comicInfoObj.set_Colorist,
                loadedInfo.comicInfoObj.set_Letterer,
                loadedInfo.comicInfoObj.set_LanguageISO,
                loadedInfo.comicInfoObj.set_CoverArtist,
                loadedInfo.comicInfoObj.set_Editor,
                loadedInfo.comicInfoObj.set_Publisher,
                loadedInfo.comicInfoObj.set_Imprint,
                loadedInfo.comicInfoObj.set_Format,
                loadedInfo.comicInfoObj.set_Characters,
                loadedInfo.comicInfoObj.set_Web,
                loadedInfo.comicInfoObj.set_BlackAndWhite,
                loadedInfo.comicInfoObj.set_Manga,
                loadedInfo.comicInfoObj.set_ScanInformation,
                loadedInfo.comicInfoObj.set_Year,
                loadedInfo.comicInfoObj.set_Month,
                loadedInfo.comicInfoObj.set_Volume,
                loadedInfo.comicInfoObj.set_Number,
                loadedInfo.comicInfoObj.set_PageCount,
                loadedInfo.comicInfoObj.set_Tags,
                loadedInfo.comicInfoObj.set_Genre,
                loadedInfo.comicInfoObj.set_Summary
            ]

            if cls.widgets_obj:  # Initializing UI is optional. If there is no ui then there's no widgets neither.
                widgets_var_zip = zip(cls.widgets_var, comicinfo_attrib_get, comicinfo_attrib_set, cls.widgets_obj)
                cls._initialized_UI = True
            else:
                widgets_var_zip = zip(cls.widgets_var, comicinfo_attrib_get, comicinfo_attrib_set)
                cls._initialized_UI = False

            # Load the comic info into our StringVar and IntVar, so they can be modified in the ui
            for widgets_var_tuple in widgets_var_zip:
                widgetvar = widgets_var_tuple[0]
                comicinfo_atr_get = widgets_var_tuple[1]
                comicinfo_atr_set = widgets_var_tuple[2]

                if widgetvar.get() != comicinfo_atr_get() and widgetvar.get() not in (-1, 0, "", "Unknown", None):
                    comicinfo_atr_set(widgetvar.get())
                else:
                    if str(widgetvar) == "volume" and doForceVolume:
                        comicinfo_atr_set(-1)
                    elif str(widgetvar) == "volume" and self.spinbox_3_volume_var_isModified:
                        comicinfo_atr_set(widgetvar.get())
                    elif str(widgetvar) == "Number" and cls.spinbox_4_chapter_var_isModified:
                        comicinfo_atr_set(widgetvar.get())

            return loadedInfo

        modified_loadedComicInfo_list = []
        # modified_loadedComicInfo_XML_list = list[str]()
        for comicObj in self.loadedComicInfo_list:
            modified_loadedComicInfo = parse_UI_toComicInfo(self, comicObj, doForceVolume=forceVolume)
            modified_loadedComicInfo_list.append(modified_loadedComicInfo)
            self.loadedComicInfo_list = modified_loadedComicInfo_list

    def saveComicInfo(self):
        total_times_count = len(self.loadedComicInfo_list)
        start_time = time.time()
        processed_counter = 0
        processed_errors = 0

        if self._initialized_UI:
            self.frame_1_progressbar = tk.Frame(self._files_controller)
            self.frame_1_progressbar.grid(row=1, columnspan=4)
            # TBH I'd like to rework how this processing bar works. - Promidius
            pb_root = self.frame_1_progressbar

            style = ttk.Style(pb_root)
            style.layout('text.Horizontal.TProgressbar',
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
            pb = ttk.Progressbar(pb_root, length=400, style='text.Horizontal.TProgressbar',
                                 mode="determinate")  # create progress bar
            style.configure('text.Horizontal.TProgressbar', text='0 %', anchor='center')
            label_progress_text = tk.StringVar()
            pb_text = tk.Label(pb_root, textvariable=label_progress_text, anchor=tk.W)
            logger.info("Initialized progress bar")
            pb.grid(row=0, column=0, sticky=tk.E + tk.W)
            pb_text.grid(row=1, column=0, sticky=tk.E)
            label_progress_text.set(
                f"Processed: {(processed_counter + processed_errors)}/{total_times_count} files - {processed_errors} errors\n"
                f"Elapsed time  : {get_elapsed_time(start_time)}\n"
                f"Estimated time: {get_estimated_time(start_time, processed_counter, total_times_count)}")

        for loadedComicObj in self.loadedComicInfo_list:
            print("Started thread")

            logger.info(f"[Processing] Starting processing to save data to file {loadedComicObj.path}")
            # The following Try/Catch looks awful
            # TODO: redo this in a better way
            try:
                WriteComicInfo(loadedComicObj).to_file()
                if self._initialized_UI:
                    label_progress_text.set(
                        f"Processed: {(processed_counter + processed_errors)}/{total_times_count} files - {processed_errors} errors\n"
                        f"Elapsed time  : {get_elapsed_time(start_time)}\n"
                        f"Estimated time: {get_estimated_time(start_time, processed_counter, total_times_count)}")
                processed_counter += 1
            except FileExistsError as e:
                if self._initialized_UI:
                    mb.showwarning(f"[ERROR] File already exists",
                                   f"Trying to create:\n`{str(e.filename2)}` but already exists\n\nException:\n{e}")

                logger.error("[ERROR] File already exists\n"
                             f"Trying to create:\n`{str(e.filename2)}` but already exists\nException:\n{e}")
                if not self._initialized_UI:
                    raise e
                else:
                    continue
            except PermissionError as e:
                if self._initialized_UI:
                    mb.showerror("[ERROR] Permission Error",
                                 "Can't access the file because it's being used by a different process\n\n"
                                 f"Exception:\n{e}")

                logger.error("[ERROR] Permission Error"
                             "Can't access the file because it's being used by a different process\n"
                             f"Exception:\n{str(e)}")
                processed_errors += 1
                if not self._initialized_UI:
                    raise e
                else:
                    continue
            except FileNotFoundError as e:
                if self._initialized_UI:
                    mb.showerror("[ERROR] File Not Found",
                                 "Can't access the file because it's being used by a different process\n\n"
                                 f"Exception:\n{str(e)}")

                logger.error("[ERROR] File Not Found\n"
                             "Can't access the file because it's being used by a different process\n"
                             f"Exception:\n{str(e)}")
                processed_errors += 1
                if not self._initialized_UI:
                    raise e
                else:
                    continue
            except Exception as e:
                if self._initialized_UI:
                    mb.showerror("Something went wrong", "Error processing. Check logs.")
                logger.critical("Exception Processing", e)
                raise e
            if self._initialized_UI:
                pb_root.update()
                percentage = ((processed_counter + processed_errors) / total_times_count) * 100
                style.configure('text.Horizontal.TProgressbar',
                                text='{:g} %'.format(round(percentage, 2)))  # update label
                pb['value'] = percentage
                label_progress_text.set(
                    f"Processed: {(processed_counter + processed_errors)}/{total_times_count} files - {processed_errors} errors\n"
                    f"Elapsed time  : {get_elapsed_time(start_time)}\n"
                    f"Estimated time: {get_estimated_time(start_time, processed_counter, total_times_count)}")

    def deleteComicInfo(self):
        """
        Deletes all ComicInfo.xml from the selected files
        """
        if self._initialized_UI:
            answer = mb.askokcancel("Warning", "This will remove 'ComicInfo.xml' file from the selected files")
            if answer:
                for loadedComicObj in self.loadedComicInfo_list:
                    logger.info("Processing delete")
                    WriteComicInfo(loadedComicObj).delete()
        else:
            for loadedComicObj in self.loadedComicInfo_list:
                logger.info("Processing delete")
                WriteComicInfo(loadedComicObj).delete()

    def do_save_UI(self):
        self.parseUI_toComicInfo()
        self.saveComicInfo()
