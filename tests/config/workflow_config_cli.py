from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=Loop(["tests.plugin.simple_plugin", "tests.plugin.simple_plugin"])
)
