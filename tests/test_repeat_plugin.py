from more_or_less import more_plugins
from more_or_less.input import Input
from more_or_less.more_plugin import MorePlugin
from more_or_less.output import Output
from more_or_less.page import Page
from more_or_less.search_plugin import SearchPage
from tests.test_more_page_builder import TestUtil
from unittest.mock import Mock, call

_UNREPEATABLE_PAGE_KEY = 'U'


class TestRepeatPlugin(TestUtil):

    def setUp(self):
        self.input = Mock(Input)
        self.output = Mock(Output)
        plugins = more_plugins.get() + [UnrepeatablePagePlugin()]
        self.builder = self.get_more_page_builder(
            input=self.input,
            output=self.output,
            plugins=plugins)

    def fill_page(self, page):
        while not page.is_full():
            page.add_line('line \n')

    def test_can_repeat_enter(self):
        self.input.get_character.side_effect = ['5', '\n']
        page = self.builder.build_next_page()
        self.fill_page(page)

        self.input.get_character.side_effect = ['.']

        repeated_page = self.builder.build_next_page()

        self.assertIsPageOfHeight(repeated_page, 5)
        self.assertFalse(repeated_page.is_full())

    def test_can_repeat_space(self):
        self.input.get_character.side_effect = [' ']
        page = self.builder.build_next_page()
        self.fill_page(page)

        self.input.get_character.side_effect = ['.']

        repeated_page = self.builder.build_next_page()

        self.assertIsPageOfHeight(repeated_page, page.height)

    def test_can_repeat_search(self):
        self.input.get_character.side_effect = ['5', '/']
        self.input.prompt.return_value = 'the pattern'

        self.builder.build_next_page()

        self.input.get_character.side_effect = ['.']

        repeated_page = self.builder.build_next_page()

        self.assertIsPageOfType(repeated_page, SearchPage)
        self.assertEqual('the pattern', repeated_page.pattern)
        self.assertEqual(5, repeated_page.required_match_count)

    def test_prints_warning_on_unrepeatable_command(self):
        self.input.get_character.side_effect = [_UNREPEATABLE_PAGE_KEY]
        self.builder.build_next_page()

        self.input.get_character.side_effect = ['.', ' ', ' ']

        self.builder.build_next_page()
        self.input.assert_has_calls([
            call.get_character('--More--'),
            call.get_character('--Previous command can not be repeated--'),
        ])


class UnrepeatablePage(Page):

    def is_full(self):
        return False

    def add_line(self, line):
        pass


class UnrepeatablePagePlugin(MorePlugin):
    '''
        Plugin that returns a page of type 'DefaultPage'
    '''
    @property
    def keys(self):
        return [_UNREPEATABLE_PAGE_KEY]

    def build_page(self, page_builder, key_pressed, arguments):
        return UnrepeatablePage()

    def get_help(self):
        pass
