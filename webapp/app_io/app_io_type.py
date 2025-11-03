from enum import Enum, auto


class AppIOType(Enum):
    BOOL = auto()
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    FILENAME = auto()
    URL = auto()
    DATETIME = auto()
    DATE = auto()
    TIME = auto()
    SELECTION = auto()
    FILE = auto()
    BINARY_FILE = auto()
    TABLE = auto()