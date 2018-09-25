from .more_plugin import MorePlugin
from .page_of_height import PageOfHeight


class OneLinePlugin(MorePlugin):
    ''' 
        Displays one more output line.
        Invoked when the user types '<enter>'. 
    '''

    def __init__(self):
        self._page_height = 1

    @property
    def keys(self):
        return ['\r', '\n']

    def build_page(self, page_builder, key_pressed, arguments):
        self._update_page_height(arguments)
        return PageOfHeight(height=self._page_height, output=page_builder.get_output())

    def get_help(self):
        yield ('<return>', 'Display next k lines of text [{}]*'.format(self._page_height))

    def _update_page_height(self, arguments):
        self._page_height = arguments.get('count', self._page_height)
