from abc import ABC, abstractmethod


class Page(ABC):
    '''
        A single output page.
        Text will be send to the page until 'is_full()' returns true.
        After that a new page will be used.

        When no more input is incoming (either because the page is full or the input ran out),
        'flush' will be called.
    '''

    @abstractmethod
    def is_full(self):
        # Returns 'true' if the page is full, or 'false' if more lines can be added.
        pass

    @abstractmethod
    def add_line(self, line):
        # Adds a line of output to this page.
        # The line is already terminated with a '\n'.
        pass

    def flush(self):
        # If any cleanup is required when a page is complete, it should be done here.
        pass
