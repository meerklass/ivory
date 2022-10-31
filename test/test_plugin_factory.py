from unittest.mock import MagicMock

import pytest

from ivy.context import ctx
from ivy.exceptions.exceptions import UnsupportedPluginTypeException
from ivy.plugin.plugin_factory import PluginFactory
from test.plugin import simple_plugin

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestPluginFactory:

    def test_simple(self):
        plugin = PluginFactory.create_instance(PLUGIN_NAME, ctx())
        assert plugin is not None
        assert isinstance(plugin, simple_plugin.SimplePlugin)

    def test_unknown_module(self):
        plugin_name = "unknown.plugin.invalid"
        try:
            plugin = PluginFactory.create_instance(plugin_name, ctx())
            pytest.fail("UnsupportedPluginTypeException expected", False)
            assert False
        except UnsupportedPluginTypeException as ex:
            assert True

    def test_invalid_module(self):
        plugin_name = "ivy.plugin.AbstractPlugin"
        try:
            plugin = PluginFactory.create_instance(plugin_name, ctx())
            pytest.fail("UnsupportedPluginTypeException expected", False)
            assert False
        except UnsupportedPluginTypeException as ex:
            assert True

    def test_get_plugin_attribute(self):
        mock_module = MagicMock(__dir__=MagicMock(return_value=[
            '_invalid',
            'MockPlugin',
            'AbstractInvalidPlugin',
            'SecondMockIsNotSeenPlugin'
        ]))
        assert mock_module.MockPlugin == PluginFactory._get_plugin_attribute(module=mock_module)


if __name__ == '__main__':
    pytest.main()
