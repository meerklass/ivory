from ivory.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    backend="sequential",
    cpu_count=1,
    valuesMin=1,
    valuesMax=16,

    plugins=ParallelPluginCollection(["ivory.test.simple_square_plugin"],
                                     "ivory.test.range_map_plugin",
                                     "ivory.test.sum_reduce_plugin")
)
