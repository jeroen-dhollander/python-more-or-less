from .more_plugin import MorePlugin
from .page_of_height import PageOfHeight


class OnePagePlugin(MorePlugin):
    ''' 
        Displays a new full output page.
        Invoked when the user types ' '. 
    '''

    def get_keys(self):
        return [' ']

    def build_page(self, page_builder, key_pressed, arguments):
        page_height = arguments.get('count', page_builder.get_page_height())
        return PageOfHeight(height=page_height, output=page_builder.get_output())

    def get_help(self):
        yield ('<space>', 'Display next k lines of text [current screen size]')
