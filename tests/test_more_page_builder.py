#!python
from more_or_less import OutputAborted, PageOfHeight
from more_or_less.fixed_size_screen import FixedSizeScreen
from more_or_less.input import Input
from more_or_less.more_page_builder import MorePageBuilder
from unittest.mock import Mock
import unittest


class TestMorePageBuilder(unittest.TestCase):

    def assertIsPageOfHeight(self, page, height):
        self.assertIsInstance(page, PageOfHeight)
        self.assertEqual(height, page.height)

    def assertIsFullscreenPage(self, page, screen_height):
        self.assertIsPageOfHeight(page, _page_height_for_screen(screen_height))

    def get_more_page_builder(self, output=None, input=None, screen_height=1000):
        return MorePageBuilder(
            input=input or Mock(Input),
            output=output or OutputMock(),
            screen_dimensions=FixedSizeScreen(height=screen_height),
        )

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
        with self.assertRaises(OutputAborted):
            builder.build_next_page()

    def test_stops_output_if_user_presses_Q(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.return_value = 'Q'
        with self.assertRaises(OutputAborted):
            builder.build_next_page()

    def test_ignores_unexpected_user_input(self):
        input = Mock(Input)
        builder = self.get_more_page_builder(input=input)

        input.get_character.side_effect = ['a', 'b', 'c', '\r']

        builder.build_next_page()

        self.assertEqual(4, input.get_character.call_count)


class OutputMock(object):

    def __init__(self):
        self.lines = []

    def print(self, text):
        self.lines.append(text)


def _page_height_for_screen(screen_height):
    height_reserved_for_more_prompt = 1
    return screen_height - height_reserved_for_more_prompt
