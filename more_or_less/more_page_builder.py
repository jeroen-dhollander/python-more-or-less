from .page_builder import PageBuilder, StopOutput
from .page_of_height import PageOfHeight
from .terminal_input import TerminalInput
from .terminal_screen import TerminalScreen
import sys


class MorePageBuilder(PageBuilder):
    '''
        A PageBuilder that is intended to work closely the way 'more' works.
        It supports the basic 'more' actions (one-more-page, n-more-lines, find-text).

        Constructor Arguments:
        ----------------------

        input: [type Input]
        output: [type Output]
        screen_dimensions: [type ScreenDimensions]

        If no constructor arguments are passed,
        it defaults to reading input from stdin,
        printing output to stdout,
        and using the screen-dimensions of the terminal window.
    '''

    def __init__(self, input=None, output=None, screen_dimensions=None):
        self._screen_dimensions = screen_dimensions or TerminalScreen()
        self._output = output or sys.stdout
        self._input = input or TerminalInput()

    def build_first_page(self):
        return PageOfHeight(height=self._get_page_height(), output=self._output)

    def build_next_page(self):
        try:
            return self._try_to_build_next_page()
        except KeyboardInterrupt:
            # Stop output on ctrl-c
            raise StopOutput

    def _try_to_build_next_page(self):
        char = self._input.get_character('--More--')

        if char == ' ':
            return PageOfHeight(height=self._get_page_height(), output=self._output)
        if char in ['\r', '\n']:
            return PageOfHeight(height=1, output=self._output)
        if char in ['q', 'Q']:
            raise StopOutput()

        return self._try_to_build_next_page()
        # TODO(jeroend): Do not recurse

    def _get_page_height(self):
        height_reserved_for_more_prompt = 1
        return self._screen_dimensions.get_height() - height_reserved_for_more_prompt

# TODO(jeroen): Catch KeyboardInterrupt (ctrl-c)
# TODO(jeroen): Support help ('h')
