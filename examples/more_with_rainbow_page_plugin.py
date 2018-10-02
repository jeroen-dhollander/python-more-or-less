#!/usr/bin/env python
'''
    Example on how to add a plugin.
    
    The plugin added is triggered through 'r', and adds rainbow colors to every output line.
    Try it, it's fabulous!

    Example usage: ls | more_with_rainbow_page_plugin.py

    When the page is full, use 'h' to see the options.
'''
from more_or_less import MorePlugin, Page, PageOfHeight, RepeatableMixin
import more_or_less
import random
import sys


# See https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
#     http://www.isthe.com/chongo/tech/comp/ansi_escapes.html
# Make text bold, faint, normal, underlined, blinking, crossed-out, ...
_MODIFIERS = list(range(0, 10))
_FOREGROUND_COLORS = list(range(30, 38)) + list(range(90, 98))
_BACKGROUND_COLORS = list(range(40, 48)) + list(range(100, 108))


def main():
    more_or_less.add_plugin(RainbowPlugin)
    more_or_less.paginate(input=sys.stdin)


class RainbowPlugin(MorePlugin):

    def get_keys(self):
        # We trigger our plugin on 'r' and 'R'
        return ['r', 'R']

    def build_page(self, page_builder, key_pressed, arguments):
        # Return our output page.
        # For the page height, we either use the value provided on the command line
        # (if the user typed 10r),
        # or we default to the screen height
        height = arguments.get('count', page_builder.get_page_height())
        return RainbowPage(output=page_builder.get_output(), height=height)

    def get_help(self):
        # Help is returned as an iterator over ('key', 'help') tupples
        yield ('r or R', 'Rainbowify the next k lines of text [current screen height]')


class RainbowPage(Page, RepeatableMixin):
    '''
        Rainbowifies every line.

        By inheriting from 'RepeatableMixin' we support repeating the command by pressing '.'
    '''

    def __init__(self, height, output):
        self._page = PageOfHeight(height, output=output)

    def is_full(self):
        return self._page.is_full()

    def add_line(self, line):
        return self._page.add_line(rainbowify(line))

    def flush(self):
        return self._page.flush()

    def repeat(self):
        return RainbowPage(self._page.height, self._page.output)


def rainbowify(line):
    modifier = random.choice(_MODIFIERS)
    foreground = random.choice(_FOREGROUND_COLORS)
    background = random.choice(_BACKGROUND_COLORS)
    return f'\x1b[{modifier};{foreground};{background}m{line}\x1b[0m'


if __name__ == "__main__":
    main()
