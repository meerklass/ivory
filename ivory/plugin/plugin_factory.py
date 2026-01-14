import importlib
from types import ModuleType

from ivory.config_keys import ConfigKeys
from ivory.exceptions.exceptions import UnsupportedPluginTypeException
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.config_section import ConfigSection
from ivory.utils.struct import Struct


class PluginFactory:
    """
    Simple factory creating instances of plugins
    """

    @staticmethod
    def create_instance(plugin_name: str, ctx: Struct) -> AbstractPlugin | None:
        """
        Instantiates the given plugin from its module string (like a python import).
        Expects that this module contains exactly one class with name starting on a capital letter and ending on
        'Plugin', 'AbstractPlugin' is excluded.
        :param plugin_name: name of module containing plugin
        :param ctx: context
        :raises: UnsupportedPluginTypeException
        :return: an instance of the plugin
        """
        try:
            module = importlib.import_module(plugin_name)
        except ImportError as ex:
            raise UnsupportedPluginTypeException(f"Module '{plugin_name}' could not be loaded", ex)
        except AttributeError:
            raise UnsupportedPluginTypeException(f"Module '{plugin_name}' has no class definition 'Plugin(ctx)'")
        except Exception as ex:
            raise UnsupportedPluginTypeException(f"Module '{plugin_name}' could not be instantiated'", ex)
        plugin = PluginFactory._get_plugin_attribute(module)
        if ConfigKeys.PARAMS.value in ctx and plugin.name in ctx.params:
            config = ctx.params[plugin.name]
        else:
            config = {}
        if plugin is not None:
            return plugin(**config)

    @staticmethod
    def _get_plugin_attribute(module: ModuleType) -> type[AbstractPlugin]:
        """
        Returns the `class` in `module` that ends with 'Plugin' and is not 'AbstractPlugin.
        :raise ValueError: if more than one valid `class` is found
        :raise ValueError: if no valid `class` is found
        """
        result = None
        already_found = False
        for attribute in dir(module):
            if attribute.endswith("Plugin") and not attribute.startswith("Abstract") and not attribute.startswith("_"):
                attribute = getattr(module, attribute)
                if isinstance(attribute, ConfigSection):
                    continue
                if already_found:
                    raise ValueError(f"Input `module` {module} contains more than one valid `Plugin`.")
                result = attribute
                already_found = True
        if result is None:
            raise ValueError(f"No valid plugin found in {module}. Typo? Does the class name end on `Plugin`?")
        return result
