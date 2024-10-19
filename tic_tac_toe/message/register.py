from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Register(Event):
    def __init__(self, player_name):
        super().__init__(EventType.REGISTER, player_name)