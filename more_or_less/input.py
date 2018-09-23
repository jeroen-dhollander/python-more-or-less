from abc import ABC, abstractmethod


class Input(ABC):
    '''
        Input object that supports either reading a single character,
        or a complete input line.
    '''

    @abstractmethod
    def prompt(self, message):
        pass

    @abstractmethod
    def get_character(self, message):
        pass
