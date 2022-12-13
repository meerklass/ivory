from typing import Any

from ivory.plugin.abstract_plugin import AbstractPlugin


class SimplePlugin(AbstractPlugin):
    """
    Simple implementation of the AbstractPlugin
    """
    def __init__(self, value: Any = None):
        super().__init__()
        self.value = value

    def run(self):
        if self.value is not None:
            print(self.value)

    def set_requirements(self):
        pass
