from abc import ABC, abstractmethod


class Output(ABC):
    '''
        Example API of what is expected from the 'output' object.
        This does not mean it must inherit from this.

        Note that any 'file' object matches this API,
        so files can natively be used as output.
    '''

    @abstractmethod
    def write(self, text):
        pass
