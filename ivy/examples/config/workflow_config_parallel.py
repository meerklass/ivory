from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection

Pipeline = dict(
    backend="sequential",
    cpu_count=1,
    valuesMin=1,
    valuesMax=16,

    plugins=ParallelPluginCollection(["ivy.test.simple_square_plugin"],
                                     "ivy.test.range_map_plugin",
                                     "ivy.test.sum_reduce_plugin")
)
