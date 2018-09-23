from .page_builder import StopOutput
from .page_of_height import PageOfHeight
from abc import ABC, abstractproperty, abstractmethod


def add_more_action(handler):
    '''
        Adds a MoreActionHandler class. 
        This allows you to add extra keys that the user can enter on the '--More--' prompt.

        Note that you must pass a callable in here that, when invoked,
        returns a MoreActionHandler.
    '''
    assert callable(handler)
    __HANDLERS.append(handler)


def build_dictionary():
    '''
        Builds the action handlers that define the keys the user can enter
        at the 'more' prompt, and create the corresponding 'Page'.

        This returns a dictionary {key : handler}.
        The  same handler can be mapped to multiple keys
    '''
    def iter_action_handlers():
        return (handler() for handler in __HANDLERS)

    return {
        key: handler
        for handler in iter_action_handlers()
        for key in handler.keys
    }


class MoreActionHandler(ABC):

    @abstractproperty
    def keys(self):
        ''' Returns a list of the keys the user has to enter to trigger this action. '''
        pass

    @abstractmethod
    def build_page(self, page_builder, key_pressed):
        ''' 
            Called when the user pressed one of the keys to trigger this action.
        '''
        pass


class SpaceHandler(MoreActionHandler):
    ''' Invoked when the user types ' '. Displays a new full output page '''

    @property
    def keys(self):
        return [' ']

    def build_page(self, page_builder, key_pressed):
        return PageOfHeight(height=page_builder.get_page_height(), output=page_builder.get_output())


class QuitHandler(MoreActionHandler):
    ''' Invoked when the user types 'q'. Stops output '''

    @property
    def keys(self):
        return ['q', 'Q']

    def build_page(self, page_builder, key_pressed):
        raise StopOutput()


class EnterHandler(MoreActionHandler):
    ''' Invoked when the user types '<enter>'. Displays one more output line '''

    @property
    def keys(self):
        return ['\r', '\n']

    def build_page(self, page_builder, key_pressed):
        return PageOfHeight(height=1, output=page_builder.get_output())


__HANDLERS = [
    SpaceHandler,
    EnterHandler,
    QuitHandler,
]
