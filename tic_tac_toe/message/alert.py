from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Alert(Event):
    def __init__(self, alert_message):
        super().__init__(EventType.ALERT, alert_message)