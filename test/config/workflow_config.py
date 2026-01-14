from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(plugins=Loop(["test.plugin.simple_plugin", "test.plugin.simple_plugin"]))

MockPlugin = ConfigSection(
    a=None,
    b=None,
    c=None,
    d=None,
    e=None,
    f=None,
    g=None,
    h=None,
    i=None,
    j=None,
    bool1=True,
    bool2=True,
    bool3=False,
    bool4=False,
)
