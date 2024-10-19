from tic_tac_toe.message.event import Event
from tic_tac_toe.message.event_type import EventType

class Order(Event):
    def __init__(self, order_data):
        super().__init__(EventType.MOVE, order_data)