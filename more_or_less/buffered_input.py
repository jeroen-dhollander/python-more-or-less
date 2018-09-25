from .input import Input
import queue


class BufferedInput(Input):
    '''
        Input object that allows you to put back characters
        (which are then returned by the next call to 'get_character')
    '''

    def __init__(self, input):
        self._buffered_characters = queue.Queue()
        self._input = input

    def prompt(self, message):
        return self._input.prompt(message)

    def get_character(self, message):
        if not self._buffered_characters.empty():
            return self._buffered_characters.get()
        return self._input.get_character(message)

    def put_back(self, character):
        self._buffered_characters.put(character)
