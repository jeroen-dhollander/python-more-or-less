from .more_plugin import MorePlugin
from .page_builder import StopOutput


class QuitPlugin(MorePlugin):
    ''' 
        Invoked when the user types 'q'.
        Stops output 
     '''

    def get_keys(self):
        return ['q', 'Q']

    def build_page(self, page_builder, key_pressed, arguments):
        raise StopOutput()

    def get_help(self):
        yield ('q or Q or <interrupt>', 'Exit from more')
