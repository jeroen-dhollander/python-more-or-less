from .test_more_page_builder import TestUtil
from more_or_less.count_plugin import CountPlugin
from more_or_less.input import Input
from more_or_less.more_plugin import MorePlugin
from more_or_less.one_page_plugin import OnePagePlugin
from more_or_less.page import Page
from unittest.mock import Mock


class TestPageWrapper(TestUtil):

    def assertIsWrappingPage(self, page, wrapped_page=None):
        self.assertIsInstance(page, WrappingPage)
        if wrapped_page:
            self.assertIsInstance(page.wrapped_page, wrapped_page)

    def test_wraps_pages_created_in_build_first_page(self):
        plugins = [WrappingPlugin()]
        builder = self.get_more_page_builder(plugins=plugins)

        page = builder.build_first_page()

        self.assertIsWrappingPage(page)

    def test_wraps_pages_created_in_build_next_page(self):
        plugins = [WrappingPlugin(), DefaultPlugin()]
        input = Mock(Input)
        builder = self.get_more_page_builder(plugins=plugins, input=input)

        input.get_character.return_value = 'D'
        page = builder.build_next_page()

        self.assertIsWrappingPage(page, wrapped_page=DefaultPage)

    def test_only_wraps_the_outer_page_not_nested_pages(self):
        plugins = [WrappingPlugin(), DefaultPlugin(), NestedBuilderPlugin()]
        input = Mock(Input)
        builder = self.get_more_page_builder(plugins=plugins, input=input)

        input.get_character.side_effect = ['N', 'D']
        page = builder.build_next_page()

        self.assertIsWrappingPage(page, wrapped_page=DefaultPage)


class WrappingPage(Page):

    def __init__(self, page):
        self.wrapped_page = page

    def is_full(self):
        return False

    def add_line(self, line):
        pass


class WrappingPlugin(MorePlugin):
    '''
        Plugin that wraps pages with a WrappingPage
    '''

    @property
    def keys(self):
        return []

    def build_page(self, page_builder, key_pressed, arguments):
        assert False

    def wrap_page(self, page):
        return WrappingPage(page)

    def get_help(self):
        pass


class DefaultPage(Page):

    def is_full(self):
        return False

    def add_line(self, line):
        pass


class DefaultPlugin(MorePlugin):
    '''
        Plugin that returns a page of type 'DefaultPage'
    '''
    @property
    def keys(self):
        return ['D']

    def build_page(self, page_builder, key_pressed, arguments):
        return DefaultPage()

    def get_help(self):
        pass


class NestedBuilderPlugin(MorePlugin):
    '''
        Plugin that does a nested call to 'page_builder.build_next_page'
    '''

    @property
    def keys(self):
        return ['N']

    def build_page(self, page_builder, key_pressed, arguments):
        return page_builder.build_next_page()

    def get_help(self):
        pass
