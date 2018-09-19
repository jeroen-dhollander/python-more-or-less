#!python
from abc import ABC, abstractmethod
import enum
import queue
import threading


# Signal to send to the input queue when there is no more input
END_OF_INPUT = None


def paginate(input, output=None, action_reader=None, page_height=None, asynchronous=False):
    '''
        Paginates the input, similar to how 'more' works in bash.

        Input lines is read from 'input',
        and forwarded to 'output' until we hit the 'page_height'.
        At that point, 'action_reader' is contacted to ask how to continue.

        TODO(jeroend) implement the defaults!
        If 'output' is missing, will print to 'stdout'.
        If 'action_reader' is missing, this will display a prompt asking the user for input.
        If 'page_height' is missing, this will use the height of the current terminal window.

        Arguments:
        ----------

        input: 
            The input text that should be paginated.
            This must either be an iterable over text (e.g. a list or a file), or an instance of queue.Queue.

            If it is a queue.Queue, you must pass 'END_OF_INPUT' into the queue when no more input is expected.
            This will flush the final incomplete line (if any) to the output.
            Note that you can NOT use queue.join() to detect all input has been processed
            (as that just raises issues if the user decides to abort the output halfway through).
            Instead, if you use 'asynchronous=True' you can join the returned context.

        output: 
            The object that will receive all the output lines.
            Must follow the API described by the 'Output' object (but must not necessary inherit from this base-class).
            Note that a file can be used as output.

            The paginator will start by sending enough input lines to the output to fill the page.
            After that no lines will be sent until the action_reader tells us to continue.

        page_height: 
            The number of lines that will be sent to 'output' before asking the action_reader what to do next.
            This must either be a number or a callable that returns the height of the current page.

        action_reader: 
            This object is contacted when a page is full to stop the output and ask the user when to continue.
            No more output lines are printed until the action_reader returns the 'Action' to take.

            Must follow the API described by the 'ActionReader' object 
            (but must not necessary inherit from this base-class)

        asynchronous: 
            If true the 'paginate' call will return instantly and run asynchronously.
            In this case a context is returned on which you can call 'context.join([timeout])' 
            to block until all lines are sent to the output.

        Returns:
        --------

        None if asynchronous is False
        A joinable 'context' if asynchronous is True

        Raises:
        -------

        OutputAborted if the action_reader ever returns Action.abort
    '''

    if asynchronous:
        thread = threading.Thread(
            target=paginate,
            kwargs={
                'input': input,
                'output': output,
                'action_reader': action_reader,
                'page_height': page_height,
                'asynchronous': False,
            },
        )
        thread.start()
        return thread

    paginator = Paginator(output, action_reader, page_height)
    if isinstance(input, queue.Queue):
        paginator.paginate_from_queue(input)
    else:
        paginator.paginate(input)


class OutputAborted(Exception):
    '''
        Exception raised when the paginator receives 'Action.abort' from the action-reader.
    '''


class Output(ABC):
    '''
        Example API of what is expected from the 'output' object.
        This does not mean it must inherit from this.

        Note that any 'file' object matches this API,
        so files can natively be used as output.
    '''

    @abstractmethod
    def print(self, text):
        pass


class Action(enum.Enum):
    '''
        Enum indicating what to do when a page is full.
    '''

    print_next_page = enum.auto()
    # print a single line, then ask for the next action
    print_next_line = enum.auto()
    # stop printing any output.
    abort = enum.auto()


class ActionReader(ABC):
    '''
        Example API of what is expected from the 'action_reader' object.
        This does not mean it must inherit from this.

        'get_next' will be called when a page is full,
        and it should return an instance of 'Action' indicating what to do next.
    '''

    @abstractmethod
    def get_next(self):
        pass


class Paginator(object):
    '''
        Paginates given input text, similar to how 'more' works in bash.

        See help of 'paginate' for a more detailed description of output/action_reader and page_height.

        There are 3 ways to send input text:
            - pass an iterable to self.paginate.
            - pass a queue to self.paginate_from_queue.
            - call 'add_text' repeatedly until all text has been sent in, then call 'flush_incomplete_line'.

        In all cases the calls will block until the input has been forwarded to output,
        meaning if the action_reader never returns these calls will block forever.
    '''

    def __init__(self, output, action_reader, page_height):
        self._output = output
        self._action_reader = action_reader
        self._get_page_height = _make_callable(page_height)
        self._remaining_lines = None
        self._lines = _LineCollector()

        self.start_new_page()

    def paginate(self, iterable):
        '''
            Iterates over the iterable, and paginates all the text it returns
        '''
        for text in iterable:
            self.add_text(text)

        self.flush_incomplete_line()

    def paginate_from_queue(self, input_queue):
        '''
            Iterates over the queue, and paginates all the text it returns.
            Stops paginating when END_OF_INPUT is encountered on the queue.

            Will signal input_queue.task_done() when finished
        '''

        while True:
            text = input_queue.get()
            if text is END_OF_INPUT:
                self.flush_incomplete_line()
                return

            self.add_text(text)

    def add_text(self, input_text):
        '''
            Splits the input_text into lines, and paginates them.
            Can be called multiple times.

            When you're done you must call 'flush_incomplete_line'
            to ensure the last incomplete input line is sent to the output.
        '''
        self._lines.add(input_text)

        for line in self._lines.pop_complete_lines():
            self._paginate_and_print_text(line + '\n')

    def flush_incomplete_line(self):
        if len(self._lines.incomplete_line):
            self._paginate_and_print_text(self._lines.pop_incomplete_line())

    def _paginate_and_print_text(self, text):
        if self._is_page_full():
            self._prompt_for_action()
        self._output_text(text)

    def _is_page_full(self):
        return self._remaining_lines == 0

    def _prompt_for_action(self):
        action = self._action_reader.get_next()

        if action == Action.print_next_line:
            self.start_new_page(page_size=1)
        elif action == Action.print_next_page:
            self.start_new_page()
        elif action == Action.abort:
            raise OutputAborted()
        else:
            assert False, "action_reader should return an instance of 'Action' but got {}".format(action)

    def start_new_page(self, page_size=None):
        self._remaining_lines = page_size or self._get_page_height()

    def _output_text(self, text):
        self._output.print(text)
        self._remaining_lines = self._remaining_lines - 1


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
        lines = text.splitlines()

        if text.endswith('\n'):
            complete_lines = lines
            incomplete_line = ''
        elif lines:
            complete_lines = lines[:-1]
            incomplete_line = lines[-1]
        else:
            complete_lines = []
            incomplete_line = ''

        return (complete_lines, incomplete_line)


def _make_callable(value):
    if not callable(value):
        return lambda: value
    else:
        return value
