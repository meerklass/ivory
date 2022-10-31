from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivy.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    backend="sequential",
    cpu_count=1,
    plugins=["test.plugin.simple_plugin",
             ParallelPluginCollection(["test.plugin.simple_square_plugin"],
                                      "test.plugin.range_map_plugin",
                                      "test.plugin.sum_reduce_plugin"),
             "test.plugin.simple_plugin"]
)

SumReducePlugin = ConfigSection(
    values_min=1,
    values_max=10
)

SimplePlugin = ConfigSection(
    value=1
)

RangeMapPlugin = ConfigSection(
    values_min=1,
    values_max=9
)
