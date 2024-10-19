from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class BoardUpdate(Event):
    def __init__(self, board_info):
        super().__init__(EventType.BOARD_UPDATE, board_info)