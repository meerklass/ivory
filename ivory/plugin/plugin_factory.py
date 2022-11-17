import importlib
from typing import Optional

from ivory.exceptions.exceptions import UnsupportedPluginTypeException
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.config_section import ConfigSection
from ivory.utils.struct import Struct


class PluginFactory:
    """
    Simple factory creating instances of plugins
    """

    # TODO(amadeus) this should hand over the config parameters directly to the plugins
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
        Returns the `class` in `module` that ends with 'Plugin' and is not 'AbstractPlugin.
        :raise ValueError: if more than one valid `class` is found
        """
        result = None
        already_found = False
        for attribute in dir(module):
            if attribute.endswith('Plugin') and not attribute.startswith('Abstract') and not attribute.startswith('_'):
                attribute = getattr(module, attribute)
                if isinstance(attribute, ConfigSection):
                    continue
                if already_found:
                    raise ValueError(f'Input `module` {module} contains more than one valid `Plugin`.')
                result = attribute
                already_found = True
        return result
