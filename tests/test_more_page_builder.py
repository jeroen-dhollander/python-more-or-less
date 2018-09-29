#!python
from more_or_less import PageOfHeight
from more_or_less.fixed_size_screen import FixedSizeScreen
from more_or_less.input import Input
from more_or_less.more_page_builder import MorePageBuilder
from more_or_less.output import Output
from more_or_less.page_builder import StopOutput
from more_or_less.wrapped_page import WrappedPage
from unittest.mock import Mock
import unittest


class TestUtil(unittest.TestCase):

    def assertIsPageOfType(self, page, page_type):
        ''' assertIsInstance, but will first strip page-wrappers '''
        page = _skip_page_wrappers(page)
        self.assertIsInstance(page, page_type)

    def assertIsPageOfHeight(self, page, height):
        self.assertIsPageOfType(page, PageOfHeight)
        self.assertEqual(height, page.height)

    def assertIsFullscreenPage(self, page, screen_height=1000):
        self.assertIsPageOfHeight(page, _page_height_for_screen(screen_height))

    def get_more_page_builder(self, output=None, input=None, plugins=None, screen_height=1000):
        return MorePageBuilder(
            input=input or Mock(Input),
            output=output or Mock(Output),
            screen_dimensions=FixedSizeScreen(height=screen_height),
            plugins=plugins,
        )


class TestMorePageBuilder(TestUtil):

    def test_build_first_page_returns_page_of_screen_height_minus_one(self):
        screen_height = 10
        builder = self.get_more_page_builder(screen_height=screen_height)

        page = builder.build_first_page()

        self.assertIsPageOfHeight(page, screen_height - 1)

    def test_build_next_page_prompts_user_for_action(self):
        input = Mock(Input)
        input.get_character.return_value = ' '
        builder = self.get_more_page_builder(input=input)

        builder.build_next_page()

        input.get_character.assert_called_once_with('--More--')

    def test_returns_full_screen_page_if_user_presses_space(self):
        screen_height = 10
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input, screen_height=10)

        input.get_character.return_value = ' '
        page = builder.build_next_page()

        self.assertIsFullscreenPage(page, screen_height)

    def test_returns_one_line_page_if_user_presses_enter(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.return_value = '\r'
        page = builder.build_next_page()

        self.assertIsPageOfHeight(page, 1)

    def test_enter_works_both_on_newline_and_carriage_return(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.return_value = '\n'
        page = builder.build_next_page()

        self.assertIsPageOfHeight(page, 1)

    def test_stops_output_if_user_presses_q(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.return_value = 'q'
        with self.assertRaises(StopOutput):
            builder.build_next_page()

    def test_stops_output_if_user_presses_Q(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.return_value = 'Q'
        with self.assertRaises(StopOutput):
            builder.build_next_page()

    def test_stops_output_on_ctrl_c(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = KeyboardInterrupt

        with self.assertRaises(StopOutput):
            builder.build_next_page()

    def test_ignores_unexpected_user_input(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['a', 'b', 'c', '\r']

        builder.build_next_page()

        self.assertEqual(4, input.get_character.call_count)

    def test_user_can_enter_count_before_enter(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['5', '\n']
        page = builder.build_next_page()

        self.assertIsPageOfHeight(page, 5)

    def test_count_becomes_the_new_default_for_enter(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['5', '\n']
        builder.build_next_page()

        input.get_character.side_effect = ['\n']
        second_page = builder.build_next_page()

        self.assertIsPageOfHeight(second_page, 5)

    def test_can_specify_count_bigger_than_10(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['5', '0', '0', '\n']
        page = builder.build_next_page()

        self.assertIsPageOfHeight(page, 500)

    def test_user_can_enter_count_before_space(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['5', ' ']
        page = builder.build_next_page()

        self.assertIsPageOfHeight(page, 5)

    def test_count_does_not_become_the_new_default_for_space(self):
        input = Mock(Input)
        screen_height = 666
        builder = self.get_more_page_builder(input=input, screen_height=screen_height)

        input.get_character.side_effect = ['5', ' ']
        builder.build_next_page()

        input.get_character.side_effect = [' ']
        second_page = builder.build_next_page()

        self.assertIsFullscreenPage(second_page, screen_height)


def _page_height_for_screen(screen_height):
    height_reserved_for_more_prompt = 1
    return screen_height - height_reserved_for_more_prompt


def _skip_page_wrappers(page):
    while isinstance(page, WrappedPage):
        page = page.wrapped_page
    return page