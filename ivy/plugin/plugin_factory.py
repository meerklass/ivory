import importlib
from typing import Optional

from ivy.exceptions.exceptions import UnsupportedPluginTypeException
from ivy.plugin.abstract_plugin import AbstractPlugin
from ivy.utils.struct import Struct


class PluginFactory:
    """
    Simple factory creating instances of plugins
    """

    @staticmethod
    def create_instance(plugin_name: str, ctx: Struct) -> Optional[AbstractPlugin]:
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
            raise UnsupportedPluginTypeException("Module '%s' could not be loaded" % plugin_name, ex)
        except AttributeError as ex:
            raise UnsupportedPluginTypeException("Module '%s' has no class definition 'Plugin(ctx)'" % plugin_name)
        except Exception as ex:
            raise UnsupportedPluginTypeException("Module '%s' could not be instantiated'" % plugin_name, ex)
        plugin = PluginFactory._get_plugin_attribute(module)
        if plugin is not None:
            return plugin(ctx)

    @staticmethod
    def _get_plugin_attribute(module) -> Optional[type[AbstractPlugin]]:
        """
        Returns the first occuring (alphabetically) `class` in `module`
        that ends with 'Plugin' and is not 'AbstractPlugin.
        """
        for attribute in dir(module):
            if attribute.endswith('Plugin') and not attribute.startswith('Abstract') and not attribute.startswith('_'):
                return getattr(module, attribute)
