import os
import sys

from .input import Input


# http://ascii-table.com/ansi-escape-sequences.php
_CLEAR_TEXT_ON_LINE = '\x1b[2K'
_MOVE_CURSOR_TO_START_OF_LINE = '\x1b[1000D'  # Actually moves the cursor 1000 characters to the left
ERASE_LINE = _CLEAR_TEXT_ON_LINE + _MOVE_CURSOR_TO_START_OF_LINE


class TerminalInput(Input):
    '''
        Input object that gets the input from the user terminal.
    '''

    def __init__(self):
        self._input = _get_interactive_input_stream()
        self._output = sys.stdout

    def prompt(self, message):
        self._print_prompt(message)
        return self._input.readline().rstrip('\n')

    def get_character(self, message):
        try:
            self._print_prompt(message)
            return _read_character(self._input)
        finally:
            self._erase_input_prompt()

    def _print_prompt(self, message):
        print(message, end='', file=self._output, flush=True)

    def _erase_input_prompt(self):
        self._output.write(ERASE_LINE)


def _get_interactive_input_stream():
    if sys.stdin.isatty():
        return sys.stdin
    else:
        '''
            We come here if the stdin is read from a file/pipe.
            In this case, that is probably the content we want to paginate,
            so we will open a new interactive input-stream.

            See https://stackoverflow.com/questions/46441623/get-user-input-while-reading-stdin-from-a-pipe/46445955#46445955
        '''
        return _create_interactive_input_stream()


def _create_interactive_input_stream():
    if sys.platform in ('win32', 'cygwin'):
        raise AssertionError('Reading interactive input while stdin is not a tty is not supported on Windows')
    try:
        return open('/dev/tty', 'r')
    except FileNotFoundError:
        raise AssertionError('Terminal is unavailable for interactive input (could not open /dev/tty).')


def _read_character(file):
    '''' reads a single character. Does not wait for 'enter' '''
    import termios
    import tty
    fd = file.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        return os.read(fd, 1).decode('utf-8')
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
