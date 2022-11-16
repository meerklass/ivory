from abc import ABC, abstractmethod

from ivory import context
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result
from ivory.utils.struct import Struct


class AbstractPlugin(ABC):
    """
    Abstract base class for all plugins.
    The config for a plugin is made accessible via `self.config
    The input arguments of the `run` method need to be defined in `cls.requirements`.
    """

    requirements: list[Requirement] = []

    def __init__(self, ctx: Struct | None = None):
        """
        Initializes with context `ctx` and kwargs.
        The config of the `plugin` is made accessible via `self.config`.
        """
        if ctx is None:
            ctx = Struct()
        self.config = context.create_immutable_ctx()
        self.set_config(ctx)
        self.results: list[Result] = []
        self.set_requirements()

    def __str__(self):
        return self.name

    def set_config(self, ctx: Struct):
        """ Sets the config of `self` if it is present in `ctx`. """
        if 'params' in ctx:
            if self.name in ctx.params:
                self.config = ctx.params[self.name]

    @abstractmethod
    def run(self, **kwargs):
        """ Runs the plugin and store results. """
        pass

    @abstractmethod
    def set_requirements(self):
        """ Set the requirements of `self`, i.e. the arguments of `self.run()`. """
        self.requirements = []

    @classmethod
    @property
    def name(self):
        return self.__name__

    def set_result(self, result: Result):
        """ Appends `result` to `self.result`. """
        self.results.append(result)
