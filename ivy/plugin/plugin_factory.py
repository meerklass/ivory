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

from ivy.exceptions.exceptions import UnsupportedPluginTypeException


class PluginFactory:
    """
    Simple factory creating instances of plugins
    """

    @staticmethod
    def createInstance(plugin_name, ctx):
        """
        Instantiates the given plugin. Expects that the given module contains a class
        
        with the name 'Plugin'
        
        :param plugin_name: name of the plugin to instanciate
        
        :return plugin: an instance of the plugin
        
        :raises: UnsupportedPluginTypeException
        """
        try:
            module = importlib.import_module(plugin_name)
            plugin = module.Plugin(ctx)
            return plugin
        except ImportError as ex:
            raise UnsupportedPluginTypeException("Module '%s' could not be loaded" % plugin_name, ex)
        except AttributeError as ex:
            raise UnsupportedPluginTypeException("Module '%s' has no class definition 'Plugin(ctx)'" % plugin_name)
        except Exception as ex:
            raise UnsupportedPluginTypeException("Module '%s' could not be instantiated'" % plugin_name, ex)
