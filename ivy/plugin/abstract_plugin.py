from abc import ABC, abstractmethod
from typing import Any, Type

from ivy import context
from ivy.utils.struct import Struct, ImmutableStruct


class AbstractPlugin(ABC):
    """
    Abstract base class for all plugins.
    The config for a plugin is made accessible via `self.config
    """

    def __init__(self, ctx: Struct, **kwargs: dict[str, Any]):
        """
        Initialize with context `ctx` and kwargs.
        The config of the `plugin` is made accessible via `self.config`.
        """
        self.ctx = ctx
        self.ctx.update(kwargs)

        self.config = context.create_immutable_ctx()
        self.set_config()

    def __str__(self):
        return self.name

    def set_config(self):
        """ Set the config of `self` if it is present. """
        if 'params' in self.ctx:
            if self.name in self.ctx.params:
                self.config = self.ctx.params[self.name]

    @abstractmethod
    def run(self):
        """ Run the plugin and store results. """
        pass

    @classmethod
    @property
    def name(self):
        return self.__name__

    def output_of_plugin(self, plugin: Type['AbstractPlugin']) -> ImmutableStruct:
        """ Returns the output of a `plugin`. """
        if plugin.name in self.ctx:
            return self.ctx[plugin.name]
        return context.create_immutable_ctx()

    def save_to_context(self, result_dict: dict):
        """ Save `result_dict` to `self.ctx` for following `plugin`s to access. """
        self.ctx[self.name] = context.create_immutable_ctx(**result_dict)
