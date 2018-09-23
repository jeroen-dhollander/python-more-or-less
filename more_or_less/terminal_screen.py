from more_or_less.screen_dimensions import ScreenDimensions
import os
import shutil
import sys


class TerminalScreen(ScreenDimensions):
    '''
        Retrieves the dimensions of the current terminal window
    '''

    def __init__(self):
        pass

    def get_height(self):
        return self._get_height_and_width()[0]

    def get_width(self):
        return self._get_height_and_width()[1]

    def _get_height_and_width(self):
        columns, lines = shutil.get_terminal_size()
        return lines, columns
