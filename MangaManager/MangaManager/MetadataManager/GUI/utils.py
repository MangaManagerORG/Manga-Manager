import re

INT_PATTERN = re.compile("^-*\d*(?:,?\d+|\.?\d+)?$")

def validate_int(value) -> bool:
    """
    Validates if all the values in the string matches the int pattern
    :param value:
    :return: true if matches
    """
    ilegal_chars = [character for character in str(value) if not INT_PATTERN.match(character)]
    return not ilegal_chars


def center(win):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()