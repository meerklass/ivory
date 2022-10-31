from ivory import backend
from ivory import context
from ivory.exceptions.exceptions import InvalidAttributeException
from ivory.loop import Loop
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.plugin.plugin_factory import PluginFactory


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
        super().__init__(ctx)

        if not isinstance(plugin_list, Loop):
            plugin_list = Loop(plugin_list)

        self.plugin_list = plugin_list

        if map_plugin is None:
            raise InvalidAttributeException("No map plugin provided")

        self.map_plugin = map_plugin
        self.reduce_plugin = reduce_plugin
        self.parallel = parallel

    def run(self):
        force = None
        if not self.parallel:
            force = "sequential"

        backend_impl = backend.create(self.ctx, force)

        map_plugin = self.map_plugin
        if isinstance(self.map_plugin, str):
            map_plugin = PluginFactory.create_instance(map_plugin, self.ctx)

        ctx_list = backend_impl.run(self.plugin_list, map_plugin)

        if self.reduce_plugin is not None:
            reduce_plugin = self.reduce_plugin
            if isinstance(self.reduce_plugin, str):
                reduce_plugin = PluginFactory.create_instance(reduce_plugin, self.ctx)

            reduce_plugin.run(ctx_list)
