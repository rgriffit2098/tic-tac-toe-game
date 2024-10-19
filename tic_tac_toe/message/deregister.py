from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Deregister(Event):
    def __init__(self, player_name):
        super().__init__(EventType.DEREGISTER, player_name)