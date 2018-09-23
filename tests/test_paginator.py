#!python
from more_or_less import OutputAborted, PageBuilder, PageOfHeight
from queue import Queue
import more_or_less
import unittest


_big_page = 1000


class TestUtil(unittest.TestCase):

    def setUp(self):
        self._page_builder = None

    def paginate(self, input, page_builder=None, page_height=_big_page, asynchronous=False):
        self._page_builder = page_builder or PageBuilderMock(page_height)

        return more_or_less.paginate(
            input=input,
            page_builder=self._page_builder,
            asynchronous=asynchronous,
        )

    @property
    def output(self):
        return self._page_builder.pages


class TestPaginate(TestUtil):

    def test_input_is_passed_to_first_page(self):
        self.paginate(['first \n', 'second \n'])

        self.assertEqual(
            [
                FirstPage(['first \n', 'second \n', ])
            ],
            self.output
        )

    def test_can_read_input_from_a_queue(self):
        queue = _make_queue('first \n', 'second \n', more_or_less.END_OF_INPUT)
        self.paginate(queue)

        self.assertEqual(
            [
                FirstPage(['first \n', 'second \n', ])
            ],
            self.output
        )

    def test_starts_new_page_if_first_is_full(self):
        self.paginate(
            ['first \n', 'second \n', 'third \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                FirstPage(['first \n', 'second \n', ]),
                NextPage(['third \n']),
            ],
            self.output
        )

    def test_starts_new_page_if_second_is_full(self):
        self.paginate(
            ['first \n', 'second \n', 'third \n', 'fourth \n', 'fifth \n'],
            page_height=2,
        )

        self.assertEqual(
            [
                FirstPage(['first \n', 'second \n', ]),
                NextPage(['third \n', 'fourth \n', ]),
                NextPage(['fifth \n']),
            ],
            self.output
        )

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
                FirstPage(['first \n']),
            ],
            self.output
        )

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
                FirstPage(['first \n', 'second \n']),
                NextPage(['third \n']),
            ],
            self.output
        )

    def test__combines_incomplete_lines(self):
        self.paginate(
            input=['first \nthis ', 'is ', 'a ', 'single ', 'line \n'],
            page_height=2,
        )
        self.assertEqual(
            [
                FirstPage(['first \n', 'this is a single line \n', ]),
            ],
            self.output
        )

    def test__survives_empty_string(self):
        self.paginate(
            input=['-->', '', '<-- \n'],
            page_height=2,
        )
        self.assertEqual(
            [
                FirstPage(['--><-- \n']),
            ],
            self.output
        )

    def test__survives_empty_string_as_first_string(self):
        self.paginate(
            input=['', '<-- \n'],
            page_height=2,
        )
        self.assertEqual(
            [
                FirstPage(['<-- \n']),
            ],
            self.output
        )

    def test__flushes_final_incomplete_line(self):
        self.paginate(
            input=['this line is incomplete '],
            page_height=2,
        )
        self.assertEqual(
            [
                FirstPage(['this line is incomplete ']),
            ],
            self.output
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
                FirstPage(['this line is incomplete ']),
            ],
            self.output
        )

    def test_raises_output_aborted_exception_on_abort(self):

        class AbortingPageBuilder(PageBuilderMock):

            def build_next_page(self):
                raise OutputAborted()

        with self.assertRaises(OutputAborted):
            self.paginate(
                ['first \n', 'second \n', 'after the abort message \n'],
                page_builder=AbortingPageBuilder(page_height=2),
            )


def _make_queue(*args):
    queue = Queue()
    for item in args:
        queue.put(item)
    return queue


class PageTester(object):

    def __eq__(self, other_page):
        return (self.name == other_page.name) and (other_page.lines == self.lines)

    def __repr__(self):
        return '{}Page({})'.format(self.name, self.lines)


class PageMock(PageOfHeight, PageTester):

    def __init__(self, name, page_height=None):
        self.lines = []
        self.name = name
        super().__init__(height=page_height, output=self._ListOutput(self.lines))

    class _ListOutput(object):
        def __init__(self, output_list):
            self.lines = output_list

        def write(self, text):
            self.lines.append(text)


class FirstPage(PageTester):

    def __init__(self, lines):
        self.lines = lines
        self.name = 'First'


class NextPage(PageTester):

    def __init__(self, lines):
        self.lines = lines
        self.name = 'Next'


class PageBuilderMock(PageBuilder):

    def __init__(self, page_height):
        self.pages = []
        self._page_height = page_height

    def build_first_page(self):
        return self._build_page('First')

    def build_next_page(self):
        return self._build_page('Next')

    def _build_page(self, name):
        page = PageMock(name=name, page_height=self._page_height)
        self.pages.append(page)
        return page
