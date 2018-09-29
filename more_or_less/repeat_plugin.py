from .more_plugin import MorePlugin

_NON_REPEATABLE_COMMAND = '--Previous command can not be repeated--'


class RepeatPlugin(MorePlugin):
    '''
        Allows repeating of the previous command by pressing '.'.
        This only works if the previous command implements the RepeatableMixin.
    '''

    def __init__(self):
        self._last_page = None

    @property
    def keys(self):
        return ['.']

    def build_page(self, page_builder, key_pressed, arguments):
        # DO_NOT_PUSH test no previous page
        if _is_repeatable(self._last_page):
            return self._last_page.repeat()
        else:
            return page_builder.build_next_page(message=_NON_REPEATABLE_COMMAND)

    def wrap_page(self, page):
        self._last_page = page
        return page

    def get_help(self):
        yield ('.', 'Repeat previous command')


def _is_repeatable(page):
    return hasattr(page, 'repeat')
