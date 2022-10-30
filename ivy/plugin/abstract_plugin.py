from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from ivy import context
from ivy.utils.struct import Struct


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

        self.config = self.ctx.params[self.plugin_name]

    @classmethod
    @property
    def plugin_name(self):
        return self.__name__

    def output_of_plugin(self, plugin: Type['AbstractPlugin']) -> Optional[Struct]:
        """ Returns the output of a `plugin` if it has already run. """
        if plugin.plugin_name in self.ctx:
            return self.ctx[plugin.plugin_name]

    def __str__(self):
        return self.plugin_name

    def save_to_context(self, result_dict: dict):
        """ Save `result_dict` to `self.ctx` for following `plugin`s to access. """
        self.ctx[self.plugin_name] = context.create_immutable_ctx(**result_dict)

    @abstractmethod
    def run(self):
        """ Run the plugin and store results. """
        pass
