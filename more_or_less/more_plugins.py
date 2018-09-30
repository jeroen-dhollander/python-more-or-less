from .count_plugin import CountPlugin
from .help_plugin import HelpPlugin
from .line_count_plugin import LineCountPlugin
from .more_plugin import MorePlugin
from .one_line_plugin import OneLinePlugin
from .one_page_plugin import OnePagePlugin
from .quit_plugin import QuitPlugin
from .repeat_plugin import RepeatPlugin
from .search_plugin import SearchPlugin

__plugins = [
    CountPlugin,
    OnePagePlugin,
    OneLinePlugin,
    QuitPlugin,
    LineCountPlugin,
    SearchPlugin,
    RepeatPlugin,
    HelpPlugin,
]


def add_plugin(handler):
    '''
        Adds a MorePlugin class. 
        This allows you to add extra keys that the user can enter on the '--More--' prompt.

        Note that you must pass a callable in here that, when invoked, returns a MorePlugin.
    '''
    assert callable(handler)
    assert isinstance(handler(), MorePlugin)
    __plugins.append(handler)


def remove_plugin(handler):
    '''
        Removes a MorePlugin class. 
    '''
    __plugins.remove(handler)


def get():
    return [plugin() for plugin in __plugins]
