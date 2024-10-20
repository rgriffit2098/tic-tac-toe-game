from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Fin(Event):
    def __init__(self, reason):
        super().__init__(EventType.FIN, reason)