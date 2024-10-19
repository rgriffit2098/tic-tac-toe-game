from abc import ABC

class Event(ABC):
    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data

    def get_message_type(self):
        return self.event_type

    def get_data(self):
        return self.data