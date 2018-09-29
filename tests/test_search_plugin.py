from more_or_less.input import Input
from more_or_less.output import Output
from more_or_less.page import Page
from more_or_less.search_plugin import SearchPage
from tests.test_more_page_builder import TestUtil
from unittest.mock import Mock, call
import unittest


class TestSearchPlugin(TestUtil):

    def assertIsSearchPageWithPattern(self, page, pattern):
        self.assertIsPageOfType(page, SearchPage)
        self.assertEqual(pattern, page.pattern)

    def assertIsSearchPageWithMatchCount(self, page, match_count):
        self.assertIsPageOfType(page, SearchPage)
        self.assertEqual(match_count, page.required_match_count)

    def test_creates_search_page_when_pressing_slash(self):
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.return_value = ''
        builder = self.get_more_page_builder(input=input)

        page = builder.build_next_page()

        self.assertIsSearchPageWithPattern(page, pattern='')

    def test_passes_search_pattern_to_search_page(self):
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.return_value = 'the-pattern'
        builder = self.get_more_page_builder(input=input)

        page = builder.build_next_page()

        self.assertIsSearchPageWithPattern(page, pattern='the-pattern')

    def test_n_repeats_previous_search(self):
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input)

        builder.build_next_page()

        input.get_character.return_value = 'n'
        second_page = builder.build_next_page()

        self.assertIsSearchPageWithPattern(second_page, pattern='the-pattern')

    def test_n_without_previous_search_prints_error_in_prompt(self):
        input = Mock(Input)
        input.get_character.side_effect = ['n', ' ']
        builder = self.get_more_page_builder(input=input)

        builder.build_next_page()

        input.get_character.assert_has_calls([
            call('--More--'),
            call('--No previous regular expression--'),
        ])

    def test_prints_skipping_text_to_output(self):
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.side_effect = ['the-pattern']
        output = Mock(Output)
        builder = self.get_more_page_builder(input=input, output=output)

        builder.build_next_page()
        output.write.assert_called_once_with('...skipping\n')

    def test_passes_full_page_to_search_page(self):
        screen_height = 100
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input, screen_height=screen_height)

        page = builder.build_next_page()

        self.assertIsFullscreenPage(page.next_page, screen_height=screen_height)

    def test_passes_count_1_to_search_page_by_default(self):
        input = Mock(Input)
        input.get_character.return_value = '/'
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input)

        page = builder.build_next_page()
        self.assertIsSearchPageWithMatchCount(page, match_count=1)

    def test_passes_count_to_search_page(self):
        input = Mock(Input)
        input.get_character.side_effect = ['5', '/']
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input)

        page = builder.build_next_page()
        self.assertIsSearchPageWithMatchCount(page, match_count=5)

    def test_n_defaults_to_match_count_1(self):
        input = Mock(Input)
        input.get_character.side_effect = ['5', '/']
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input)
        builder.build_next_page()

        input.get_character.side_effect = ['n']
        second_page = builder.build_next_page()

        self.assertIsSearchPageWithMatchCount(second_page, match_count=1)

    def test_n_accepts_a_count(self):
        input = Mock(Input)
        input.get_character.side_effect = ['/']
        input.prompt.side_effect = ['the-pattern']
        builder = self.get_more_page_builder(input=input)
        builder.build_next_page()

        input.get_character.side_effect = ['7', 'n']
        second_page = builder.build_next_page()

        self.assertIsSearchPageWithMatchCount(second_page, match_count=7)


class TestSearchPage(unittest.TestCase):

    def setUp(self):
        self.next_page = Mock(Page)

    def create_search_page(self, pattern='', match_count=1):
        return SearchPage(pattern=pattern, next_page=self.next_page, match_count=match_count)

    def test_add_line_blackholed_if_it_doesnt_match(self):
        page = self.create_search_page('the-pattern')
        page.add_line('this does not match the pattern')
        self.next_page.add_line.assert_not_called()

    def test_add_line_forwarded_if_it_matches_the_pattern(self):
        page = self.create_search_page('the.*pattern')
        page.add_line('this matches the regex pattern')
        self.next_page.add_line.assert_called_once_with('this matches the regex pattern')

    def test_add_line_forwarded_if_previous_line_matched_the_pattern(self):
        page = self.create_search_page('the.*pattern')
        page.add_line('this matches the regex pattern')
        page.add_line('next line')
        self.next_page.add_line.assert_has_calls([
            call('this matches the regex pattern'),
            call('next line'),
        ])

    def test_must_match_the_provided_number_of_times(self):
        match_count = 5
        page = self.create_search_page('the.*pattern', match_count=match_count - 1)

        page.add_line('this matches the regex pattern the 1th time')
        page.add_line('this matches the regex pattern the 2nd time')
        page.add_line('this matches the regex pattern the 3rd time')
        page.add_line('this matches the regex pattern the 4th time')
        page.add_line('this matches the regex pattern the 5th time')
        self.next_page.add_line.assert_has_calls([
            call('this matches the regex pattern the 5th time'),
        ])

    def test_is_full_false_initially(self):
        page = self.create_search_page()
        self.assertFalse(page.is_full())

    def test_is_full_does_not_contact_next_page_if_pattern_is_not_matched(self):
        page = self.create_search_page()
        page.is_full()
        self.next_page.is_full.assert_not_called()

    def test_is_full_forwarded_to_next_page_after_pattern_has_been_matched(self):
        page = self.create_search_page('the.*pattern')
        page.add_line('this matches the regex pattern')

        page.is_full()
        self.next_page.is_full.assert_called_once()

    def test_flush_not_forwarded_if_pattern_is_not_matched(self):
        page = self.create_search_page()

        page.flush()
        self.next_page.flush.assert_not_called()

    def test_flush_forwarded_to_next_page_after_pattern_has_been_matched(self):
        page = self.create_search_page('the.*pattern')
        page.add_line('this matches the regex pattern')

        page.flush()
        self.next_page.flush.assert_called_once()
