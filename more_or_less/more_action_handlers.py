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
    def build_page(self, page_builder, key_pressed, arguments):
        ''' 
            Called when the user pressed one of the keys to trigger this action.

            Arguments:
            ----------

            page_builder:
                The MorePageBuilder instance.
            key_pressed:
                The key the user pressed to trigger this action.
            arguments:
                A dictionary of arguments the user entered on this line before triggering
                this action.
                By default, the only value that can be in there is 'count',
                which will be set if the user entered a number before your action.

                For example, if the user entered '10 ' then the '<space>' action is triggered
                with argument {'count': 10}.
        '''
        pass


class SpaceHandler(MoreActionHandler):
    ''' Invoked when the user types ' '. Displays a new full output page '''

    @property
    def keys(self):
        return [' ']

    def build_page(self, page_builder, key_pressed, arguments):
        page_height = arguments.get('count', page_builder.get_page_height())
        return PageOfHeight(height=page_height, output=page_builder.get_output())


class QuitHandler(MoreActionHandler):
    ''' Invoked when the user types 'q'. Stops output '''

    @property
    def keys(self):
        return ['q', 'Q']

    def build_page(self, page_builder, key_pressed, arguments):
        raise StopOutput()


class EnterHandler(MoreActionHandler):
    ''' Invoked when the user types '<enter>'. Displays one more output line '''

    def __init__(self):
        self._page_height = 1

    @property
    def keys(self):
        return ['\r', '\n']

    def build_page(self, page_builder, key_pressed, arguments):
        self._update_page_height(arguments)
        return PageOfHeight(height=self._page_height, output=page_builder.get_output())

    def _update_page_height(self, arguments):
        self._page_height = arguments.get('count', self._page_height)


class CountHandler(MoreActionHandler):
    ''' Invoked when the user types any number. Calls the next action handler with a 'count' argument '''

    def __init__(self):
        self._digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    @property
    def keys(self):
        return self._digits

    def build_page(self, page_builder, key_pressed, arguments):
        arguments['count'] = self._get_count(page_builder, key_pressed)
        return page_builder.build_next_page(arguments)

    def _get_count(self, page_builder, first_key):

        def iter_digits():
            # Read characters as long as the user enters digits
            key_pressed = first_key
            while key_pressed in self._digits:
                yield key_pressed
                key_pressed = input.get_character(prompt_message)
            input.put_back(key_pressed)

        input = page_builder.get_input()
        prompt_message = page_builder.get_prompt_message()

        return int(''.join(iter_digits()))


__HANDLERS = [
    CountHandler,
    SpaceHandler,
    EnterHandler,
    QuitHandler,
]
