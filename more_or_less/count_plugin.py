from .more_plugin import MorePlugin


class CountPlugin(MorePlugin):
    ''' 
        Invoked when the user types any number. 
        Adds a 'count' argument to the next action.
    '''

    def __init__(self):
        self._digits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    @property
    def keys(self):
        return self._digits

    def build_page(self, page_builder, key_pressed, arguments):
        arguments['count'] = self._get_count(page_builder, key_pressed)
        return page_builder.build_next_page(arguments=arguments)

    def get_help(self):
        return []

    def _get_count(self, page_builder, first_key):

        def iter_digits():
            # Read characters as long as the user enters digits
            key_pressed = first_key
            while key_pressed in self._digits:
                yield key_pressed
                key_pressed = input.get_character(prompt_message)
            input.put_back(key_pressed)

        input = page_builder.get_input()
        prompt_message = page_builder.get_prompt_message()

        return int(''.join(iter_digits()))
