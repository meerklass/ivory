
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=Loop(["test.plugin.simple_plugin",
                  "test.plugin.simple_plugin"])
)
