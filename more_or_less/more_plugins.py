from .count_plugin import CountPlugin
from .more_plugin import MorePlugin
from .one_line_plugin import OneLinePlugin
from .one_page_plugin import OnePagePlugin
from .quit_plugin import QuitPlugin
from .search_plugin import SearchPlugin

__plugins = [
    CountPlugin,
    OneLinePlugin,
    OnePagePlugin,
    QuitPlugin,
    SearchPlugin,
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


def build_dictionary():
    '''
        Builds the action handlers that define the keys the user can enter
        at the 'more' prompt, and create the corresponding 'Page'.

        This returns a dictionary {key : handler}.
        The  same handler can be mapped to multiple keys
    '''
    def iter_action_handlers():
        return (handler() for handler in __plugins)

    return {
        key: handler
        for handler in iter_action_handlers()
        for key in handler.keys
    }
