from more_or_less.input import Input
from more_or_less.more_page_builder import MorePageBuilder
from textwrap import dedent
from unittest.mock import Mock
import unittest


class TestHelpPlugin(unittest.TestCase):
    expected_help = dedent('''\

        -------------------------------------------------------------------------------
        Most commands can optionally be preceded by an integer argument k.
        The default values are printed in brackets.
        A star (*) indicates the value of k becomes the new default.
        -------------------------------------------------------------------------------
        <space>                Display next k lines of text [current screen size]
        <return>               Display next k lines of text [1]*
        q or Q or <interrupt>  Exit from more
        /<regular expression>  Search for kth occurrence of the regular expression [1]
        n                      Search for kth occurrence of the last regular expression [1]
        h or ?                 Display this help text
        -------------------------------------------------------------------------------
    ''')

    def setUp(self):
        self.output = OutputMock()
        self.input = Mock(Input)
        self.maxDiff = None

    def get_more_page_builder(self):
        return MorePageBuilder(input=self.input, output=self.output)

    def test_prints_help_on_h(self):
        builder = self.get_more_page_builder()

        self.input.get_character.side_effect = ['h', ' ']
        builder.build_next_page()

        self.assertEqual(self.expected_help, self.output.text)

    def test_prints_help_on_question_mark(self):
        builder = self.get_more_page_builder()

        self.input.get_character.side_effect = ['?', ' ']
        builder.build_next_page()

        self.assertEqual(self.expected_help, self.output.text)

    def test_prompts_for_next_page_after_printing_help(self):
        builder = self.get_more_page_builder()

        self.input.get_character.side_effect = ['?', ' ']
        builder.build_next_page()

        self.assertEqual(2, self.input.get_character.call_count)


class OutputMock(object):

    def __init__(self):
        self.lines = []

    def write(self, text):
        self.lines.append(text)

    @property
    def text(self):
        return ''.join(self.lines)
