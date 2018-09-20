from abc import ABC, abstractmethod


class PageBuilder(ABC):
    '''
        Builds the output pages (of type Page) used in the paginator.

        When the paginator start, it will call build_first_page.
        When that page is full, it will call build_next_page.
        This is repeated until there is no more input.

    '''

    @abstractmethod
    def build_first_page(self):
        pass

    @abstractmethod
    def build_next_page(self):
        '''
            Raises 'OutputAborted' exception if no next page can/should be created.
        '''
        pass
