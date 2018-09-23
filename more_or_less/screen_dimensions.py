from abc import ABC, abstractmethod


class ScreenDimensions(ABC):

    @abstractmethod
    def get_height(self):
        pass

    @abstractmethod
    def get_width(self):
        pass
