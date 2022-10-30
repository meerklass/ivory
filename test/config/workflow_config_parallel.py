from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection

Pipeline = dict(
    backend="sequential",
    cpu_count=1,
    plugins=["test.plugin.simple_plugin",
             ParallelPluginCollection(["test.plugin.simple_square_plugin"],
                                      "test.plugin.range_map_plugin",
                                      "test.plugin.sum_reduce_plugin"),
             "test.plugin.simple_plugin"]
)

SumReducePlugin = dict(
    values_min=1,
    values_max=10
)

SimplePlugin = dict(
    value=1
)

RangeMapPlugin = dict(
    values_min=1,
    values_max=9
)
