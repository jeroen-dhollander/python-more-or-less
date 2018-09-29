from .page_builder import PageBuilder


class PageWrapper(PageBuilder):
    '''
        Wrapper around the 'build_[first|next]_page' methods that calls all the plugins.wrap_page
        methods.
    '''

    def __init__(self, actual_page_builder):
        self._actual_page_builder = actual_page_builder

    def build_first_page(self):
        return self._wrap_page(self._actual_page_builder.build_first_page())

    def build_next_page(self):
        return self._wrap_page(self._actual_page_builder.build_next_page())

    def __getattr__(self, name):
        return getattr(self._actual_page_builder, name)

    def _wrap_page(self, page):
        for plugin in self.get_plugins():
            page = plugin.wrap_page(page)
        return page
