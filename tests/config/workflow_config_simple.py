from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["tests.plugin.simple_plugin", "tests.plugin.simple_plugin"]
)
