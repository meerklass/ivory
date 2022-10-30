
from ivy.loop import Loop

Pipeline = dict(
    plugins=Loop(["test.plugin.simple_plugin",
                  "test.plugin.simple_plugin"])
)
