from .page import Page


class PageOfHeight(Page):
    '''
        A page that accepts a given number of lines.
        Every line will be forwarded to the given 'output' object
        (of type output.Output).
    '''

    def __init__(self, height, output):
        self._output = output
        self._remaining_lines = height

    def is_full(self):
        return self._remaining_lines == 0

    def add_line(self, line):
        self._remaining_lines = self._remaining_lines - 1
        self._output.write(line)
