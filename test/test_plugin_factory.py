from unittest.mock import MagicMock

import pytest

from ivory.context import ctx
from ivory.exceptions.exceptions import UnsupportedPluginTypeException
from ivory.plugin.plugin_factory import PluginFactory
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
        plugin_name = "ivory.plugin.AbstractPlugin"
        try:
            plugin = PluginFactory.create_instance(plugin_name, ctx())
            pytest.fail("UnsupportedPluginTypeException expected", False)
            assert False
        except UnsupportedPluginTypeException as ex:
            assert True

    def test_get_plugin_attribute_expect_value_error(self):
        mock_module = MagicMock(__dir__=MagicMock(return_value=[
            '_invalid',
            'MockPlugin',
            'AbstractInvalidPlugin',
            'SecondMockIsNotSeenPlugin'
        ]))
        try:
            PluginFactory._get_plugin_attribute(module=mock_module)
            assert False
        except ValueError:
            assert True


if __name__ == '__main__':
    pytest.main()
