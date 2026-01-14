from enum import Enum
from typing import Any

from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.result import Result


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
        if self.value == "store":
            self.set_result(result=Result(location=SimpleEnum.simple, result=1))
            self.store_context_to_disc(context_directory="cache/", context_file_name="simple_plugin.pickle")

    def set_requirements(self):
        pass


class SimpleEnum(Enum):
    simple = "simple"
