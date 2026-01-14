"""
Test configuration file that can be loaded from anywhere without being part of a package.
Usage: ivory ./test_standalone_config.py
"""
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    backend="sequential",
    plugins=[
        "test.plugin.simple_plugin",
    ],
)

SimplePlugin = ConfigSection(
    value="Hello from standalone config!",
)
