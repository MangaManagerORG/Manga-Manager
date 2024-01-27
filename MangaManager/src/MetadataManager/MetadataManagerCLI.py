import itertools
import logging
import shutil
import sys
import textwrap
import time

import prompt_toolkit
from prompt_toolkit import prompt
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator

from common.models import ComicInfo
from src.Common.LoadedComicInfo.LoadedComicInfo import LoadedComicInfo
from src.Common.utils import ShowPathTreeAsDict
from src.MetadataManager.MetadataManagerLib import MetadataManagerLib


def prompt_autocomplete():
    app = get_app()
    b = app.current_buffer
    if b.complete_state:
        b.complete_next()
    else:
        b.start_completion(select_first=False)


def grouper(n, iterable, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(fillvalue=fillvalue, *args)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


bindings = KeyBindings()
app = None


@bindings.add('c-q')
def _(event: prompt_toolkit.key_binding.KeyPressEvent):
    """Exit when `c-q` is pressed. """
    event.app.running = False
    app.quit()


@bindings.add('c-p')
def _(event: prompt_toolkit.key_binding.KeyPressEvent):
    """Exit when `c-q` is pressed."""
    event.app.running = False
    event.app.exit()
    # app.quit()
    app.process()


@bindings.add('c-l')
def _(event: prompt_toolkit.key_binding.KeyPressEvent):
    """Exit when `c-l` is pressed."""
    app.restart()
    event.app.exit()
    app.quit()
    print("Selected files will be shown for 10 seconds")
    print("\033[%d;%dH" % (0, 0))
    print(f"{' '*int(shutil.get_terminal_size().columns)}\n"* int(shutil.get_terminal_size().lines))
    print("\033[%d;%dH" % (0, 0))
    # print("\033[%d;%dH" % (row, 0))
    print("Selected files will be shown for 10 seconds")
    time.sleep(10)


logger = logging.getLogger()


class App(MetadataManagerLib):
    def on_processed_item(self, loaded_info: LoadedComicInfo):
        pass

    def on_manga_not_found(self, exception, series_name):
        pass

    def __init__(self, file_paths: list[str]):
        self.is_cli = True
        self._restart = False
        self.terminal_height = int(shutil.get_terminal_size().lines)
        self.terminal_width = int(shutil.get_terminal_size().columns)
        self.selected_files_path = file_paths
        self.serve_ui()

    def _parse_lcinfo_list_to_gui(self, loaded_cinfo_list) -> ComicInfo:

        displayed_gui = self.new_edited_cinfo = ComicInfo()

        for cinfo_tag in self.cinfo_tags:
            tag_values = set()
            for loaded_cinfo in loaded_cinfo_list:
                tag_value = str(loaded_cinfo.cinfo_object.get_by_tag_name(cinfo_tag))
                tag_values.add(tag_value if tag_value not in ("",-1,0,"-1","0") else None)
            tag_values = tuple(tag_values)
            tag_values_len = len(tag_values)

            # All files have the same content for this field

            if tag_values_len == 1 and tag_values[0] not in ("", -1, 0, "-1", "0", None):
                displayed_gui.get_by_tag_name(cinfo_tag, tag_values[0])
            # Multiple values across different files for this field
            elif tag_values_len > 1:
                # Append "multiple_values" string to the suggestion listbox
                tag_values = (self.MULTIPLE_VALUES_CONFLICT,) + tag_values
                displayed_gui.get_by_tag_name(cinfo_tag, self.MULTIPLE_VALUES_CONFLICT)

    def serve_ui(self):
        self.open_cinfo_list()
        # self.merge_changed_metadata()
        global app
        app = self
        self.terminal_width_half = int(self.terminal_width / 2 - 40)
        custom_entered_values = []
        self.clear()

        self._parse_lcinfo_list_to_gui(self.loaded_cinfo_list)
        self.process()
        self.running = True
        # Set the validator for the user prompts.
        is_valid_tag = Validator.from_callable(
            self._is_valid_tool,
            error_message='Not a valid tool. Select one in the list',
            move_cursor_to_end=False)
        while self.running:
            # Clear terminal, so it will redraw because of the loop with the modified values.
            self.clear()
            # Display current values
            for tag_1, tag_2 in grouper(2, self.cinfo_tags, fillvalue=None):

                # We get 2 different values to support the 2 column layout and also support wrapping the text if multiline
                value_1 = textwrap.wrap(str(self.new_edited_cinfo.get_by_tag_name(tag_1)), width=self.terminal_width_half) or [""]
                if tag_2:
                    value_2 = textwrap.wrap(str(self.new_edited_cinfo.get_by_tag_name(tag_2)), width=self.terminal_width_half) or [""]
                else:
                    value_2 = [""]
                print_once = False
                print(" " * self.terminal_width, end="\r")
                # Divide/wrap both strings. Make a list of each line.
                # Add empty strings to the list of lines with less lines to allow consistent wrapping
                for val_1, val2 in itertools.zip_longest(value_1, value_2, fillvalue=" "):
                    # Print one allow to not print the label on each row if the text is being wrapped in multiple lines
                    if not print_once:
                        print(f"{bcolors.OKBLUE if tag_1 in custom_entered_values else ''}"+f"{tag_1}".ljust(16) +
                              f"{bcolors.ENDC if tag_1 in custom_entered_values else ''}:  ", end='')
                    else:
                        print(f" ".ljust(19), end="")
                    # Print the actual value inline:
                    print(f"{val_1.ljust(self.terminal_width_half)}", end='  ')

                    if not print_once:
                        print(f"{bcolors.OKBLUE if tag_2 in custom_entered_values else ''}" + f"{tag_2}".ljust(16) +
                              f"{bcolors.ENDC if tag_2 in custom_entered_values else ''}:  ", end='')
                    else:
                        print(f" ".ljust(19), end="")
                    print(f"{val2}")
                    # Set the flag that the labels have been printed
                    print_once = True

            # Prompt to have the user select what tag to edit
            choosed_tag = prompt("Select tag to edit (Use arrow keys to navigate) ",
                                 completer=WordCompleter(self.cinfo_tags),
                                 validator=is_valid_tag, pre_run=prompt_autocomplete,
                                 bottom_toolbar="Exit:ctrl+q - Process:ctrl+p - Show Selected:ctrl+l",
                                 key_bindings=bindings)
            if choosed_tag is None:
                logger.warning("No tag selected. Restarting")
                continue
            if self._restart:
                self._restart = False
                continue
            if not self.running:
                return
            # User selected one tag. If it has prefefined values, show a list of them and let the user select those.
            # If one field has multiple values from different files show a list of those.
            # Adds an option "Custom" to custom enter the value
            print(f"You selected {bcolors.HEADER}{choosed_tag}{bcolors.ENDC}")
            choosed_value = ""
            if self.new_edited_cinfo.get_by_tag_name(choosed_tag) == self.MULTIPLE_VALUES_CONFLICT:
                print("Multiple values conflict. Select one value to keep."
                      f" '{bcolors.HEADER}Cancel{bcolors.ENDC}' to cancel editing."
                      f" '{bcolors.HEADER}Custom{bcolors.ENDC}' to manually enter a new value."
                      f" '{bcolors.HEADER}None{bcolors.ENDC}' to clear the content")
                if choosed_tag == "AgeRating":
                    validation_vals = ComicInfo.AgeRating.list()
                elif choosed_tag == "Manga":
                    validation_vals = ComicInfo.Manga.list()
                elif choosed_tag == "BlackAndWhite":
                    validation_vals = ComicInfo.YesNo.list()
                elif choosed_tag == "CommunityRating":
                    validation_vals = range(1,5)
                else:
                    validation_vals = ["Cancel", "None", "Custom",
                     *[lcinfo.cinfo_object.get_by_tag_name(choosed_tag)
                       for lcinfo in self.loaded_cinfo_list
                       if lcinfo.cinfo_object.get_by_tag_name(choosed_tag)]]

                choosed_value = prompt(f"Value to keep as '{choosed_tag}': ",
                                       completer=WordCompleter(validation_vals),
                                       pre_run=prompt_autocomplete,
                                       validator=Validator.from_callable(lambda value: value in validation_vals,
                                                                         error_message="Invalid value. Select one in the list",
                                                                         move_cursor_to_end=False))
            if choosed_value == "Cancel":
                continue
            elif choosed_value == "None":
                choosed_value = None
            elif choosed_value == "Custom" or self.new_edited_cinfo.get_by_tag_name(choosed_tag) != self.MULTIPLE_VALUES_CONFLICT:
                alt_enter = " (Alt+Enter to save)" if choosed_tag == "Summary" else ""
                # Make the prompt to edit the value. Make it multiline if the tag is "Summary"
                choosed_value = prompt(f"Write new value for {choosed_tag}{alt_enter}: ", multiline=choosed_tag == "Summary")
            # Mark the field as modified.
            custom_entered_values.append(choosed_tag)
            # Edit the field in the ""Gui""
            self.new_edited_cinfo.get_by_tag_name(choosed_tag, choosed_value)
    def restart(self):
        self._restart = True

    def clear(self):
        sys.stdout.write("\033[F" * int(self.terminal_height))
        sys.stdout.flush()

    def quit(self):
        self.clear()
        self.running = False
        exit()

    def process(self):
        self.clear()
        self.running = False
        # export = StringIO(self.new_edited_cinfo.to_xml())
        # print(export.getvalue())
        self.merge_changed_metadata(self.loaded_cinfo_list)
        super(App, self).process()
        self.new_edited_cinfo = ComicInfo()
        self._parse_lcinfo_list_to_gui(self.loaded_cinfo_list)

    def tree_selected(self) -> int:
        print("")
        # print(path)
        paths = ShowPathTreeAsDict([lcinfo.file_path for lcinfo in self.loaded_cinfo_list])
        return paths.display_tree()

    def _is_valid_tool(self, value):
        return True if value in self.cinfo_tags else False


    def on_badzipfile_error(self, exception, file_path):
        pass

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):
        pass

