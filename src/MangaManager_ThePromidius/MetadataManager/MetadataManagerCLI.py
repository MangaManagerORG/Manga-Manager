import itertools
import shutil
import sys
import textwrap

import prompt_toolkit
from prompt_toolkit import prompt
from prompt_toolkit.application.current import get_app
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import Validator

from src.MangaManager_ThePromidius.Common.loadedcomicinfo import LoadedComicInfo
from src.MangaManager_ThePromidius.MetadataManager import comicinfo
from src.MangaManager_ThePromidius.MetadataManager.MetadataManagerLib import MetadataManagerLib


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
def _(event):
    """Exit when `c-q` is pressed. """
    app.quit()

@bindings.add('c-p')
def _(event:prompt_toolkit.key_binding.KeyPressEvent):
    """Exit when `c-q` is pressed."""
    event.app.exit()
    app.proces()


class App(MetadataManagerLib):
    def __init__(self, file_paths: list[str]):
        self.terminal_height = int(shutil.get_terminal_size().lines)
        self.terminal_width = int(shutil.get_terminal_size().columns)
        self.selected_files_path = file_paths
        self.serve_ui()
    def serve_ui(self):
        self.load_cinfo_list()
        # self.merge_changed_metadata()
        global app
        app = self
        self.new_edited_cinfo = merged_info = self.merge_loaded_metadata()
        merged_info.set_Summary(
            "3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r\n\nsdad3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r3dsadasasdasdsadsad3422r")
        print("a")
        self.terminal_width_half = int(self.terminal_width / 2 - 40)
        custom_entered_values =[]
        self.clear()

        self.running = True

        while self.running:
            for tag_1, tag_2 in grouper(2, self.cinfo_tags, fillvalue=None):
                value_1 = textwrap.wrap(str(merged_info.get_attr_by_name(tag_1)), width=self.terminal_width_half) or [""]
                if tag_2:
                    value_2 = textwrap.wrap(str(merged_info.get_attr_by_name(tag_2)), width=self.terminal_width_half) or [""]
                else:
                    value_2 = [""]
                print_once = False
                print(" " * self.terminal_width, end="\r")
                print("─" * self.terminal_width)
                for val_1, val2 in itertools.zip_longest(value_1, value_2, fillvalue=" "):

                    if not print_once:
                        print(f"{bcolors.OKBLUE if tag_1 in custom_entered_values else ''}"+f"{tag_1}".ljust(16) +
                              f"{bcolors.ENDC if tag_1 in custom_entered_values else ''}:  ", end='')
                    else:
                        print(f" ".ljust(19),end="")
                    print(f"{val_1.ljust(self.terminal_width_half)}", end='  ')
                    if not print_once:
                        print(f"{bcolors.OKBLUE if tag_2 in custom_entered_values else ''}" + f"{tag_2}".ljust(16) +
                              f"{bcolors.ENDC if tag_2 in custom_entered_values else ''}:  ", end='')
                    else:
                        print(f" ".ljust(19), end="")
                    print(f"{val2}")
                    print_once = True
            is_valid_tag = Validator.from_callable(
                self._is_valid_tool,
                error_message='Not a valid tool. Select one in the list',
                move_cursor_to_end=False)
            choosed_tag = prompt("Select tag to edit (tab to show options): ", completer=WordCompleter(self.cinfo_tags),
                                 validator=is_valid_tag, pre_run=prompt_autocomplete,
                                 bottom_toolbar="Exit:ctrl+q - Process:ctrl+p",
                                 key_bindings=bindings)
            if not self.running:
                return
            print(f"You selected {choosed_tag}")
            choosed_value = ""
            if merged_info.get_attr_by_name(choosed_tag) == self.MULTIPLE_VALUES_CONFLICT:
                print("Multiple values conflict. Select one value to keep or use custom.")
                if choosed_tag == "AgeRating":
                    validation_vals = comicinfo.AgeRating.list()
                elif choosed_tag == "Manga":
                    validation_vals = comicinfo.Manga.list()
                elif choosed_tag == "BlackAndWhite":
                    validation_vals = comicinfo.YesNo.list()
                elif choosed_tag == "CommunityRating":
                    validation_vals = range(1,5)
                else:
                    validation_vals = ["custom",
                     *[lcinfo.cinfo_object.get_attr_by_name(choosed_tag)
                       for lcinfo in self.loaded_cinfo_list
                       if lcinfo.cinfo_object.get_attr_by_name(choosed_tag)]]

                choosed_value = prompt(f"Value to keep as '{choosed_tag}': ",
                                       completer=WordCompleter(validation_vals),
                                       pre_run=prompt_autocomplete,
                                       validator=Validator.from_callable(lambda value: value in validation_vals,
                                                                         error_message="Invalid value. Select one in the list",
                                                                         move_cursor_to_end=False))

            if choosed_value == "custom" or merged_info.get_attr_by_name(choosed_tag) != self.MULTIPLE_VALUES_CONFLICT:
                alt_enter = " (Alt+Enter to save)" if choosed_tag == "Summary" else ""
                choosed_value = prompt(f"Write new value for {choosed_tag}{alt_enter}: ", multiline=choosed_tag == "Summary")
            custom_entered_values.append(choosed_tag)
            merged_info.set_attr_by_name(choosed_tag, choosed_value)
            self.clear()
    def clear(self):
        sys.stdout.write("\033[F" * int(self.terminal_height))
        sys.stdout.flush()

    def quit(self):
        self.clear()
        self.running = False
        exit()
    def proces(self):
        self.clear()
        self.running = False
        super(App, self).proces()

    #     while True:
    #         is_valid_tool = Validator.from_callable(
    #             self._is_valid_tool,
    #             error_message='Not a valid tool. Select one in the list',
    #             move_cursor_to_end=False)
    #         data = {self.cinfo_tags[0]:"abc"}
    #         multiple_values = False
    #         choosed_tag = prompt("Select tag to edit (tab to show options): ", completer=WordCompleter(self.cinfo_tags),
    #                           validator=is_valid_tool, pre_run=prompt_autocomplete)
    #
    #
    #
    #
    #
    #
    #         for loaded_cinfo in self.loaded_cinfo_list:
    #             b = loaded_cinfo.cinfo_object.get_attr_by_name(choosed_tag)
    #             if b:
    #                 if b not in multiple_values:
    #                     multiple_values.append(f"{os.path.basename(loaded_cinfo.file_path):80}->{b}")
    #         for tag in self.cinfo_tags:
    #
    #             for i in itertools.zip_longest(tag,textwrap.wrap(self.new_edited_cinfo.get_attr_by_name(tag))):
    #                 print(f"{i[0] if i[0] else '':80}", i[1])
    #
    #
    #
    #         textwrap.wrap([tag,self.])
    #         for i in itertools.zip_longest(*wrapped):
    #             print(f"{i[0]:80}", i[1])
    #         if len(multiple_values) > 1:
    #             print("Multiple values selected:")
    #             # print("\n".join(multiple_values))
    #         new_value = prompt(f"{choosed_tag} >", default=self.MULTIPLE_VALUES_CONFLICT,
    #                            mouse_support=True)
    #
    def _is_valid_tool(self, value):
        return True if value in self.cinfo_tags else False

    #
    #

    def on_badzipfile_error(self, exception, file_path):
        pass

    def on_corruped_metadata_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_error(self, exception, loaded_info: LoadedComicInfo):
        pass

    def on_writing_exception(self, exception, loaded_info: LoadedComicInfo):
        pass


# if __name__ == '__main__':
#
#     arguments = argparse.
#
#
#     App(["test_patching/" + path for path in os.listdir("test_patching")])
