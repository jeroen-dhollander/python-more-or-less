from .more_plugin import MorePlugin
from .wrapped_page import WrappedPage


class LineCountPlugin(MorePlugin):
    ''' 
        Prints the current line number on '='.
        Toggles prefixing all lines with the line number on 'l'.
    '''

    def __init__(self):
        self.line_numbers_enabled = False
        self.line_count = 0

    def get_keys(self):
        return ['=', 'l', 'L']

    def get_help(self):
        yield ('=', 'Display current line number')
        yield ('l', f'Toggle printing line number on every line [currently {self._format_enabled()}]')

    def build_page(self, page_builder, key_pressed, arguments):
        if key_pressed == '=':
            return page_builder.build_next_page(message=f'--{self.line_count}--')
        elif key_pressed == 'l':
            self.line_numbers_enabled = not self.line_numbers_enabled
            return page_builder.build_next_page(message=f'--Line numbers are now {self._format_enabled()}--')
        else:
            assert False, 'Unexpected key event'

    def wrap_page(self, page):
        return _LineCounter(self, page)

    def _format_enabled(self):
        return {
            True: 'enabled',
            False: 'disabled',
        }.get(self.line_numbers_enabled)


class _LineCounter(WrappedPage):

    def __init__(self, line_count_plugin, wrapped_page):
        super().__init__(wrapped_page)
        self._plugin = line_count_plugin

    def on_add_line(self, line):
        self._bump_line_count()
        if self.must_add_line_number():
            return self.add_line_number(line)
        else:
            return line

    def _bump_line_count(self):
        self._plugin.line_count = self._plugin.line_count + 1

    def must_add_line_number(self):
        return self._plugin.line_numbers_enabled

    def add_line_number(self, text):
        return f'{self._plugin.line_count}: {text}'
