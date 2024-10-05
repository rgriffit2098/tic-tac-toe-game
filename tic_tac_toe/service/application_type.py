from abc import ABC, abstractmethod
import selectors

class ApplicationType(ABC):
    def __init__(self):
        self.sel = selectors.DefaultSelector()

    @abstractmethod
    def start(self):
        ...