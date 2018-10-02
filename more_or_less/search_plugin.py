from .more_plugin import MorePlugin
from .page import Page
from .page_of_height import PageOfHeight
from .repeatable_mixin import RepeatableMixin
import re

_NO_PREVIOUS_REGULAR_EXPRESSION = '--No previous regular expression--'
_SKIPPING_MESSAGE = '...skipping\n'


class SearchPlugin(MorePlugin):
    ''' 
        Skips all output until a certain search pattern is found.
        Invoked when the user types '/'.
        The search can be repeated by pressing 'n'
    '''

    def __init__(self):
        self._pattern = None
        self._match_count = None

    def get_keys(self):
        return ['/', 'n']

    def build_page(self, page_builder, key_pressed, arguments):
        self._match_count = arguments.get('count', 1)

        if key_pressed == '/':
            return self._do_new_search(page_builder)
        elif key_pressed == 'n':
            return self._repeat_last_search(page_builder)
        else:
            assert False, 'Unexpected input key'

    def get_help(self):
        yield ('/<regular expression>', 'Search for kth occurrence of the regular expression [1]')
        yield ('n', 'Search for kth occurrence of the last regular expression [1]')

    def _do_new_search(self, page_builder):
        self._update_pattern(page_builder.get_input())
        return self._create_search_page(page_builder)

    def _repeat_last_search(self, page_builder):
        if self._pattern is None:
            return page_builder.build_next_page(message=_NO_PREVIOUS_REGULAR_EXPRESSION)
        else:
            return self._create_search_page(page_builder)

    def _create_search_page(self, page_builder):
        page_builder.get_output().write(_SKIPPING_MESSAGE)
        return SearchPage(
            pattern=self._pattern,
            next_page=self._create_full_page(page_builder),
            match_count=self._match_count,
        )

    def _create_full_page(self, page_builder):
        return PageOfHeight(
            height=page_builder.get_page_height(),
            output=page_builder.get_output())

    def _update_pattern(self, input):
        self._pattern = input.prompt('/')


class SearchPage(Page, RepeatableMixin):
    '''
        A page that suppresses all output until a given search pattern is found.
        After that it displays the passed in page
    '''

    def __init__(self, pattern, next_page, match_count):
        self.pattern = pattern
        self.next_page = next_page
        self._matcher = re.compile(pattern)
        self._actual_match_count = 0
        self.required_match_count = match_count

    def is_full(self):
        if self.has_match:
            return self.next_page.is_full()
        return False

    def add_line(self, line):
        self._match(line)

        if self.has_match:
            self.next_page.add_line(line)

    def _match(self, line):
        if self._matcher.search(line):
            self._actual_match_count = self._actual_match_count + 1

    def flush(self):
        if self.has_match:
            self.next_page.flush()

    def repeat(self):
        return SearchPage(self.pattern, self.next_page.repeat(), self.required_match_count)

    @property
    def has_match(self):
        return self._actual_match_count >= self.required_match_count
