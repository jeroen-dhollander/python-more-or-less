from . import more_plugins
from .buffered_input import BufferedInput
from .page_builder import PageBuilder, StopOutput
from .page_of_height import PageOfHeight
from .page_wrapper import PageWrapper
from .terminal_input import TerminalInput
from .terminal_screen import TerminalScreen
import sys


def MorePageBuilder(*args, **kwargs):
    '''
        A PageBuilder that is intended to work closely the way 'more' works.
        It supports the basic 'more' actions (one-more-page, n-more-lines, find-text).

        Extra actions can be installed as plugins, see more_plugins.py

        Constructor Arguments:
        ----------------------

        input: [type Input]
            If not specified we read input from stdin
        output: [type Output]
            If not specified we print output to stdout
        screen_dimensions: [type ScreenDimensions]
            If not specified we use the dimensions of the terminal window
        plugins: [type list of MorePlugin]
            The plugins to load. If not specified will fetch all plugins from more_plugins.py
    '''
    return PageWrapper(_MorePageBuilder(*args, **kwargs))


class _MorePageBuilder(PageBuilder):

    def __init__(self, input=None, output=None, screen_dimensions=None, plugins=None):
        self._screen_dimensions = screen_dimensions or TerminalScreen()
        self._output = output or sys.stdout
        self._input = BufferedInput(input or TerminalInput())

        self._plugins = plugins or more_plugins.get()
        self._action_handlers = _build_plugins_dictionary(self._plugins)

    def build_first_page(self):
        return PageOfHeight(height=self.get_page_height(), output=self._output)

    def build_next_page(self, message=None, arguments=None):
        try:
            return self._try_to_build_next_page(
                message or self.get_prompt_message(),
                arguments or {}
            )
        except KeyboardInterrupt:
            # Stop output on ctrl-c
            raise StopOutput

    def _try_to_build_next_page(self, message, arguments):
        while True:
            key_pressed = self._input.get_character(message)
            if key_pressed in self._action_handlers:
                handler = self._action_handlers[key_pressed]
                return handler.build_page(self, key_pressed=key_pressed, arguments=arguments)

    def get_plugins(self):
        return self._plugins

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


def _build_plugins_dictionary(plugins):

    return {
        key: plugin
        for plugin in plugins
        for key in plugin.keys
    }
