#!python
from queue import Queue
import unittest

from more_or_less import Action, Output, ActionReader, OutputAborted
import more_or_less


_big_page = 1000


class OutputDummy(Output):

    def __init__(self):
        self.output = []

    def print(self, text):
        self.output.append(text)

    def add_action(self, action):
        self.output.append(action)


class ActionReaderMock(ActionReader):
    '''
        Mock that returns a given action but also tells an observer what it returned
    '''

    def __init__(self, action=Action.print_next_line, observer=None):
        self.action = action
        self.observer = observer

    def get_next(self):
        self.observer.add_action(self.action)
        return self.action


class TestUtil(unittest.TestCase):

    def setUp(self):
        self.output = OutputDummy()

    def paginate(self, input, output=None, action=Action.print_next_page, page_height=_big_page, asynchronous=False):
        # Wrapper around paginate that adds some defaults that are handier for the tests.
        output = output or self.output
        return more_or_less.paginate(
            input=input,
            output=output,
            action_reader=ActionReaderMock(action=action, observer=output),
            page_height=page_height,
            asynchronous=asynchronous,
        )


class TestPaginate(TestUtil):

    def test_input_is_passed_to_output(self):
        self.paginate(['first \n', 'second \n'])

        self.assertEqual(['first \n', 'second \n'], self.output.output)

    def test_can_read_input_from_a_queue(self):
        queue = _make_queue('first \n', 'second \n', more_or_less.END_OF_INPUT)
        self.paginate(queue)

        self.assertEqual(['first \n', 'second \n'], self.output.output)

    def test_action_is_requested_after_a_full_page(self):
        self.paginate(
            ['first \n', 'second \n', 'third \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.print_next_page,
                'third \n'
            ],
            self.output.output)

    def test_action_is_requested_after_a_second_full_page(self):
        self.paginate(
            ['first \n', 'second \n', 'third \n', 'fourth \n', 'fifth \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.print_next_page,
                'third \n',
                'fourth \n',
                Action.print_next_page,
                'fifth \n',
            ],
            self.output.output)

    def test__action_reader_returns_print_next_line__prompts_after_one_more_line(self):
        self.paginate(
            ['first \n', 'second \n', 'third \n', 'fourth \n'],
            page_height=2,
            action=Action.print_next_line,
        )

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.print_next_line,
                'third \n',
                Action.print_next_line,
                'fourth \n',
            ],
            self.output.output)

    def test__run_asynchronous__returns_controller_that_can_be_joined(self):
        input_queue = Queue()
        controller = self.paginate(
            input_queue,
            page_height=2,
            asynchronous=True,
        )

        input_queue.put('first \n')
        input_queue.put(more_or_less.END_OF_INPUT)

        controller.join(timeout=1)

        self.assertEqual(
            [
                'first \n',
            ],
            self.output.output)

    def test__can_not_join_queue_when_input_is_finished(self):
        '''
            Note it might seem harsh to ensure we do NOT do a nice thing like allowing the caller
            to use queue.join().

            However, if the caller were to rely on 'queue.join()',
            and the user aborts the paginating,
            we would be forced to keep draining the input queue until we encounter 'END_OF_INPUT',
            just to ensure the caller's 'join' call doesn't block forever.

            Which is not the behavior people would expect us to have
            (they expect us to stop reading the input as soon as they tell us to abort,
            and they are right to expect this).
        '''
        input_queue = Queue()
        self.paginate(
            input_queue,
            page_height=2,
            asynchronous=True,
        )

        input_queue.put('first \n')
        input_queue.put(more_or_less.END_OF_INPUT)

        self.assertTrue(bool(input_queue.unfinished_tasks))

    def test__single_input_string_can_contain_multiple_lines(self):
        self.paginate(
            input=['first \nsecond \nthird \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.print_next_page,
                'third \n',
            ],
            self.output.output
        )

    def test__combines_incomplete_lines(self):
        self.paginate(
            input=['first \nthis ', 'is ', 'a ', 'single ', 'line \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                'first \n',
                'this is a single line \n',
            ],
            self.output.output
        )

    def test__survives_empty_string(self):
        self.paginate(
            input=['-->', '', '<-- \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                '--><-- \n',
            ],
            self.output.output
        )

    def test__survives_empty_string_as_first_string(self):
        self.paginate(
            input=['', '<-- \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                '<-- \n',
            ],
            self.output.output
        )

    def test__flushes_final_incomplete_line(self):
        self.paginate(
            input=['this line is incomplete '],
            page_height=2,
        )

        self.assertEqual(
            [
                'this line is incomplete ',
            ],
            self.output.output
        )

    def test__queue_flushes_final_incomplete_line(self):
        input_queue = Queue()
        context = self.paginate(
            input_queue,
            page_height=2,
            asynchronous=True,
        )

        input_queue.put('this line is incomplete ')
        input_queue.put(more_or_less.END_OF_INPUT)

        context.join(timeout=1)

        self.assertEqual(
            [
                'this line is incomplete ',
            ],
            self.output.output
        )

    def test_page_height_can_be_a_callable(self):
        page_height = 2

        def get_page_height():
            return page_height

        input_queue = Queue()
        context = self.paginate(
            input_queue,
            page_height=get_page_height,
            asynchronous=True,
        )

        input_queue.put('first \n')
        input_queue.put('second \n')
        input_queue.put('third \n')  # This call will prompt the more prompt

        page_height = 1
        input_queue.put('fourth \n')  # This call will prompt the more prompt again
        input_queue.put(more_or_less.END_OF_INPUT)

        context.join(timeout=1)

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.print_next_page,
                'third \n',
                Action.print_next_page,
                'fourth \n',
            ],
            self.output.output
        )

    def test_raises_output_aborted_exception_on_abort(self):
        with self.assertRaises(OutputAborted):
            self.paginate(
                ['first \n', 'second \n', 'after the abort message \n'],
                page_height=2,
                action=Action.abort,
            )

        self.assertEqual(
            [
                'first \n',
                'second \n',
                Action.abort,
            ],
            self.output.output
        )


def _make_queue(*args):
    queue = Queue()
    for item in args:
        queue.put(item)
    return queue
