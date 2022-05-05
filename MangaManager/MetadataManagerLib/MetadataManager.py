#!/usr/bin/env python3
from __future__ import annotations

if __name__ == '__main__':
    import logging
    import os.path
    import pathlib
    import sys
    import cbz_handler
    from ComicInfo import ComicInfo
    from errors import NoFilesSelected, NoComicInfoLoaded
    from models import LoadedComicInfo
    import argparse


    def is_dir_path(path):

        if os.path.isfile(path):
            return path
        else:
            raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
else:
    import logging
    import os
    import pathlib
    import tkinter as tk
    from tkinter import filedialog
    from tkinter import messagebox as mb
    from tkinter import ttk
    from tkinter.scrolledtext import ScrolledText
    from ScrolledFrame import ScrolledFrame
    from lxml.etree import XMLSyntaxError

    from CommonLib.ProgressBarWidget import ProgressBar
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


    def get_gettersArray(ComicInfoObject):
        # self.widgets_var = [
        #     {
        #     self.entry_Title_val,
        #     self.entry_Series_val,
        #     self.entry_LocalizedSeries_val,
        #     self.entry_SeriesSort_val,
        #     self.entry_AlternateSeries_val,
        #     self.input_1_summary_obj,
        #     self.entry_Notes_val,
        #     self.entry_Genre_val,
        #     self.entry_Tags_val,
        #     self.entry_Web_val,
        #     self.entry_SeriesGroup_val,
        #     self.entry_AgeRating_val,
        #     self.entry_CommunityRating_val,
        #     self.entry_ScanInformation_val,
        #     self.entry_StoryArc_val,
        #
        #     self.entry_Writer_val,
        #     self.entry_Inker_val,
        #     self.entry_Colorist_val,
        #     self.entry_Letterer_val,
        #     self.entry_CoverArtist_val,
        #     self.entry_Editor_val,
        #     self.entry_Translator_val,
        #     self.entry_Publisher_val,
        #     self.entry_Imprint_val,
        #     self.entry_Characters_val,
        #     self.entry_Teams_val,
        #     self.entry_Locations_val,}
        #
        #     self.entry_Number_val,
        #     self.entry_AlternateNumber_val,
        #     self.entry_Count_val,
        #     self.entry_AlternateCount_val,
        #     self.entry_Volume_val,
        #     self.entry_PageCount_val,
        #     self.entry_Year_val,
        #     self.entry_Month_val,
        #     self.entry_Day_val,
        #     self.entry_Format_val,
        #     self.entry_LanguageISO_val,
        #     self.entry_BlackAndWhite_val,
        #     self.entry_Manga_val,
        #     self.entry_StoryArcNumber_val
        #
        # ]
        return [
            ComicInfoObject.get_Title,
            ComicInfoObject.get_Series,
            ComicInfoObject.get_LocalizedSeries,
            ComicInfoObject.get_SeriesSort,
            ComicInfoObject.get_AlternateSeries,
            ComicInfoObject.get_Summary,
            ComicInfoObject.get_Notes,
            ComicInfoObject.get_Genre,
            ComicInfoObject.get_Tags,
            ComicInfoObject.get_Web,
            ComicInfoObject.get_SeriesGroup,
            ComicInfoObject.get_AgeRating,
            ComicInfoObject.get_CommunityRating,
            ComicInfoObject.get_ScanInformation,
            ComicInfoObject.get_StoryArc,
            ComicInfoObject.get_Writer,
            ComicInfoObject.get_Inker,
            ComicInfoObject.get_Colorist,
            ComicInfoObject.get_Letterer,
            ComicInfoObject.get_CoverArtist,
            ComicInfoObject.get_Editor,
            ComicInfoObject.get_Translator,
            ComicInfoObject.get_Publisher,
            ComicInfoObject.get_Imprint,
            ComicInfoObject.get_Characters,
            ComicInfoObject.get_Teams,
            ComicInfoObject.get_Locations,
            ComicInfoObject.get_Number,
            ComicInfoObject.get_AlternateNumber,
            ComicInfoObject.get_Count,
            ComicInfoObject.get_AlternateCount,
            ComicInfoObject.get_Volume,
            ComicInfoObject.get_PageCount,
            ComicInfoObject.get_Year,
            ComicInfoObject.get_Month,
            ComicInfoObject.get_Day,
            ComicInfoObject.get_Format,
            ComicInfoObject.get_LanguageISO,
            ComicInfoObject.get_BlackAndWhite,
            ComicInfoObject.get_Manga,
            ComicInfoObject.get_StoryArcNumber
        ]


    def get_settersArray(ComicInfoObject):
        return [
            ComicInfoObject.set_Title,
            ComicInfoObject.set_Series,
            ComicInfoObject.set_LocalizedSeries,
            ComicInfoObject.set_SeriesSort,
            ComicInfoObject.set_AlternateSeries,
            ComicInfoObject.set_Summary,
            ComicInfoObject.set_Notes,
            ComicInfoObject.set_Genre,
            ComicInfoObject.set_Tags,
            ComicInfoObject.set_Web,
            ComicInfoObject.set_SeriesGroup,
            ComicInfoObject.set_AgeRating,
            ComicInfoObject.set_CommunityRating,
            ComicInfoObject.set_ScanInformation,
            ComicInfoObject.set_StoryArc,
            ComicInfoObject.set_Writer,
            ComicInfoObject.set_Inker,
            ComicInfoObject.set_Colorist,
            ComicInfoObject.set_Letterer,
            ComicInfoObject.set_CoverArtist,
            ComicInfoObject.set_Editor,
            ComicInfoObject.set_Translator,
            ComicInfoObject.set_Publisher,
            ComicInfoObject.set_Imprint,
            ComicInfoObject.set_Characters,
            ComicInfoObject.set_Teams,
            ComicInfoObject.set_Locations,
            ComicInfoObject.set_Number,
            ComicInfoObject.set_AlternateNumber,
            ComicInfoObject.set_Count,
            ComicInfoObject.set_AlternateCount,
            ComicInfoObject.set_Volume,
            ComicInfoObject.set_PageCount,
            ComicInfoObject.set_Year,
            ComicInfoObject.set_Month,
            ComicInfoObject.set_Day,
            ComicInfoObject.set_Format,
            ComicInfoObject.set_LanguageISO,
            ComicInfoObject.set_BlackAndWhite,
            ComicInfoObject.set_Manga,
            ComicInfoObject.set_StoryArcNumber]





class App:
    def __init__(self, master: tk.Tk = None, disable_metadata_notFound_warning=False):
        self.master = master
        # self.master.eval('tk::PlaceWindow . center')
        self.highlighted_changes = []
        self._initialized_UI = False
        self.widgets_obj = []
        self.spinbox_4_chapter_var_isModified = False
        self.spinbox_3_volume_var_isModified = False
        self.warning_metadataNotFound = disable_metadata_notFound_warning
        self.selected_filenames = []
        self.loadedComicInfo_list = list[LoadedComicInfo]()

        self.entry_Title_val = tk.StringVar(value='', name="title")
        self.entry_Series_val = tk.StringVar(value='', name="Series")
        self.entry_LocalizedSeries_val = tk.StringVar(value='', name="LocalizedSeries")
        self.entry_SeriesSort_val = tk.StringVar(value='', name="SeriesSort")
        self.entry_AlternateSeries_val = tk.StringVar(value='', name="AlternateSeries")
        self.entry_Notes_val = tk.StringVar(value='', name="Notes")
        self.entry_Genre_val = tk.StringVar(value='', name="Genre")
        self.entry_Tags_val = tk.StringVar(value='', name="Tags")
        self.entry_Web_val = tk.StringVar(value='', name="Web")
        self.entry_SeriesGroup_val = tk.StringVar(value='', name="SeriesGroup")
        self.entry_AgeRating_val = tk.StringVar(value="Unknown", name="OptionMenu_AgeRating")
        self.entry_CommunityRating_val = tk.StringVar(value='', name="CommunityRating")
        self.entry_ScanInformation_val = tk.StringVar(value='', name="ScanInformation")
        self.entry_StoryArc_val = tk.StringVar(value='', name="StoryArc")
        self.entry_Writer_val = tk.StringVar(value='', name="Writer")
        self.entry_Inker_val = tk.StringVar(value='', name="Inker")
        self.entry_Colorist_val = tk.StringVar(value='', name="Colorist")
        self.entry_Letterer_val = tk.StringVar(value='', name="Letterer")
        self.entry_CoverArtist_val = tk.StringVar(value='', name="CoverArtist")
        self.entry_Editor_val = tk.StringVar(value='', name="Editor")
        self.entry_Translator_val = tk.StringVar(value='', name="Translator")
        self.entry_Publisher_val = tk.StringVar(value='', name="Publisher")
        self.entry_Imprint_val = tk.StringVar(value='', name="Imprint")
        self.entry_Characters_val = tk.StringVar(value='', name="Characters")
        self.entry_Teams_val = tk.StringVar(value='', name="Teams")
        self.entry_Locations_val = tk.StringVar(value='', name="Locations")
        self.entry_Number_val = tk.StringVar(value='', name="Number")
        self.entry_AlternateNumber_val = tk.StringVar(value='', name="AlternateNumber")
        self.entry_Format_val = tk.StringVar(value='', name="Format")
        self.entry_LanguageISO_val = tk.StringVar(value='', name="LanguageISO")
        # self.__tkvar = tk.StringVar(value='Unknown')
        self.entry_StoryArcNumber_val = tk.StringVar(value="", name="StoryArcNumber")
        self.input_1_summary_obj = models.LongText(name="summary")
        self.entry_BlackAndWhite_val = tk.StringVar(name="OptionMenu_BlackWhite", value="Unknown")
        self.entry_Manga_val = tk.StringVar(name="OptionMenu_Manga", value="Unknown")
        self.entry_Count_val = tk.IntVar(value=-1, name="Count")
        self.entry_AlternateCount_val = tk.IntVar(value=-1, name="AlternateCount")
        self.entry_Volume_val = tk.IntVar(value=-1, name="Volume")
        self.entry_PageCount_val = tk.IntVar(value=0, name="PageCount")
        self.entry_Year_val = tk.IntVar(value=-1, name="Year")
        self.entry_Month_val = tk.IntVar(value=-1, name="Month")
        self.entry_Day_val = tk.IntVar(value=-1, name="Day")
        try:
            self.input_1_summary_obj.linked_text_field = self.tkinterscrolledtext_1
        except:
            pass
        self.widgets_var = [
            self.entry_Title_val,
            self.entry_Series_val,
            self.entry_LocalizedSeries_val,
            self.entry_SeriesSort_val,
            self.entry_AlternateSeries_val,
            self.input_1_summary_obj,
            self.entry_Notes_val,
            self.entry_Genre_val,
            self.entry_Tags_val,
            self.entry_Web_val,
            self.entry_SeriesGroup_val,
            self.entry_AgeRating_val,
            self.entry_CommunityRating_val,
            self.entry_ScanInformation_val,
            self.entry_StoryArc_val,

            self.entry_Writer_val,
            self.entry_Inker_val,
            self.entry_Colorist_val,
            self.entry_Letterer_val,
            self.entry_CoverArtist_val,
            self.entry_Editor_val,
            self.entry_Translator_val,
            self.entry_Publisher_val,
            self.entry_Imprint_val,
            self.entry_Characters_val,
            self.entry_Teams_val,
            self.entry_Locations_val,

            self.entry_Number_val,
            self.entry_AlternateNumber_val,
            self.entry_Count_val,
            self.entry_AlternateCount_val,
            self.entry_Volume_val,
            self.entry_PageCount_val,
            self.entry_Year_val,
            self.entry_Month_val,
            self.entry_Day_val,
            self.entry_Format_val,
            self.entry_LanguageISO_val,
            self.entry_BlackAndWhite_val,
            self.entry_Manga_val,
            self.entry_StoryArcNumber_val

        ]

    def initialize_StringVars(self):
        self.highlighted_changes = []
        self.conflict_chapter = False

        self.entry_Title_val.set('')
        self.entry_Series_val.set('')
        self.entry_LocalizedSeries_val.set('')
        self.entry_SeriesSort_val.set('')
        self.entry_AlternateSeries_val.set('')
        self.entry_Notes_val.set('')
        self.entry_Genre_val.set('')
        self.entry_Tags_val.set('')
        self.entry_Web_val.set('')
        self.entry_SeriesGroup_val.set('')
        self.entry_AgeRating_val.set("Unknown")
        self.entry_CommunityRating_val.set('')
        self.entry_ScanInformation_val.set('')
        self.entry_StoryArc_val.set('')
        self.entry_Writer_val.set('')
        self.entry_Inker_val.set('')
        self.entry_Colorist_val.set('')
        self.entry_Letterer_val.set('')
        self.entry_CoverArtist_val.set('')
        self.entry_Editor_val.set('')
        self.entry_Translator_val.set('')
        self.entry_Publisher_val.set('')
        self.entry_Imprint_val.set('')
        self.entry_Characters_val.set('')
        self.entry_Teams_val.set('')
        self.entry_Locations_val.set('')
        self.entry_Number_val.set('')
        self.entry_AlternateNumber_val.set('')
        self.entry_Format_val.set('')
        self.entry_LanguageISO_val.set('')
        # self.__tkvar.set('Unknown')
        self.entry_StoryArcNumber_val.set("")
        self.entry_BlackAndWhite_val.set("Unknown")
        self.entry_Manga_val.set("Unknown")
        self.entry_Count_val.set(-1)
        self.entry_AlternateCount_val.set(-1)
        self.entry_Volume_val.set(-1)
        self.entry_PageCount_val.set(0)
        self.entry_Year_val.set(-1)
        self.entry_Month_val.set(-1)
        self.entry_Day_val.set(-1)

        self.input_1_summary_obj.set("")

    def _get_widgets_var_zip(self, widgets_variable_list, comicInfoObj: ComicInfo.ComicInfo, widgets_object_list=None):
        getters_array = get_gettersArray(comicInfoObj)
        setters_array = get_settersArray(comicInfoObj)
        if widgets_object_list:  # Initializing UI is optional. If there is no ui then there's no widgets neither.
            return zip(widgets_variable_list, getters_array,
                       setters_array, widgets_object_list)
        else:
            return zip(widgets_variable_list, getters_array,
                       setters_array)

    def makeEditable(self, event: tk.Event = None):
        pass

    def start_ui(self):
        master = self.master

        def makeReadOnly(event: tk.Event = None):
            # # <Return>
            # if event.widget.cget('state') == "disabled":
            #     return
            # if isinstance(event.widget, ttk.Combobox):
            #     event.widget.configure(state="readonly")
            pass

        def makeFocused(event: tk.Event = None):
            # <Button-1>
            # event.widget.focus()
            pass

        def onFocusOut(event: tk.Event = None):
            # <FocusOut>
            # makeReadOnly(event)
            pass

        def ValidateIfNum(s, S):
            dummy = s
            # disallow anything but numbers
            valid = S == '' or S.isdigit() or S == "."
            if not valid:
                self.frame_1.bell()
                # logger.info("input not valid")
            return valid

        self._initialized_UI = True
        # vldt_ifnum_cmd = (self.master.register(ValidateIfNum), '%s', '%S')
        self._edit_warning = False  # We send warning that changing chapter or volume will be set to all files selected
        self.frame_1 = tk.Frame(master)

        # build ui
        # build ui
        self.frame_1 = tk.Frame(master)
        self._frame_3 = tk.Frame(self.frame_1)

        self._button_1 = tk.Button(self._frame_3)
        self._button_1.configure(text='Open', command=self._open_files, width='10')
        self._button_1.grid(column='1', row='0', sticky='ew')

        self._button_2 = tk.Button(self._frame_3)
        self._button_2.configure(text='Save', command=self.do_save_UI, width='10')
        self._button_2.grid(column='0', row='0', sticky='ew')

        self._button_3 = tk.Button(self._frame_3)
        self._button_3.configure(text='Remove ComicInfo', command=self.deleteComicInfo, justify='center', )
        self._button_3.grid(column='0', row='1', sticky='w')

        self._button_4 = tk.Button(self._frame_3)
        self._button_4.configure(state='disabled', text='Fetch Online', justify='center')
        self._button_4.grid(column='1', columnspan='3', row='1', sticky='e')

        self._button_5 = tk.Button(self._frame_3)
        self._button_5.configure(text='Clear', command=self._clearUI, width='10')
        self._button_5.grid(column='2', row='0', sticky='ew')

        self._frame_3.configure(height='200', width='200')
        self._frame_3.pack(side='top')
        self._frame_3.columnconfigure('0', weight='1')
        self._frame_3.columnconfigure('1', weight='10')
        self._frame_3.columnconfigure('2', weight='1')
        self._frame_3.columnconfigure('3', pad='20')
        self.scrolledframe_2 = ScrolledFrame(self.frame_1, scrolltype='both')
        self.frame_3 = tk.Frame(self.scrolledframe_2.innerframe)
        self._panedwindow_1 = tk.PanedWindow(self.frame_3, orient='horizontal')
        self.frame_2 = tk.Frame(self._panedwindow_1)
        self.label_1 = tk.Label(self.frame_2)
        self.label_1.configure(text='Title')
        self.label_1.pack(side='top')
        self._entry_Title = ttk.Combobox(self.frame_2)
        self._entry_Title.configure(textvariable=self.entry_Title_val)
        self._entry_Title.pack(expand='false', fill='both', side='top')
        self._entry_Title.bind('<Button-1>', makeFocused, add='')
        self._entry_Title.bind('<Button-1>', makeFocused, add='')
        self._entry_Title.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Title.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Title.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Title.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Title.bind('<Return>', makeReadOnly, add='')
        self._entry_Title.bind('<Return>', makeReadOnly, add='')
        self._label_2 = tk.Label(self.frame_2)
        self._label_2.configure(text='Series')
        self._label_2.pack(side='top')
        self._entry_Series = ttk.Combobox(self.frame_2)
        self._entry_Series.configure(textvariable=self.entry_Series_val)
        self._entry_Series.pack(fill='both', side='top')
        self._entry_Series.bind('<Button-1>', makeFocused, add='')
        self._entry_Series.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Series.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Series.bind('<Return>', makeReadOnly, add='')
        self.label_41 = tk.Label(self.frame_2)
        self.label_41.configure(text='Localized Series')
        self.label_41.pack(side='top')
        self._entry_LocalizedSeries = ttk.Combobox(self.frame_2)
        self._entry_LocalizedSeries.configure(textvariable=self.entry_LocalizedSeries_val)
        self._entry_LocalizedSeries.pack(fill='both', side='top')
        self._label_3 = tk.Label(self.frame_2)
        self._label_3.configure(text='SeriesSort')
        self._label_3.pack(side='top')
        self._entry_SeriesSort1 = ttk.Combobox(self.frame_2)
        self._entry_SeriesSort1.configure(textvariable=self.entry_SeriesSort_val)
        self._entry_SeriesSort1.pack(fill='both', side='top')
        self._entry_SeriesSort1.bind('<Button-1>', makeFocused, add='')
        self._entry_SeriesSort1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_SeriesSort1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_SeriesSort1.bind('<Return>', makeReadOnly, add='')
        self._label_7 = tk.Label(self.frame_2)
        self._label_7.configure(text='AlternateSeries')
        self._label_7.pack(side='top')
        self._entry_AlternateSeries1 = ttk.Combobox(self.frame_2)
        self._entry_AlternateSeries1.configure(cursor='boat', textvariable=self.entry_AlternateSeries_val)
        self._entry_AlternateSeries1.pack(fill='both', side='top')
        self._entry_AlternateSeries1.bind('<Button-1>', makeFocused, add='')
        self._entry_AlternateSeries1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_AlternateSeries1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_AlternateSeries1.bind('<Return>', makeReadOnly, add='')
        self._label_10 = tk.Label(self.frame_2)
        self._label_10.configure(text='Summary')
        self._label_10.pack(side='top')
        self.tkinterscrolledtext_1 = ScrolledText(self.frame_2)
        self.tkinterscrolledtext_1.configure(height='5')
        self.tkinterscrolledtext_1.pack(fill='both', side='top')
        self._label_11 = tk.Label(self.frame_2)
        self._label_11.configure(text='Notes')
        self._label_11.pack(side='top')
        self._entry_Notes1 = ttk.Combobox(self.frame_2)
        self._entry_Notes1.configure(textvariable=self.entry_Notes_val)
        self._entry_Notes1.pack(fill='both', side='top')
        self._entry_Notes1.bind('<Button-1>', makeFocused, add='')
        self._entry_Notes1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Notes1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Notes1.bind('<Return>', makeReadOnly, add='')
        self._label_24 = tk.Label(self.frame_2)
        self._label_24.configure(text='Genre')
        self._label_24.pack(side='top')
        self._entry_Genre1 = ttk.Combobox(self.frame_2)
        self._entry_Genre1.configure(textvariable=self.entry_Genre_val)
        self._entry_Genre1.pack(fill='both', side='top')
        self._entry_Genre1.bind('<Button-1>', makeFocused, add='')
        self._entry_Genre1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Genre1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Genre1.bind('<Return>', makeReadOnly, add='')
        self._label_25 = tk.Label(self.frame_2)
        self._label_25.configure(text='Tags')
        self._label_25.pack(side='top')
        self._entry_Tags1 = ttk.Combobox(self.frame_2)
        self._entry_Tags1.configure(textvariable=self.entry_Tags_val)
        self._entry_Tags1.pack(fill='both', side='top')
        self._entry_Tags1.bind('<Button-1>', makeFocused, add='')
        self._entry_Tags1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Tags1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Tags1.bind('<Return>', makeReadOnly, add='')
        self._label_26 = tk.Label(self.frame_2)
        self._label_26.configure(text='Web')
        self._label_26.pack(side='top')
        self._entry_Web1 = ttk.Combobox(self.frame_2)
        self._entry_Web1.configure(textvariable=self.entry_Web_val)
        self._entry_Web1.pack(fill='both', side='top')
        self._entry_Web1.bind('<Button-1>', makeFocused, add='')
        self._entry_Web1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Web1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Web1.bind('<Return>', makeReadOnly, add='')
        self._label_38 = tk.Label(self.frame_2)
        self._label_38.configure(text='SeriesGroup')
        self._label_38.pack(side='top')
        self._entry_SeriesGroup1 = ttk.Combobox(self.frame_2)
        self._entry_SeriesGroup1.configure(textvariable=self.entry_SeriesGroup_val)
        self._entry_SeriesGroup1.pack(fill='both', side='top')
        self._entry_SeriesGroup1.bind('<Button-1>', makeFocused, add='')
        self._entry_SeriesGroup1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_SeriesGroup1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_SeriesGroup1.bind('<Return>', makeReadOnly, add='')
        self._label_39 = tk.Label(self.frame_2)
        self._label_39.configure(text='AgeRating')
        self._label_39.pack(side='top')
        self._entry_AgeRating1 = ttk.Combobox(self.frame_2)
        self._entry_AgeRating1.configure(textvariable=self.entry_AgeRating_val)
        self._entry_AgeRating1.pack(fill='both', side='top')
        self._entry_AgeRating1.bind('<Button-1>', makeFocused, add='')
        self._entry_AgeRating1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_AgeRating1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_AgeRating1.bind('<Return>', makeReadOnly, add='')
        self._label_40 = tk.Label(self.frame_2)
        self._label_40.configure(text='CommunityRating')
        self._label_40.pack(side='top')
        self._entry_CommunityRating1 = ttk.Combobox(self.frame_2)
        self._entry_CommunityRating1.configure(textvariable=self.entry_CommunityRating_val)
        self._entry_CommunityRating1.pack(fill='both', side='top')
        self._entry_CommunityRating1.bind('<Button-1>', makeFocused, add='')
        self._entry_CommunityRating1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_CommunityRating1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_CommunityRating1.bind('<Return>', makeReadOnly, add='')
        self._label_35 = tk.Label(self.frame_2)
        self._label_35.configure(text='ScanInformation')
        self._label_35.pack(side='top')
        self._entry_ScanInformation1 = ttk.Combobox(self.frame_2)
        self._entry_ScanInformation1.configure(textvariable=self.entry_ScanInformation_val)
        self._entry_ScanInformation1.pack(fill='both', side='top')
        self._entry_ScanInformation1.bind('<Button-1>', makeFocused, add='')
        self._entry_ScanInformation1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_ScanInformation1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_ScanInformation1.bind('<Return>', makeReadOnly, add='')
        self._label_36 = tk.Label(self.frame_2)
        self._label_36.configure(text='StoryArc')
        self._label_36.pack(side='top')
        self._entry_StoryArc1 = ttk.Combobox(self.frame_2)
        self._entry_StoryArc1.configure(textvariable=self.entry_StoryArc_val)
        self._entry_StoryArc1.pack(fill='both', side='top')
        self._entry_StoryArc1.bind('<Button-1>', makeFocused, add='')
        self._entry_StoryArc1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_StoryArc1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_StoryArc1.bind('<Return>', makeReadOnly, add='')
        self.frame_2.configure(height='200', width='200')
        self.frame_2.place(anchor='nw', x='0', y='0')
        self._panedwindow_1.add(self.frame_2, pady='10')
        self._lframe_2 = tk.LabelFrame(self._panedwindow_1)
        self._label_15 = tk.Label(self._lframe_2)
        self._label_15.configure(text='Writer')
        self._label_15.pack(side='top')
        self._entry_Writer1 = ttk.Combobox(self._lframe_2)
        self._entry_Writer1.configure(textvariable=self.entry_Writer_val)
        self._entry_Writer1.pack(fill='x', side='top')
        self._entry_Writer1.bind('<Button-1>', makeFocused, add='')
        self._entry_Writer1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Writer1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Writer1.bind('<Return>', makeReadOnly, add='')
        self._label_16 = tk.Label(self._lframe_2)
        self._label_16.configure(text='Inker')
        self._label_16.pack(side='top')
        self._entry_Inker1 = ttk.Combobox(self._lframe_2)
        self._entry_Inker1.configure(textvariable=self.entry_Inker_val)
        self._entry_Inker1.pack(fill='x', side='top')
        self._entry_Inker1.bind('<Button-1>', makeFocused, add='')
        self._entry_Inker1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Inker1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Inker1.bind('<Return>', makeReadOnly, add='')
        self._label_17 = tk.Label(self._lframe_2)
        self._label_17.configure(text='Colorist')
        self._label_17.pack(side='top')
        self._entry_Colorist1 = ttk.Combobox(self._lframe_2)
        self._entry_Colorist1.configure(textvariable=self.entry_Colorist_val)
        self._entry_Colorist1.pack(fill='x', side='top')
        self._entry_Colorist1.bind('<Button-1>', makeFocused, add='')
        self._entry_Colorist1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Colorist1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Colorist1.bind('<Return>', makeReadOnly, add='')
        self._label_18 = tk.Label(self._lframe_2)
        self._label_18.configure(text='Letterer')
        self._label_18.pack(side='top')
        self._entry_Letterer1 = ttk.Combobox(self._lframe_2)
        self._entry_Letterer1.configure(textvariable=self.entry_Letterer_val)
        self._entry_Letterer1.pack(fill='x', side='top')
        self._entry_Letterer1.bind('<Button-1>', makeFocused, add='')
        self._entry_Letterer1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Letterer1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Letterer1.bind('<Return>', makeReadOnly, add='')
        self._label_19 = tk.Label(self._lframe_2)
        self._label_19.configure(text='CoverArtist')
        self._label_19.pack(side='top')
        self._entry_CoverArtist1 = ttk.Combobox(self._lframe_2)
        self._entry_CoverArtist1.configure(textvariable=self.entry_CoverArtist_val)
        self._entry_CoverArtist1.pack(fill='x', side='top')
        self._entry_CoverArtist1.bind('<Button-1>', makeFocused, add='')
        self._entry_CoverArtist1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_CoverArtist1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_CoverArtist1.bind('<Return>', makeReadOnly, add='')
        self._label_20 = tk.Label(self._lframe_2)
        self._label_20.configure(text='Editor')
        self._label_20.pack(side='top')
        self._entry_Editor1 = ttk.Combobox(self._lframe_2)
        self._entry_Editor1.configure(textvariable=self.entry_Editor_val)
        self._entry_Editor1.pack(fill='x', side='top')
        self._entry_Editor1.bind('<Button-1>', makeFocused, add='')
        self._entry_Editor1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Editor1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Editor1.bind('<Return>', makeReadOnly, add='')
        self._label_21 = tk.Label(self._lframe_2)
        self._label_21.configure(text='Translator')
        self._label_21.pack(side='top')
        self._entry_Translator1 = ttk.Combobox(self._lframe_2)
        self._entry_Translator1.configure(textvariable=self.entry_Translator_val)
        self._entry_Translator1.pack(fill='x', side='top')
        self._entry_Translator1.bind('<Button-1>', makeFocused, add='')
        self._entry_Translator1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Translator1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Translator1.bind('<Return>', makeReadOnly, add='')
        self._label_22 = tk.Label(self._lframe_2)
        self._label_22.configure(text='Publisher')
        self._label_22.pack(side='top')
        self._entry_Publisher1 = ttk.Combobox(self._lframe_2)
        self._entry_Publisher1.configure(textvariable=self.entry_Publisher_val)
        self._entry_Publisher1.pack(fill='x', side='top')
        self._entry_Publisher1.bind('<Button-1>', makeFocused, add='')
        self._entry_Publisher1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Publisher1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Publisher1.bind('<Return>', makeReadOnly, add='')
        self._label_23 = tk.Label(self._lframe_2)
        self._label_23.configure(text='Imprint')
        self._label_23.pack(side='top')
        self._entry_Imprint1 = ttk.Combobox(self._lframe_2)
        self._entry_Imprint1.configure(textvariable=self.entry_Imprint_val)
        self._entry_Imprint1.pack(fill='x', side='top')
        self._entry_Imprint1.bind('<Button-1>', makeFocused, add='')
        self._entry_Imprint1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Imprint1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Imprint1.bind('<Return>', makeReadOnly, add='')
        self._label_32 = tk.Label(self._lframe_2)
        self._label_32.configure(text='Characters')
        self._label_32.pack(side='top')
        self._entry_Characters1 = ttk.Combobox(self._lframe_2)
        self._entry_Characters1.configure(textvariable=self.entry_Characters_val)
        self._entry_Characters1.pack(fill='x', side='top')
        self._entry_Characters1.bind('<Button-1>', makeFocused, add='')
        self._entry_Characters1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Characters1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Characters1.bind('<Return>', makeReadOnly, add='')
        self._label_33 = tk.Label(self._lframe_2)
        self._label_33.configure(text='Teams')
        self._label_33.pack(side='top')
        self._entry_Teams1 = ttk.Combobox(self._lframe_2)
        self._entry_Teams1.configure(textvariable=self.entry_Teams_val)
        self._entry_Teams1.pack(fill='x', side='top')
        self._entry_Teams1.bind('<Button-1>', makeFocused, add='')
        self._entry_Teams1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Teams1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Teams1.bind('<Return>', makeReadOnly, add='')
        self._label_34 = tk.Label(self._lframe_2)
        self._label_34.configure(text='Locations')
        self._label_34.pack(side='top')
        self._entry_Locations1 = ttk.Combobox(self._lframe_2)
        self._entry_Locations1.configure(textvariable=self.entry_Locations_val)
        self._entry_Locations1.pack(fill='x', side='top')
        self._entry_Locations1.bind('<Button-1>', makeFocused, add='')
        self._entry_Locations1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Locations1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Locations1.bind('<Return>', makeReadOnly, add='')
        self._lframe_2.configure(height='200', width='200')
        self._lframe_2.place(anchor='nw', relx='0.1', rely='0.1', x='500000', y='50')
        self._panedwindow_1.add(self._lframe_2)
        self._frame_5 = tk.Frame(self._panedwindow_1)
        self._label_4 = tk.Label(self._frame_5)
        self._label_4.configure(text='Number')
        self._label_4.pack(side='top')
        self._entry_Number1 = ttk.Combobox(self._frame_5)
        self._entry_Number1.configure(textvariable=self.entry_Number_val, width='10')
        self._entry_Number1.pack(side='top')
        self._entry_Number1.bind('<Button-1>', makeFocused, add='')
        self._entry_Number1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Number1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Number1.bind('<Return>', makeReadOnly, add='')
        self._label_8 = tk.Label(self._frame_5)
        self._label_8.configure(text='AlternateNumber')
        self._label_8.pack(side='top')
        self._entry_AlternateNumber1 = ttk.Combobox(self._frame_5)
        self._entry_AlternateNumber1.configure(textvariable=self.entry_AlternateNumber_val, width='10')
        self._entry_AlternateNumber1.pack(side='top')
        self._entry_AlternateNumber1.bind('<Button-1>', makeFocused, add='')
        self._entry_AlternateNumber1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_AlternateNumber1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_AlternateNumber1.bind('<Return>', makeReadOnly, add='')
        self._label_5 = tk.Label(self._frame_5)
        self._label_5.configure(text='Count')
        self._label_5.pack(side='top')
        self._entry_AlternateCount1 = ttk.Combobox(self._frame_5)
        self.entry_AlternateCount_val = tk.IntVar(value='')
        self._entry_AlternateCount1.configure(textvariable=self.entry_AlternateCount_val, values='-1', width='10')
        self._entry_AlternateCount1.pack(side='top')
        self._entry_AlternateCount1.bind('<Button-1>', makeFocused, add='')
        self._entry_AlternateCount1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_AlternateCount1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_AlternateCount1.bind('<Return>', makeReadOnly, add='')
        self._label_9 = tk.Label(self._frame_5)
        self._label_9.configure(text='AlternateCount')
        self._label_9.pack(side='top')
        self._entry_Count1 = ttk.Combobox(self._frame_5)
        self.entry_Count_val = tk.IntVar(value='')
        self._entry_Count1.configure(textvariable=self.entry_Count_val, values='-1', width='10')
        self._entry_Count1.pack(side='top')
        self._entry_Count1.bind('<Button-1>', makeFocused, add='')
        self._entry_Count1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Count1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Count1.bind('<Return>', makeReadOnly, add='')
        self._label_6 = tk.Label(self._frame_5)
        self._label_6.configure(text='Volume')
        self._label_6.pack(side='top')
        self._entry_Volume1 = ttk.Combobox(self._frame_5)
        self.entry_Volume_val = tk.IntVar(value='')
        self._entry_Volume1.configure(textvariable=self.entry_Volume_val, values='-1', width='10')
        self._entry_Volume1.pack(side='top')
        self._entry_Volume1.bind('<Button-1>', makeFocused, add='')
        self._entry_Volume1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Volume1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Volume1.bind('<Return>', makeReadOnly, add='')
        self._label_27 = tk.Label(self._frame_5)
        self._label_27.configure(text='PageCount')
        self._label_27.pack(side='top')
        self._entry_PageCount1 = ttk.Combobox(self._frame_5)
        self.entry_PageCount_val = tk.IntVar(value='')
        self._entry_PageCount1.configure(textvariable=self.entry_PageCount_val, width='10')
        self._entry_PageCount1.pack(side='top')
        self._entry_PageCount1.bind('<Button-1>', makeFocused, add='')
        self._entry_PageCount1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_PageCount1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_PageCount1.bind('<Return>', makeReadOnly, add='')
        self._label_12 = tk.Label(self._frame_5)
        self._label_12.configure(text='Year')
        self._label_12.pack(side='top')
        self._entry_Year1 = ttk.Combobox(self._frame_5)
        self.entry_Year_val = tk.IntVar(value='')
        self._entry_Year1.configure(textvariable=self.entry_Year_val, width='10')
        self._entry_Year1.pack(side='top')
        self._entry_Year1.bind('<Button-1>', makeFocused, add='')
        self._entry_Year1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Year1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Year1.bind('<Return>', makeReadOnly, add='')
        self._label_13 = tk.Label(self._frame_5)
        self._label_13.configure(text='Month')
        self._label_13.pack(side='top')
        self._entry_Month1 = ttk.Combobox(self._frame_5)
        self.entry_Month_val = tk.IntVar(value='')
        self._entry_Month1.configure(textvariable=self.entry_Month_val, width='10')
        self._entry_Month1.pack(side='top')
        self._entry_Month1.bind('<Button-1>', makeFocused, add='')
        self._entry_Month1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Month1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Month1.bind('<Return>', makeReadOnly, add='')
        self._label_14 = tk.Label(self._frame_5)
        self._label_14.configure(text='Day')
        self._label_14.pack(side='top')
        self._entry_Day1 = ttk.Combobox(self._frame_5)
        self.entry_Day_val = tk.IntVar(value='')
        self._entry_Day1.configure(textvariable=self.entry_Day_val, width='10')
        self._entry_Day1.pack(side='top')
        self._entry_Day1.bind('<Button-1>', makeFocused, add='')
        self._entry_Day1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Day1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Day1.bind('<Return>', makeReadOnly, add='')
        self._label_29 = tk.Label(self._frame_5)
        self._label_29.configure(text='Format')
        self._label_29.pack(side='top')
        self._entry_Format1 = ttk.Combobox(self._frame_5)
        self._entry_Format1.configure(textvariable=self.entry_Format_val, width='10')
        self._entry_Format1.pack(side='top')
        self._entry_Format1.bind('<Button-1>', makeFocused, add='')
        self._entry_Format1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Format1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Format1.bind('<Return>', makeReadOnly, add='')
        self._label_28 = tk.Label(self._frame_5)
        self._label_28.configure(text='LanguageISO')
        self._label_28.pack(side='top')
        self._entry_LanguageISO1 = ttk.Combobox(self._frame_5)
        self._entry_LanguageISO1.configure(textvariable=self.entry_LanguageISO_val, width='10')
        self._entry_LanguageISO1.pack(side='top')
        self._entry_LanguageISO1.bind('<Button-1>', makeFocused, add='')
        self._entry_LanguageISO1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_LanguageISO1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_LanguageISO1.bind('<Return>', makeReadOnly, add='')
        self._label_30 = tk.Label(self._frame_5)
        self._label_30.configure(text='BlackAndWhite')
        self._label_30.pack(side='top')
        self.__tkvar = tk.StringVar(value='Unknown')
        __values = ['Yes', 'No']
        self._entry_BlackAndWhite = tk.OptionMenu(self._frame_5, self.__tkvar, 'Unknown', *__values, command=None)
        self._entry_BlackAndWhite.pack(side='top')
        self._entry_BlackAndWhite.bind('<Button-1>', makeFocused, add='')
        self._entry_BlackAndWhite.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_BlackAndWhite.bind('<FocusOut>', onFocusOut, add='')
        self._entry_BlackAndWhite.bind('<Return>', makeReadOnly, add='')
        self._label_31 = tk.Label(self._frame_5)
        self._label_31.configure(text='Manga')
        self._label_31.pack(side='top')
        __values = ['No', 'Yes', 'YesAndRightToLeft']
        self._entry_Manga = tk.OptionMenu(self._frame_5, self.__tkvar, 'Unknown', *__values, command=None)
        self._entry_Manga.pack(side='top')
        self._entry_Manga.bind('<Button-1>', makeFocused, add='')
        self._entry_Manga.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_Manga.bind('<FocusOut>', onFocusOut, add='')
        self._entry_Manga.bind('<Return>', makeReadOnly, add='')
        self._label_37 = tk.Label(self._frame_5)
        self._label_37.configure(text='StoryArcNumber')
        self._label_37.pack(side='top')
        self._entry_StoryArcNumber1 = ttk.Combobox(self._frame_5)
        self._entry_StoryArcNumber1.configure(textvariable=self.entry_StoryArcNumber_val, width='10')
        self._entry_StoryArcNumber1.pack(side='top')
        self._entry_StoryArcNumber1.bind('<Button-1>', makeFocused, add='')
        self._entry_StoryArcNumber1.bind('<Double-Button-1>', self.makeEditable, add='')
        self._entry_StoryArcNumber1.bind('<FocusOut>', onFocusOut, add='')
        self._entry_StoryArcNumber1.bind('<Return>', makeReadOnly, add='')
        self._frame_5.configure(height='200', width='200')
        self._frame_5.place(anchor='nw', x='0', y='0')
        self._panedwindow_1.add(self._frame_5)
        self._panedwindow_1.configure(borderwidth='30', handlesize='1', height='0', proxyrelief='raised')
        self._panedwindow_1.configure(sashpad='10', sashrelief='raised', sashwidth='7', showhandle='false')
        self._panedwindow_1.grid(row='0', sticky='nsew')
        self.frame_3.configure(height='200', width='200')
        self.frame_3.pack(side='top')
        self.frame_3.grid_anchor('center')
        self.scrolledframe_2.configure(usemousewheel=True)
        self.scrolledframe_2.pack(expand='true', fill='both', side='top')
        self.frame_1.configure(height='600', width='200')
        self.frame_1.pack(anchor='center', expand='true', fill='both', side='top')

        # scrollbarx

        # MAIN FRAME
        # self._frame_5_statusInfo = tk.Frame(self.frame_1,bg="grey")

        # self._frame_5_statusInfo.grid(row=4, column=1, sticky=tk.W)
        # # column=0, row=0,sticky="nesw")
        # master.rowconfigure('0', minsize='0')
        # master.columnconfigure('0', minsize='0', uniform='None')

        # # File Controller - Read,Save
        # self._files_controller = tk.Frame(self.frame_1)
        # self.button2_openfile = tk.Button(self._files_controller, text="Open", command=self._open_files, width=15)
        # self.button2_openfile.grid(column=0, row=0)
        # # self.button3_read = tk.Button(self._files_controller, text="Read",
        # # command=self.create_loadedComicInfo_list, width=15)
        # # self.button3_read.grid(column=1, row=3, pady="5 10", columnspan=2)
        # self.button4_save = tk.Button(self._files_controller, text="Save", command=self.do_save_UI, width=15)
        # self.button4_save.grid(column=1, row=0)
        # self.button4_save = tk.Button(self._files_controller, text="Remove ComicInfo.xml", command=self.deleteComicInfo,
        #                               width=20)
        # self.button4_save.grid(column=3, row=0)
        # # self.__tkvar.set('Age Rating')
        # self._files_controller.configure(pady=5)
        # self._files_controller.grid(row=2, column=1)
        # Main widget
        self.mainwindow = self.frame_1
        self._progressBarFrame = tk.Frame(self.frame_1)
        self._progressBarFrame.configure(height='70', width='200', background="red")
        self._progressBarFrame.pack(anchor='center', side='top')

        self.widgets_obj = [
            self._entry_Title,
            self._entry_Series,
            self._entry_LocalizedSeries,
            self._entry_SeriesSort1,
            self._entry_AlternateSeries1,
            self.input_1_summary_obj,
            self._entry_Notes1,
            self._entry_Genre1,
            self._entry_Tags1,
            self._entry_Web1,
            self._entry_SeriesGroup1,
            self._entry_AgeRating1,
            self._entry_CommunityRating1,
            self._entry_ScanInformation1,
            self._entry_StoryArc1,

            self._entry_Writer1,
            self._entry_Inker1,
            self._entry_Colorist1,
            self._entry_Letterer1,
            self._entry_CoverArtist1,
            self._entry_Editor1,
            self._entry_Translator1,
            self._entry_Publisher1,
            self._entry_Imprint1,
            self._entry_Characters1,
            self._entry_Teams1,
            self._entry_Locations1,

            self._entry_Number1,
            self._entry_AlternateNumber1,
            self._entry_Count1,
            self._entry_AlternateCount1,
            self._entry_Volume1,
            self._entry_PageCount1,
            self._entry_Year1,
            self._entry_Month1,
            self._entry_Day1,
            self._entry_Format1,
            self._entry_LanguageISO1,
            self._entry_BlackAndWhite,
            self._entry_Manga,
            self._entry_StoryArcNumber1,
        ]

        # self.frame_1.configure(bg="blue")
        # self._frame_2.configure(bg="red")
        # self._frame_3.configure(bg="yellow")
        # self._frame_3_people.configure(bg="purple")
        # self._frame_1.configure(bg="green")

    def run(self):
        self.mainwindow.mainloop()

    def _open_files(self):
        self._clearUI()

        self.selected_filenames = list[str]()
        covers_path_list = filedialog.askopenfiles(initialdir=launch_path, title="Select file to apply cover",
                                                   filetypes=(("CBZ Files", ".cbz"),)
                                                   # ("Zip files", ".zip"))
                                                   )
        for file in covers_path_list:
            self.selected_filenames.append(file.name)
        self.create_loadedComicInfo_list()
        # self._label_28_statusinfo.configure(text="Successfuly loaded")

    def create_loadedComicInfo_list(self, cli_selected_files: list[str] = None):
        self.initialize_StringVars()
        try:
            if not self.selected_filenames:
                if cli_selected_files:
                    for file in cli_selected_files:
                        try:
                            loaded_ComIinf = self.load_comicinfo_xml(file)
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
                logger.debug("Selected files UI:\n    " + "\n    ".join(self.selected_filenames))
                for file_path in self.selected_filenames:
                    loaded_ComIinf = self.load_comicinfo_xml(file_path)

                    if loaded_ComIinf:
                        self.loadedComicInfo_list.append(loaded_ComIinf)
                    else:
                        continue
                    # self.thiselem, self.nextelem = self.nextelem, next(self.licycle)
        except CancelComicInfoLoad:
            self.loadedComicInfo_list = []

    def _parseUI_toComicInfo(self):
        """
        Modifies every ComicInfo loaded with values from the UI
        :return: True if all LoadedComicInfo were updated. If any error or saving is cancelled returns False
        """

        modified_loadedComicInfo_list = []
        # modified_loadedComicInfo_XML_list = list[str]()
        keep_original_value = None
        for comicObj in self.loadedComicInfo_list:
            logger.debug(f"parsing UI to ComicInfo: '{comicObj.path}'")

            # Load the comic info into our StringVar and IntVar, so they can be modified in the ui
            widgets_var_zip = self._get_widgets_var_zip(self.widgets_var, comicObj.comicInfoObj, self.widgets_obj)


            if self.widgets_obj:
                noSelectionCheck = [str(widgets_var_tuple[0]) for widgets_var_tuple in
                                    [i for i in widgets_var_zip if
                                     not isinstance(i[3],
                                                    tk.OptionMenu) and not isinstance(
                                         i[3], models.LongText)] if
                                    (not list(widgets_var_tuple[3]['values']) and not widgets_var_tuple[0].get())]
                if noSelectionCheck and keep_original_value is None:
                    keep_original_value = mb.askokcancel("Fields not selected",
                                                         message=f"There are conflics in your selection.\n"
                                                                 f"Ignore if you want the following fields to keep it's original value.\n"
                                                                 f"{', '.join(noSelectionCheck)}\n\nContinue?")
                    if not keep_original_value:
                        raise CancelComicInfoSave()
                    logger.info("Proceeding with saving. Unset fields will retain original values")
                else:
                    logger.info("Proceeding with saving. Unset fields will retain original values")
                logger.info("Before loop")
            widgets_var_zip = self._get_widgets_var_zip(self.widgets_var, comicObj.comicInfoObj, self.widgets_obj)
            for widgets_var_tuple in widgets_var_zip:
                widgetvar = widgets_var_tuple[0]
                comicinfo_atr_get = widgets_var_tuple[1]()
                comicinfo_atr_set = widgets_var_tuple[2]

                # If any field is '' it should keep original value
                try:  # IntVars do not accept "" as value. If its excepts keep original value
                    value = widgetvar.get()
                    if value == "":
                        continue

                except tk.TclError:
                    continue

                # If no ui keep whatever is on the stringvar/intvar
                if not self.widgets_obj:
                    comicinfo_atr_set(widgetvar.get())
                    continue

                # If value is -1 clear the field
                elif widgetvar.get() in ("-1", -1):
                    if isinstance(widgetvar, tk.StringVar):
                        comicinfo_atr_set("")
                    elif str(widgetvar) == "PageCount":  # Pagecount default is not -1 but 0
                        comicinfo_atr_set(0)
                    else:
                        comicinfo_atr_set(-1)
                # Modify field with whatever is on the stringvar/intvar
                else:
                    comicinfo_atr_set(widgetvar.get())

            modified_loadedComicInfo, keep_original_value = comicObj, keep_original_value
            modified_loadedComicInfo_list.append(modified_loadedComicInfo)
        self.loadedComicInfo_list = modified_loadedComicInfo_list

    def _saveComicInfo(self):
        progressBar = ProgressBar(self._initialized_UI, self._progressBarFrame if self._initialized_UI else None,
                                  total=len(self.loadedComicInfo_list))
        for loadedComicObj in self.loadedComicInfo_list:
            logger.info(f"[Processing] Starting processing to save data to file {loadedComicObj.path}")

            try:
                WriteComicInfo(loadedComicObj).to_file()
                progressBar.increaseCount()
            except FileExistsError as e:
                if self._initialized_UI:
                    mb.showwarning(f"[ERROR] File already exists",
                                   f"Trying to create:\n`{str(e.filename2)}` but already exists\n\nException:\n{e}")

                logger.error("[ERROR] File already exists\n"
                             f"Trying to create:\n`{str(e.filename2)}` but already exists\nException:\n{e}")
                progressBar.increaseError()
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
                progressBar.increaseError()
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
                progressBar.increaseError()
                if not self._initialized_UI:
                    raise e
                else:
                    continue
            except Exception as e:
                if self._initialized_UI:
                    mb.showerror("Something went wrong", "Error processing. Check logs.")
                logger.critical("Exception Processing", e)
                progressBar.increaseError()
                raise e
            progressBar.updatePB()

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
        try:
            self._parseUI_toComicInfo()
            self._saveComicInfo()
        except CancelComicInfoSave:
            logger.info("Cancelled Saving")
        except Exception as e:
            raise e

    def _clearUI(self):
        self.initialize_StringVars()
        for widget in self.widgets_obj:
            if isinstance(widget, ttk.Combobox):
                widget['values'] = []
        self.loadedComicInfo_list = []

    def load_comicinfo_xml(self, cbz_path) -> LoadedComicInfo:
        """
        Accepts a path string
        Returns a LoadedComicInfo with the ComicInfo class generated from the data contained inside ComicInfo file
        which is taken from the zip-like file type

        :param self: parent self
        :param string cbz_path: the path to the zip-like file
        :return: LoadedComicInfo: LoadedComicInfo
        """
        logger.info(f"loading file: '{cbz_path}'")
        # Load ComicInfo.xml to Class
        try:
            # raise CorruptedComicInfo(cbz_path)
            comicinfo = ReadComicInfo(cbz_path).to_ComicInfo(print_xml=False)
        except NoMetadataFileFound:
            logger.warning(f"Metadata file 'ComicInfo.xml' not found inside {cbz_path}\n"
                           f"One will be created when saving changes to file.\n"
                           f"This applies to all future errors")
            if not self.warning_metadataNotFound and self._initialized_UI:
                mb.showwarning("Warning reading ComicInfo",
                               f"ComicInfo.xml was not found inside: {cbz_path}\n"
                               f"One will be created when saving changes to file.\n"
                               f"This applies to all selected files")
                self.warning_metadataNotFound = True
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

        widgets_var_zip = self._get_widgets_var_zip(
            self.widgets_var, loadedInfo.comicInfoObj, self.widgets_obj)
        # Load the comic info into our StringVar(s) and IntVar(s), so they can be modified in the ui
        for widgets_var_tuple in widgets_var_zip:
            widgetvar = widgets_var_tuple[0]
            comicinfo_atr_get = widgets_var_tuple[1]()
            comicinfo_atr_set = widgets_var_tuple[2]
            # logger.debug(f"Processing '{widgetvar}' | Value: {widgetvar.get()} | ComicInfo Value: {comicinfo_atr_get}")
            # field is empty. Skipping

            # logger.info(str(widgetvar))
            # logger.info(str(widgetvar))
            # logger.info(str(widgetvar))

            if widgetvar.get() != comicinfo_atr_get:
                if not self.widgets_obj:
                    widgetvar.set(comicinfo_atr_get)
                    continue
                try:
                    if not self.widgets_obj:
                        continue
                    widget = widgets_var_tuple[3]

                    logger.debug(f"Processing {widgetvar}")
                    if isinstance(widgetvar, models.LongText) and comicinfo_atr_get:
                        widgetvar.set(comicinfo_atr_get)
                        continue
                    elif isinstance(widget, tk.OptionMenu) and widgetvar.get() != comicinfo_atr_get:
                        widgetvar.set(comicinfo_atr_get)
                        continue
                    widget_list = list(widget['values'])
                    # logger.error(widget['values'])
                    if not widget['values']:  # There's no loaded data for this field. Set first read value as input
                        widget['values'] = (comicinfo_atr_get,)
                        widget_list = list(widget['values'])
                        widget['values'] = widget_list
                        widgetvar.set(comicinfo_atr_get)
                        logger.debug(
                            f"Loaded new value for tag '{widgetvar}' as input value")

                    else:
                        if comicinfo_atr_get not in widget_list:  # There's items in the field but this value not present. # Clear input value

                            if isinstance(widget, tk.OptionMenu):
                                widgetvar.set("Unknown")
                            elif isinstance(widgetvar, tk.StringVar):
                                widgetvar.set(-50)
                            logger.debug(f"Cleared input values for tag {widgetvar}. There's conflict")

                        # if len(widget_list) == 1:
                        #     widgetvar.set(comicinfo_atr_get)
                        #     logger.debug(
                        #         f"Loaded new value for tag '{widgetvar}'")

                    # Ignored values: Volume, number

                except Exception as e:
                    logger.error("Exception found", exc_info=e)

        return loadedInfo


class AppCli:

    def __init__(self):
        self.args = None
        self.selected_files: list[str] = None
        self.loadedComicInfo_List: list[LoadedComicInfo] = None

        self.origin_path = None
        self.parse_args()
        self.loadedComicInfo_List, self.origin_LoadedcInfo = self.loadFiles()

    def parse_args(self):
        """
        Parses the argument provided on the execution of the script.

        **AppCli.copyFrom** The path to the origin file to copy from\n
        **AppCli.copyTo** The path to the destination paths\n
        **AppCli.keepNumeration** boolean Whether to keep numeration from destination path or remove when pasting\n
        """
        parser = argparse.ArgumentParser()

        parser.add_argument("--copyfrom", help="The path to the file you want to copy the metatada from.\n "
                                               "(Volume and number are not parsed)", type=is_dir_path,
                            metavar="<path>")
        parser.add_argument("--copyto", type=is_dir_path, help="The path of the files to modify."
                                                               " (Accepts shell-style wildcards)",
                            metavar="<path>", nargs="+")
        parser.add_argument("--keepNumeration", action="store_true",
                            help="Should the modified file keep the numbering (volume and number)")
        self.args = parser.parse_args()
        from glob import glob
        if self.args.copyfrom:
            self.origin_path = glob(self.args.copyfrom)[0]
        if self.args.copyto:
            if isinstance(self.args.copyto, list):
                selected_files = self.args.copyto
            else:
                selected_files = glob(self.args.copyto)
            self.selected_files = selected_files
        self.keepNumeration = self.args.keepNumeration

    def loadFiles(self) -> tuple[list[LoadedComicInfo], LoadedComicInfo | None]:
        """
        Loads the files whose paths are contained in App.selected_files
        :return: List of LoadedComicInfo
        """
        if not self.selected_files:
            raise NoFilesSelected()
        loadedComicInfo_List = list[LoadedComicInfo]()
        copyFrom_LoadedComicInfo = None
        for file_path in self.selected_files:
            logger.debug(f"Loading '{os.path.basename(file_path)}'")
            comicInfo: ComicInfo = cbz_handler.ReadComicInfo(file_path, ignore_empty_metadata=True).to_ComicInfo()
            loadedComicinfo = LoadedComicInfo(file_path, comicInfo=comicInfo)
            loadedComicInfo_List.append(loadedComicinfo)
            logger.debug(f"Loaded  {os.path.basename(file_path)}")
        if self.args.copyfrom:
            logger.debug(f"Loading source ComicInfo: '{os.path.basename(self.args.copyfrom)}'")
            comicInfo = cbz_handler.ReadComicInfo(self.origin_path, ignore_empty_metadata=False).to_ComicInfo()
            comicInfo.set_Number("")
            comicInfo.set_Volume(-1)
            copyFrom_LoadedComicInfo = LoadedComicInfo(self.origin_path, comicInfo)

        return loadedComicInfo_List, copyFrom_LoadedComicInfo

    def saveFiles(self):
        if not self.loadedComicInfo_List:
            raise NoComicInfoLoaded()
        for loadedComicInfo in self.loadedComicInfo_List:
            cbz_handler.WriteComicInfo(loadedComicInfo).to_file()
            logger.debug(f"Saved {os.path.basename(loadedComicInfo.path)}")

    def copyCInfo(self, ):
        if not self.loadedComicInfo_List:
            raise NoComicInfoLoaded()
        if not self.origin_LoadedcInfo:
            raise NoComicInfoLoaded(": No comicinfo to copy from selected")
        for loadedInfo in self.loadedComicInfo_List:
            loadedInfo.comicInfoObj = self.origin_LoadedcInfo.comicInfoObj


if __name__ == '__main__':
    # <Logger>
    logger = logging.getLogger()
    logging.getLogger('PIL').setLevel(logging.WARNING)
    # formatter = logging.Formatter()

    PROJECT_PATH = pathlib.Path(__file__).parent
    # rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/logs/MangaManager.log", maxBytes=5725760,
    #                                             backupCount=2)
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)]
                        # filename='/tmp/myapp.log'
                        )
    # logger.debug('DEBUG LEVEL - MAIN MODULE')
    # logger.info('INFO LEVEL - MAIN MODULE\n\n')
    # </Logger>

    app = AppCli()
    app.copyCInfo()
    app.saveFiles()
