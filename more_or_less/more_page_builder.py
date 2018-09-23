from . import more_action_handlers
from .page_builder import PageBuilder, StopOutput
from .page_of_height import PageOfHeight
from .terminal_input import TerminalInput
from .terminal_screen import TerminalScreen
from more_or_less.buffered_input import BufferedInput
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
        self._input = BufferedInput(input or TerminalInput())

        self._action_handlers = more_action_handlers.build_dictionary()

    def build_first_page(self):
        return PageOfHeight(height=self.get_page_height(), output=self._output)

    def build_next_page(self, arguments=None):
        try:
            return self._try_to_build_next_page(arguments or {})
        except KeyboardInterrupt:
            # Stop output on ctrl-c
            raise StopOutput

    def _try_to_build_next_page(self, arguments):
        while True:
            key_pressed = self._input.get_character(self.get_prompt_message())
            if key_pressed in self._action_handlers:
                handler = self._action_handlers[key_pressed]
                return handler.build_page(
                    self,
                    key_pressed=key_pressed,
                    arguments=arguments)

    def get_page_height(self):
        height_reserved_for_more_prompt = 1
        return self._screen_dimensions.get_height() - height_reserved_for_more_prompt

    def get_output(self):
        return self._output

    def get_input(self):
        ''' Returns the BufferedInput object used to get the user input '''
        return self._input

    def get_prompt_message(self):
        return '--More--'

# TODO(jeroen): Catch KeyboardInterrupt (ctrl-c)
# TODO(jeroen): Support help ('h')
