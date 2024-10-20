from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Move(Event):
    def __init__(self, move_data):
        super().__init__(EventType.MOVE, move_data)