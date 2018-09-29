from .page import Page
from abc import ABC, abstractmethod


class WrappedPage(Page, ABC):
    '''
        Basic class that can be derived from if you need to
        create a Page that
           - records all printed lines
           - can change the printed lines before forwarding.

    '''

    def __init__(self, wrapped_page):
        self.wrapped_page = wrapped_page

    def is_full(self):
        return self.wrapped_page.is_full()

    def add_line(self, line):
        new_line = self.on_add_line(line)
        return self.wrapped_page.add_line(new_line)

    def flush(self):
        return self.wrapped_page.flush()

    @abstractmethod
    def on_add_line(self, line):
        ''' Called with every line. Returns the modified version of the line '''
        pass

    def __getattr__(self, name):
        return getattr(self.wrapped_page, name)
