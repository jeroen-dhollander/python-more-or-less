from .count_plugin import CountPlugin
from .help_plugin import HelpPlugin
from .more_plugin import MorePlugin
from .one_line_plugin import OneLinePlugin
from .one_page_plugin import OnePagePlugin
from .quit_plugin import QuitPlugin
from .search_plugin import SearchPlugin

__plugins = [
    CountPlugin,
    OnePagePlugin,
    OneLinePlugin,
    QuitPlugin,
    SearchPlugin,
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


def get():
    return [plugin() for plugin in __plugins]
