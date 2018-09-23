from more_or_less.input import Input
import os
import sys


ERASE_LINE = '\x1b[2K'


class TerminalInput(Input):
    '''
        Input object that gets the input from the user terminal.
    '''

    def __init__(self):
        pass

    def prompt(self, message):
        # TODO(jeroend): Implement
        assert False

    def get_character(self, message):
        try:
            print(message, end='', file=self._output)
            sys.stdout.flush()

            return os.read(sys.stdin, 1)
        finally:
            self._erase_prompt_from_output()

    def _erase_prompt_from_output(self):
        self._output.write(ERASE_LINE)
