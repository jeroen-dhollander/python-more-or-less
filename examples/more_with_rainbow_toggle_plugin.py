#!/usr/bin/env python
'''
    Example on how to add a plugin that toggles a mode on or off.
    
    The effect is similar to 'more_with_rainbow_page_plugin',
    but this time when you press 'r' all next output will be rainbowified
    (on all next pages).
    Turn it off by pressing 'r' again (but why would you?)
    
    Example usage: ls | more_with_rainbow_toggle_plugin.py

    When the page is full, use 'h' to see the options.
'''
from examples.more_with_rainbow_page_plugin import rainbowify
from more_or_less import LineCountPlugin, MorePlugin, WrappedPage
import more_or_less
import sys


def main():
    more_or_less.add_plugin(RainbowTogglePlugin)

    # Note: toggles are evaluated in the order they are installed,
    # So that means that if you enable both rainbowification and line numbers
    # (press 'r' and 'l'),
    # The line numbers are not rainbowified.
    # To overcome that we remove and reinstall the line numbers plugin
    # Try commenting out the next 2 lines and see the difference if you press 'r' and 'l'.
    more_or_less.remove_plugin(LineCountPlugin)
    more_or_less.add_plugin(LineCountPlugin)

    more_or_less.paginate(input=sys.stdin)


class RainbowTogglePlugin(MorePlugin):

    def __init__(self):
        self._is_enabled = False

    @property
    def keys(self):
        # We trigger our plugin on 'r' and 'R'
        return ['r', 'R']

    def wrap_page(self, page):
        # Wrap ourself around every output page,
        # so we can change the output lines.
        if self._is_enabled:
            return RainbowWrapper(page)
        else:
            return page

    def build_page(self, page_builder, key_pressed, arguments):
        assert key_pressed in ['r', 'R']
        self._is_enabled = not self._is_enabled
        return page_builder.build_next_page(message=f'--Rainbowification is now {self._format_enabled()}--')

    def get_help(self):
        # Help is returned as an iterator over ('key', 'help') tupples
        yield ('r or R', f'Toggle rainbowification [currently {self._format_enabled()}]')

    def _format_enabled(self):
        return {True: 'enabled', False: 'disabled'}[self._is_enabled]


class RainbowWrapper(WrappedPage):
    '''
        Rainbowifies every line.

        By inheriting from 'RepeatableMixin' we support repeating the command by pressing '.'
    '''

    def on_add_line(self, line):
        return rainbowify(line)


if __name__ == "__main__":
    main()
