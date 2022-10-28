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
Created on Mar 18, 2014

author: jakeret
"""
from ivy import backend
from ivy import context
from ivy.exceptions.exceptions import InvalidAttributeException
from ivy.loop import Loop
from ivy.plugin.abstract_plugin import AbstractPlugin
from ivy.plugin.plugin_factory import PluginFactory


class ParallelPluginCollection(AbstractPlugin):
    """
    Collection that allows for executing plugins in parallel by using
    a MapReduce aprach. The implementation therefore requires a
    list of plugins to execute, a map plugin creating the workload and 
    (optionally) a reduce plugin reducing the data from the parallel task exection
    
    :param plugin_list: List of plugins (or a Loop) which should be executed in parallel
    :param map_plugin:
    :param reduce_plugin: (optional)
    :param ctx: (optional) 
    """

    def __init__(self, plugin_list, map_plugin, reduce_plugin=None, ctx=None, parallel=True):

        """
        Constructor
        """
        if ctx is None:
            ctx = context.ctx()
        self.ctx = ctx

        super(ParallelPluginCollection, self).__init__(self.ctx)

        if not isinstance(plugin_list, Loop):
            plugin_list = Loop(plugin_list)

        self.plugin_list = plugin_list

        if map_plugin is None:
            raise InvalidAttributeException("No map plugin provided")

        self.map_plugin = map_plugin
        self.reduce_plugin = reduce_plugin
        self.parallel = parallel

    def __str__(self):
        return "ParallelPluginCollection"

    def run(self):
        force = None
        if not self.parallel:
            force = "sequential"

        backend_impl = backend.create(self.ctx, force)

        map_plugin = self.map_plugin
        if isinstance(self.map_plugin, str):
            map_plugin = PluginFactory.createInstance(map_plugin, self.ctx)

        ctx_list = backend_impl.run(self.plugin_list, map_plugin)

        if self.reduce_plugin is not None:
            reduce_plugin = self.reduce_plugin
            if isinstance(self.reduce_plugin, str):
                reduce_plugin = PluginFactory.createInstance(reduce_plugin, self.ctx)

            reduce_plugin.reduce(ctx_list)
