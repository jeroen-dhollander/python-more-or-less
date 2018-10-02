from .more_plugin import MorePlugin
from textwrap import dedent


class HelpPlugin(MorePlugin):
    '''
        Invoked when the user types 'h' or '?'.
        Prints the help text of all plugins
    '''

    def __init__(self):
        pass

    def get_keys(self):
        return ['h', '?']

    def build_page(self, page_builder, key_pressed, arguments):
        self._print_help(page_builder)
        return page_builder.build_next_page()

    def _print_help(self, page_builder):
        help_text = _HelpFormatter(plugins=page_builder.get_plugins()).format()
        page_builder.get_output().write(help_text)

    def _format_help(self):
        return self._help_format.format(help=self._format_plugin_help())

    def get_help(self):
        yield ('h or ?', 'Display this help text')


class _HelpFormatter(object):

    def __init__(self, plugins):
        self._plugins = plugins
        self._format_string = dedent('''\

            -------------------------------------------------------------------------------
            Most commands can optionally be preceded by an integer argument k.
            The default values are printed in brackets.
            A star (*) indicates the value of k becomes the new default.
            -------------------------------------------------------------------------------
            {}
            -------------------------------------------------------------------------------
        ''')

    def format(self):
        self._command_width = self._calculate_command_width()
        return self._format_string.format('\n'.join(self._iter_commands_help()))

    def _iter_commands_help(self):
        return (
            self._format_help_item(command, help_text)
            for plugin in self._plugins
            for command, help_text in plugin.get_help()
        )

    def _format_help_item(self, command, help_text):
        return '{command: <{width}}  {help_text}'.format(
            command=command,
            width=self._command_width,
            help_text=help_text)

    def _calculate_command_width(self):
        return max(len(command) for command, _ in self._get_help_items())

    def _get_help_items(self):
        for plugin in self._plugins:
            yield from plugin.get_help()
