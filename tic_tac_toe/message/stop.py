from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Stop(Event):
    def __init__(self):
        super().__init__(EventType.STOP, "")