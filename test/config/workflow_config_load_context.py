import os

from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=Loop(["test.plugin.simple_plugin"]),
    context=os.path.join(os.getcwd(), 'cache/simple_plugin.pickle')
)

SimplePlugin = ConfigSection(
    value='load'
)
