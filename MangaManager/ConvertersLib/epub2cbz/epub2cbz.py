import logging
import os
import re
import tempfile
import tkinter as tk
import zipfile
from pathlib import Path

from tkinter.filedialog import askopenfiles, askdirectory
from tkinter.ttk import Style, Progressbar

logger = logging.getLogger(__name__)


# noinspection PyUnboundLocalVariable
class App:
    def __init__(self, master: tk.Toplevel, epubs_path_ist: list[str] = None, convert_to_webp=False, settings=None):
        """
        If there are epubsPathList; start() must be called manually

        :param epubs_path_ist: The list of string paths to the epubs files to process
        :param convert_to_webp: Should the images be converted to .webp when adding
        :param master: used for tkinter integrations
        """
        self.output_folder = ""
        self.convert_to_webp = convert_to_webp
        if not master:
            master = tk.Tk()
        self.master = master
        self.epubsPathList = epubs_path_ist
        self.settings = settings
        self._initialized_ui = False

        if not epubs_path_ist:
            self._initialized_ui = True
            # self.start_ui()

    def start(self):
        if not self.epubsPathList:
            return
        logger.info(f"Loaded file list: \n" + "\n".join(self.epubsPathList))

        logger.debug("Starting processing of files.")
        total = len(self.epubsPathList)
        # TBH I'd like to rework how this processing bar works. - Promidius
        label_progress_text = tk.StringVar()
        if self._initialized_ui:
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

        for i, epub_path in enumerate(self.epubsPathList):
            try:
                if not self.output_folder:
                    output_path = os.path.dirname(epub_path) + "/epub2cbz"
                    Path(output_path).mkdir(parents=True, exist_ok=True)
                else:
                    output_path = self.output_folder
                logger.info(f"Processing '{epub_path}'")
                logger.info(f"File '{output_path}' will be created")
                zipfile_name = os.path.basename(epub_path)
                logger.debug(Path(output_path, zipfile_name))
                tmpfd, tmpname = tempfile.mkstemp(dir=output_path)
                os.close(tmpfd)
                self.newCbzName = (output_path + "/" + zipfile_name).replace(
                    re.findall(r"(?i).*(\.[a-z]+$)", epub_path)[0]
                    , ".cbz")
                if os.path.exists(self.newCbzName):
                    os.remove(tmpname)
                    raise FileExistsError
                self._processFile(epub_path, tmpname)
                os.rename(tmpname, self.newCbzName)
                logger.info(f"Successfuly created '{self.newCbzName}'")
                processed_counter += 1
                label_progress_text.set(
                    f"Processed: {processed_counter}/{total} - {processed_errors} errors")
                if self._initialized_ui:
                    try:
                        self.listbox_1.delete(0, tk.END)
                    except Exception as e:
                        print(e)
            except FileExistsError as e:
                logger.error(f"Error processing file '{epub_path}'. It already exists: {str(e)}", exc_info=False)
                processed_errors += 1
            except Exception as e:
                print(e)
                logger.error(f"Error processing file '{epub_path}': {str(e)}", e)
                processed_errors += 1
                try:
                    # noinspection PyUnboundLocalVariable
                    os.remove(tmpname)
                except UnboundLocalError: # we just want to make sure there are no leftover files
                    pass
            if self._initialized_ui:
                # noinspection PyUnboundLocalVariable
                pb_root.update()
                percentage = ((processed_counter + processed_errors) / total) * 100
                style.configure('text.Horizontal.TProgressbar',
                                text='{:g} %'.format(round(percentage, 2)))  # update label
                pb['value'] = percentage
                label_progress_text.set(
                    f"Processed: {(processed_counter + processed_errors)}/{total} files - {processed_errors} errors")
        logger.info("Completed processing for all selected files")

    def _processFile(self, zipfile_path, tmpname):
        logger.info("Inside process")
        with zipfile.ZipFile(zipfile_path, 'r') as zin:
            with zipfile.ZipFile(tmpname, 'w') as zout:

                images_in_ImagesFolder = [v for v in zin.infolist() if
                                          "images/" in v.filename]  # Notes all folders to not process them.
                if not images_in_ImagesFolder:
                    raise FileNotFoundError
                covers = [v for v in zin.namelist() if re.match(r"(?i)cover\.[a-z]+", v)]
                if covers:
                    if self.convert_to_webp:
                        # zout.writestr(covers[0],  zin.read(covers[0]))
                        raise NotImplementedError
                        # TODO webp convert
                        pass
                    else:
                        zout.writestr(covers[0], zin.read(covers[0]))

                for image in images_in_ImagesFolder:
                    image_name = image.filename.split("/")
                    logger.debug(f"Processing file {image.filename}")
                    if re.match(r"(?i).*\.[a-z]+", image_name[-1]):
                        image_name = image_name[-1]
                        zout.writestr(image_name, zin.read(image))
                        logger.debug(f"Added '{image.filename}' to new tempfile")

    def _select_files(self):

        self.epubsPathList = list[str]()
        files_IO = askopenfiles(parent=self.master, initialdir=self.settings.get("library_folder_path"),
                                title="Select .epubs files to extract to .cbz",
                                filetypes=(("epub Files", ".epub"),))
        for file in files_IO:
            self.epubsPathList.append(file.name)
            displayed_file_path = f"...{file.name[-65:]}"
            self.listbox_1.insert(tk.END, displayed_file_path)
            self.listbox_1.yview_moveto(1)

        # self.run()

    def start_ui(self):
        # build ui
        self.master.title("Epub2Cbz Converter")
        self.frame_1 = tk.Frame(self.master)

        self.label_1 = tk.Label(self.frame_1)
        self.label_1.configure(font='{Title} 20 {}', text='EPUB 2 CBZ')
        self.label_1.grid(column='0', row='0')
        self.label_2 = tk.Label(self.frame_1)
        self.label_2.configure(font='{SUBTITLE} 12 {}',
                               text='This script extracts the images from a .epub file to a .cbz file.')
        self.label_2.grid(column='0', row='1')
        self.button_1 = tk.Button(self.frame_1)
        self.button_1.configure(text='Load .epub file')
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

        self._progressbar_frame = tk.Frame(self.frame_1)
        self._progressbar_frame.grid(column=0, row=6)
        self.button_2 = tk.Button(self.frame_1)
        self.button_2.configure(text='Change output folder')
        self.button_2.grid(column='0', row=7)
        self.button_2.configure(command=self._change_out_folder)
        self.label_4 = tk.Label(self.frame_1)
        self.label_4.configure(text='Selected folder:\nfile_path/epub2cbz/')
        self.label_4.grid(column='0', row=8)

        self.frame_1.configure(height='200', padx='60', pady='60', width='200')
        self.frame_1.pack(anchor='center', expand='true', fill='both', side='top')
        self.frame_1.grid_anchor('center')

        self._initialized_ui = True

    def _change_out_folder(self):
        self.output_folder = askdirectory(parent=self.master, initialdir=self.settings.get("library_folder_path"))
        self.label_4.configure(text="Selected folder:\n" + self.output_folder)

    def run(self):
        self.master.mainloop()


if __name__ == '__main__':
    import pathlib
    from logging.handlers import RotatingFileHandler
    import sys

    #
    PROJECT_PATH = pathlib.Path(__file__).parent
    rotating_file_handler = RotatingFileHandler(f"{PROJECT_PATH}/epub2cbz.log", maxBytes=1025760,
                                                backupCount=1)
    #
    # logging.getLogger('PIL').setLevel(logging.WARNING)
    formatter = logging.Formatter()
    #
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - epub2cbz - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)]
                        # filename='/tmp/myapp.log'
                        )
    # logger.info("Starting standalone Converter")
    #
    # inputStr = input("Write the path to the epub files you want to convert to cbz.")
    # if not inputStr:
    #     print("No files selected")
    #     exit()
    # filenames = glob.glob(inputStr)
    # if not filenames:
    #     print("No files found")
    #     exit()
    root = tk.Tk()
    app = App(root)
    app.run()
