from abc import ABC, abstractmethod
import selectors
import logging

class ApplicationType(ABC):
    def __init__(self):
        self.logger = logging.getLogger('app')
        self.sel = selectors.DefaultSelector()

    @abstractmethod
    def start(self):
        ...