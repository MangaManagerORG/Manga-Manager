import enum


class CoverActions(enum.Enum):
    RESET = 0  # Cancel current selected action
    REPLACE = 1
    DELETE = 2
    APPEND = 3