from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class PlayerJoined(Event):
    def __init__(self, message):
        super().__init__(EventType.PLAYER_JOINED, message)