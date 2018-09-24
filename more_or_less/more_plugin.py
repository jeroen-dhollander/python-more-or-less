from abc import ABC, abstractproperty, abstractmethod


class MorePlugin(ABC):
    '''
        A plugin that represents an extra action the user can take on the 'more' prompt.

    '''

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
