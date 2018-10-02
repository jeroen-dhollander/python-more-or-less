from abc import ABC, abstractmethod


class MorePlugin(ABC):
    '''
        A plugin that represents an extra action the user can take on the 'more' prompt.

    '''

    @abstractmethod
    def get_keys(self):
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

    def wrap_page(self, page):
        ''' 
            Called when a new page is created. 
            Gives the plugin to return a wrapper page that can be used to modify/register
            _every_ line, including the ones that are suppressed by other plugins.

            Example usage is counting all the outputted lines.

            Must return a 'Page'. Implementing this method is optional.
        '''
        return page

    @abstractmethod
    def get_help(self):
        '''
            Returns an iterator over 'command', 'help-text' tuples that describe how to use
            this plugin.
            Example:
            yield (' ', 'Display next line of text')
        '''
        pass
