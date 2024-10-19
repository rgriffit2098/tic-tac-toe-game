from enum import Enum

class EventType(Enum):
    REGISTER = 1
    DEREGISTER = 2
    START = 3
    STOP = 4
    MOVE = 5
    BOARD_UPDATE = 6
    FIN = 7
    ALERT = 8