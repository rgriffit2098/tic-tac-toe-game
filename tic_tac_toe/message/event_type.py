from enum import Enum

class EventType(Enum):
    REGISTER = 1
    DEREGISTER = 2
    START = 3
    STOP = 4
    MOVE = 5
    ORDER = 6
    BOARD_UPDATE = 7
    FIN = 8
    PLAYER_JOINED = 9
    PLAYER_LEFT = 10