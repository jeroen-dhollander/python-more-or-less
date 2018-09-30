#!python
from .more_page_builder import MorePageBuilder
from .page_builder import StopOutput
import queue
import threading


# Signal to send to the input queue when there is no more input
END_OF_INPUT = None
# Return code if output was interrupted by the user (e.g. the user pressed ctrl+c)
OUTPUT_STOPPED = 'OUTPUT_STOPPED'


def paginate(
        input,
        output=None,
        prompt=None,
        screen_dimensions=None,
        plugins=None,
        page_builder=None,
        asynchronous=False):
    '''
        Paginates the input, similar to how 'more' works in bash.

        Reads from input until the output window is full.
        Then prompts the user for an action before reading more input.

        Pseudo-logic:
        -------------

        page = page_builder.build_first_page()
        for line in <input-lines>:
            if page.is_full():
                page.flush()
                page = page_builder.build_next_page()
            page.add_line(line)

        Arguments:
        ----------

        input: [type iterable or Queue]
            The input text that should be paginated.
            This must either be an iterable over text (e.g. a list or a file), or an instance of queue.Queue.

            It is not required that each returned string is a complete line. 
            The paginator will combine incomplete lines until a '\n' is encountered.

            If it is a queue.Queue, you must pass 'END_OF_INPUT' into the queue when no more input is expected.
            This will flush the final incomplete line (if any) to the output.
            Note that you can NOT use queue.join() to detect all input has been processed
            (as that just raises issues if the user decides to abort the output halfway through).
            Instead, if you use 'asynchronous=True' you can join the returned context.

        output: [type Output]
            If not specified we print output to stdout

        prompt: [type Input]
            Used when prompting the user for actions.
            Defaults to reading from stdin.

        screen_dimensions: [type ScreenDimensions]
            Used to know the height of the output window 
            (which is used to decide how many lines to print before we consider a page 'full').
            Defaults to using the dimensions of the terminal window.

        plugins: [type list of MorePlugin]
            The plugins to load. These plugins decide what actions are available on the 'more' prompt.
            If not specified will fetch all plugins from more_plugins.py

        asynchronous: [type bool] 
            If true the 'paginate' call will return instantly and run asynchronously.
            In this case a context is returned on which you can call 'context.join([timeout])' 
            to block until all lines are sent to the output.

        page_builder: [type PageBuilder]
            The object that will create the output pages whenever a page is full.
            Must be an instance of 'PageBuilder'.
            If specified we ignore the values of output, prompt, screen_dimensions and plugins.


        Returns:
        --------

        A joinable 'context' if asynchronous is True
        OUTPUT_STOPPED if the user stopped the output (for example using ctrl+c)

    '''

    page_builder = page_builder or MorePageBuilder(
        input=prompt,
        output=output,
        screen_dimensions=screen_dimensions,
        plugins=plugins)

    if asynchronous:
        thread = threading.Thread(
            target=paginate,
            kwargs={
                'input': input,
                'page_builder': page_builder,
                'asynchronous': False,
            },
        )
        thread.start()
        return thread

    paginator = Paginator(page_builder)
    if isinstance(input, queue.Queue):
        return paginator.paginate_from_queue(input)
    else:
        return paginator.paginate(input)


class Paginator(object):
    '''
        Paginates given input text, similar to how 'more' works in bash.

        See help of 'paginate' for a more detailed description of the behavior.

        There are 3 ways to send input text:
            - pass an iterable to self.paginate.
            - pass a queue to self.paginate_from_queue.
            - call 'add_text' repeatedly until all text has been sent in, then call 'flush_incomplete_line'.

        Each of these methods returns 'OUTPUT_STOPPED' if the user stopped the output (for example using ctrl+c)
    '''

    def __init__(self, page_builder):
        self._page_builder = page_builder
        self._lines = _LineCollector()

        self._page = self._page_builder.build_first_page()

    def paginate(self, iterable):
        '''
            Iterates over the iterable, and paginates all the text it returns
        '''
        try:
            for text in iterable:
                self._try_to_add_text(text)

            self.flush_incomplete_line()
        except StopOutput:
            return OUTPUT_STOPPED

    def paginate_from_queue(self, input_queue):
        '''
            Iterates over the queue, and paginates all the text it returns.
            Stops paginating when END_OF_INPUT is encountered on the queue.
        '''
        return self.paginate(QueueIterator(input_queue))

    def add_text(self, input_text):
        '''
            Splits the input_text into lines, and paginates them.
            Can be called multiple times.

            When you're done you must call 'flush_incomplete_line'
            to ensure the last incomplete input line is sent to the output.
        '''
        try:
            self._try_to_add_text(input_text)
        except StopOutput:
            return OUTPUT_STOPPED

    def _try_to_add_text(self, input_text):
        self._lines.add(input_text)

        for line in self._lines.pop_complete_lines():
            self._paginate_and_print_text(line)

    def flush_incomplete_line(self):
        try:
            self._try_to_flush_incomplete_line()
        except StopOutput:
            return OUTPUT_STOPPED

    def _try_to_flush_incomplete_line(self):
        if len(self._lines.incomplete_line):
            self._paginate_and_print_text(self._lines.pop_incomplete_line())
        self._page.flush()

    def _paginate_and_print_text(self, text):
        if self._page.is_full():
            self._start_new_page()
        self._output_text(text)

    def _start_new_page(self):
        self._page.flush()
        self._page = self._page_builder.build_next_page()

    def _output_text(self, text):
        self._page.add_line(text)


class _LineCollector(object):
    '''
        Collects the input text and allows us to walk over the complete lines only.
        example:
             self.add('first ')
             self.add('line \nsecond line\n')
             self.add('incomplete final line')

             self.pop_complete_lines() <-- returns ['first line', 'second line']
             self.pop_incomplete_line() <-- returns 'incomplete final line'

    '''

    def __init__(self):
        self._complete_lines = []
        self.incomplete_line = ''

    def add(self, text):
        assert isinstance(text, str), 'expected str got {}'.format(text.__class__)

        unprocessed_text = self.incomplete_line + text
        complete_lines, incomplete_line = self._split_lines(unprocessed_text)

        self._complete_lines += complete_lines
        self.incomplete_line = incomplete_line

    def pop_complete_lines(self):
        try:
            return self._complete_lines
        finally:
            self._complete_lines = []

    def pop_incomplete_line(self):
        try:
            return self.incomplete_line
        finally:
            self.incomplete_line = ''

    def _split_lines(self, text):
        lines = text.splitlines(True)

        if self._has_incomplete_line(lines):
            complete_lines = lines[:-1]
            incomplete_line = lines[-1]
        else:
            complete_lines = lines
            incomplete_line = ''

        return (complete_lines, incomplete_line)

    def _has_incomplete_line(self, lines):
        return len(lines) and not lines[-1].endswith('\n')


def _make_callable(value):
    if not callable(value):
        return lambda: value
    else:
        return value


class QueueIterator(object):
    ''' 
        Iterates over a queue, until END_OF_INPUT is encountered 
    '''

    def __init__(self, queue):
        self._queue = queue

    def __iter__(self):
        return self

    def __next__(self):
        text = self._queue.get()
        if text is END_OF_INPUT:
            raise StopIteration
        return text
