class TerminalColors:
    RESET =                 "\x1b[0m"
    BOLD =                  "\x1b[1m"
    CURSIVE =               "\x1b[3m"
    UNDERLINED =            "\x1b[4m"
    REVERSED_COLOR =        "\x1b[7" # Reversed colors
    REVERSED_COLOR_NORMAL = "\x1b[27"

    BLACK =                 "\x1b[30m"
    GREY =                  "\x1b[30m;1"
    RED =                   "\x1b[31m"
    GREEN =                 "\x1b[32m"
    YELLOW =                "\x1b[33m"
    BLUE =                  "\x1b[34m"
    PURPLE =                "\x1b[35m"
    CYAN =                  "\x1b[36m"
    WHITE =                 "\x1b[97m"

    LIGHT_BLACK =           "\x1b[90m"
    LIGHT_GREY =            "\x1b[37"
    LIGHT_RED =             "\x1b[91m"
    LIGHT_GREEN =           "\x1b[92m"
    LIGHT_YELLOW =          "\x1b[93m"
    LIGHT_BLUE =            "\x1b[94m"
    LIGHT_PURPLE =          "\x1b[95m"
    LIGHT_CYAN =            "\x1b[96m"
    LIGHT_WHITE =           "\x1b[97m"

    BG_BLACK  =             "\x1b[4"
    # BG_GREY =             "\x1b[4
    BG_RED    =             "\x1b[41m"
    BG_GREEN  =             "\x1b[42m"
    BG_YELLOW =             "\x1b[43m"
    BG_BLUE   =             "\x1b[44m"
    BG_PURPLE =             "\x1b[45m"
    BG_CYAN   =             "\x1b[46m"
    BG_WHITE  =             "\x1b[107m"

    BG_LIGHT_BLACK =        "\x1b[4"
    BG_GREY =               "\x1b[100"
    BG_LIGHT_RED =          "\x1b[101m"
    BG_LIGHT_GREEN =        "\x1b[102m"
    BG_LIGHT_YELLOW =       "\x1b[103m"
    BG_LIGHT_BLUE =         "\x1b[104m"
    BG_LIGHT_PURPLE =       "\x1b[105m"
    BG_LIGHT_CYAN =         "\x1b[106m"
    BG_LIGHT_WHITE =        "\x1b[107m"
# print( "\x1b[7m Reversed")
# print(TerminalColors.RED + "asdsadsadasdsadsadasd3453244234234")
# # print("\x1b[31;1m" + "asdsadsadasdsadsadasd3453244234234")
# print(TerminalColors.BOLD + TerminalColors.RED + "Sdsadsadasda")


# import logging
# logging.getLogger()
#
# # print(TerminalColors.BLUE + "Aaaa" + TerminalColors.RESET)
# print("\x1b[1m" + "aaa")
# # print("\x1b[21m" + "aaa")
# # print("\x1b[31m" + "aaa")
# # print("\x1b[41m" + "aaa")
# print("\x1b[51m" + "aa sd dad asasd asa")
# print("sda")
# print("sda")
# print("sda")
# print("sda")
# print("\x1b[0m ")
# # TODO: Rectangles for cli
#
if __name__ == '__main__':

    for color in TerminalColors.__dict__:
        if not color.startswith("_"):
            print(TerminalColors.RESET + f"{color:15s}" + TerminalColors.__dict__[color] + "Addsadsadasdas")