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
        self._terminal = self._create_terminal()
        self._output = sys.stdout

    def prompt(self, message):
        self._print_prompt(message)
        return self._terminal.read_line().rstrip('\r\n')

    def get_character(self, message):
        try:
            self._print_prompt(message)
            return self._terminal.read_character()
        finally:
            self._erase_input_prompt()

    def _print_prompt(self, message):
        print(message, end='', file=self._output, flush=True)

    def _erase_input_prompt(self):
        self._terminal.clear_line()

    @classmethod
    def _create_terminal(cls):
        if sys.platform in ('win32', 'cygwin'):
            return _WindowsTerminal()
        else:
            return _LinuxTerminal()


class _LinuxTerminal(object):

    def __init__(self):
        self._input = self._get_interactive_input_stream()

    def read_line(self):
        return self._input.readline()

    def read_character(self):
        '''' reads a single character. Does not wait for 'enter' '''
        import termios
        import tty
        fd = self._input.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            return os.read(fd, 1).decode('utf-8')
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def clear_line(self):
        self._output.write(ERASE_LINE)

    @classmethod
    def _get_interactive_input_stream(cls):
        if sys.stdin.isatty():
            return sys.stdin
        else:
            '''
                We come here if the stdin is read from a file/pipe.
                In this case, that is probably the content we want to paginate,
                so we will open a new interactive input-stream.

                See https://stackoverflow.com/questions/46441623/get-user-input-while-reading-stdin-from-a-pipe/46445955#46445955
            '''
            try:
                return open('/dev/tty', 'r')
            except FileNotFoundError:
                raise AssertionError('Terminal is unavailable for interactive input (could not open /dev/tty).')


class _WindowsTerminal(object):

    interrupts = [
        '\x03',  # Ctrl-C
        '\x11',  # Ctrl-Q
    ]

    def __init__(self):
        pass

    def read_line(self):
        def _read_until_newline():
            import msvcrt
            char = ''
            while char != b'\r':
                char = msvcrt.getche()
                yield char.decode('utf-8')

        return ''.join(_read_until_newline())

    def read_character(self):
        import msvcrt
        result = msvcrt.getch().decode('utf-8')
        if result in self.interrupts:
            raise KeyboardInterrupt
        return result

    def clear_line(self):
        # There is no clean way to clear the last output line,
        # So we simply
        #    * Go to the start of the line
        #    * Write 40 spaces
        #    * Go to the start of the line
        sys.stdout.write("\r" + " " * 40 + "\r")
        return
        pass
