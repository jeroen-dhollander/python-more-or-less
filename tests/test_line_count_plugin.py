from more_or_less.input import Input
from more_or_less.output import Output
from tests.test_more_page_builder import TestUtil
from unittest.mock import Mock, call


class TestLineCountPlugin(TestUtil):

    def setUp(self):
        self.input = Mock(Input)
        self.output = Mock(Output)
        self.builder = self.get_more_page_builder(input=self.input, output=self.output)

    def print_n_lines(self, n):
        page = self.builder.build_first_page()
        for i in range(0, n):
            page.add_line(f'line {i}\n')

    def test_prints_line_number_when_user_types_equal(self):
        self.print_n_lines(10)

        self.input.get_character.side_effect = ['=', ' ']
        self.builder.build_next_page()
        self.input.get_character.assert_has_calls([
            call('--More--'),
            call('--10--'),
        ])

    def test_returns_next_page_after_printing_line_number(self):
        self.print_n_lines(10)

        self.input.get_character.side_effect = ['=', ' ']
        page = self.builder.build_next_page()

        self.assertIsFullscreenPage(page)

    def test_prints_line_numbers_after_pressing_l(self):
        first_page = self.builder.build_first_page()
        first_page.add_line('before enabling line-numbers\n')

        self.input.get_character.side_effect = ['l', ' ']
        page = self.builder.build_next_page()

        page.add_line('after enabling line-numbers\n')

        self.output.assert_has_calls([
            call.write('before enabling line-numbers\n'),
            call.write('2: after enabling line-numbers\n'),
        ])

    def test_stops_printing_line_numbers_after_pressing_l_again(self):
        first_page = self.builder.build_first_page()
        first_page.add_line('before enabling line-numbers\n')

        self.input.get_character.side_effect = ['l', ' ']
        page = self.builder.build_next_page()

        page.add_line('after enabling line-numbers\n')

        self.input.get_character.side_effect = ['l', ' ']
        page = self.builder.build_next_page()

        page.add_line('after disabling line-numbers\n')

        self.output.assert_has_calls([
            call.write('before enabling line-numbers\n'),
            call.write('2: after enabling line-numbers\n'),
            call.write('after disabling line-numbers\n'),
        ])

    def test_prints_status_in_prompt_when_enabling_or_disabling_line_numbers(self):
        self.input.get_character.side_effect = ['l', 'l', ' ']
        self.builder.build_next_page()

        self.input.assert_has_calls([
            call.get_character('--Line numbers are now enabled--'),
            call.get_character('--Line numbers are now disabled--'),
        ])
