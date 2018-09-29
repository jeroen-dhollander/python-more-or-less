from abc import ABC, abstractmethod


class RepeatableMixin(ABC):
    '''
       If your Page inherits from this,
       the action it represents can be repeated by pressing '.'
    '''

    @abstractmethod
    def repeat(self):
        ''' 
            Returns an instance of a new version of this page.
            For example, a repeat of a page of height X
            returns a page of height X, on which 0 lines of output have been printed.
    '''
