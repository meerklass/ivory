import pytest

from ivy.context import ctx
from test.plugin.simple_plugin import SimplePlugin


class TestSimplePlugin:

    def test_simple(self):
        plugin = SimplePlugin(ctx())
        assert 'value' not in plugin.ctx

        plugin = SimplePlugin(ctx(), value=1)
        assert plugin.ctx.value == 1

        SimplePlugin(ctx(), foo=1)
        assert ctx().foo == 1


if __name__ == '__main__':
    pytest.main()
