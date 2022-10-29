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
Created on Mar 4, 2014

author: jakeret
"""
from typing import List, Optional

from ivy import context
from ivy.context import loop_ctx
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.exceptions.exceptions import UnsupportedPluginTypeException
from ivy.plugin.abstract_plugin import AbstractPlugin
from ivy.plugin.plugin_factory import PluginFactory
from ivy.utils.stop_criteria import SimpleStopCriteria, AbstractStopCriteria
from ivy.utils.struct import WorkflowState, Struct


class Loop:
    """
    Implementation of a loop. 
    
    :param plugin_list: List of plugin or inner :class:`Loop`
    :param stop: (optional) stop criteria
    """

    _current_plugin = None

    def __init__(self, plugin_list: str | List[str] | AbstractPlugin | List[AbstractPlugin] | 'Loop',
                 stop: AbstractStopCriteria = None,
                 ctx: Optional[Struct] = None):
        """
        Very broad options for input `plugin_list`. If they come as some form of `str`, the input `ctx` must be given
        to instantiate them.
        """

        self.plugin_list_iter = None
        if plugin_list is None:
            raise InvalidLoopException("Plugin list is None")

        if not isinstance(plugin_list, list):
            plugin_list = [plugin_list]

        self.plugin_list = plugin_list
        self._create_iter()

        if stop is None:
            stop = self._create_stop_criteria()

        stop.parent = self
        self._stop_criteria = stop
        context.register(self)
        if ctx is None:
            ctx = context.ctx()
        self.ctx = ctx

    def __str__(self):
        """ Information summary `str`. """
        result = 'loop: {\n'
        for plugin in self.plugin_list:
            if isinstance(plugin, AbstractPlugin):
                string_to_add = f'{plugin.plugin_name}\n'
            elif isinstance(plugin, str):
                string_to_add = f'{plugin}\n'
            elif isinstance(plugin, Loop):
                string_to_add = f'{str(plugin)}\n'
            else:
                raise ValueError(f'`plugin` must be either `AbstractPlugin`, `str` or `Loop`. Got {plugin}')
            result += string_to_add
        result += f'hash {self.__hash__()}\n}}'
        return result

    def __gt__(self, other):
        """ Overload of > for alphabetical order to enable `dir(loop)`. """
        if isinstance(other, str):
            return self.__str__() > other

    def reset(self):
        """
        Resets the internal state of the loop
        """

        self.plugin_list_iter = iter(self.plugin_list)
        loop_ctx(self).reset()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Returns the next plugin. Allows for using a Loop as an iter
        """

        try:
            if (self._stop_criteria.is_stop()):
                raise StopIteration

            if self._current_plugin is None:
                self._current_plugin = next(self.plugin_list_iter)

                plugin = self._current_plugin
                if isinstance(plugin, AbstractPlugin):
                    self._current_plugin = None
                    plugin.ctx = self.ctx
                    return plugin

                if isinstance(plugin, str):
                    self._current_plugin = None
                    return self._instantiate(plugin)

            if isinstance(self._current_plugin, Loop):
                inner_loop = self._current_plugin
                try:
                    plugin = next(inner_loop)
                    return plugin
                except StopIteration:
                    if (loop_ctx(inner_loop).state == WorkflowState.EXIT):
                        raise StopIteration
                    # inner
                    loop_ctx(inner_loop).reset()
                    self._current_plugin = None
                    return self.__next__()
            else:
                raise UnsupportedPluginTypeException()
        except StopIteration:
            loop_ctx(self).increment()
            self._create_iter()

            if self._stop_criteria.is_stop():
                raise StopIteration
            else:
                return self.__next__()

    def __setstate__(self, state):
        self.__dict__ = state
        context.register(self)

    @staticmethod
    def _create_stop_criteria():
        return SimpleStopCriteria()

    def _instantiate(self, plugin_name):
        return PluginFactory.create_instance(plugin_name, self.ctx)

    def _load_iter(self):
        if self.plugin_list_iter is None:
            self._create_iter()

    def _create_iter(self):
        self.plugin_list_iter = iter(self.plugin_list)
