import sys

from more_or_less.screen_dimensions import ScreenDimensions


_HUGE = sys.maxsize


class FixedSizeScreen(ScreenDimensions):

    def __init__(self, height=_HUGE, width=_HUGE):
        self._height = height
        self._width = width

    def get_height(self):
        return self._height

    def get_width(self):
        return self._width
