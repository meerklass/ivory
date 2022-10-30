# IVY is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# IVY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with IVY.  If not, see <http://www.gnu.org/licenses/>.


"""
Created on Mar 5, 2014

author: jakeret
"""

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
