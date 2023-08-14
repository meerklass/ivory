from unittest.mock import MagicMock, patch, Mock

import pytest

from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import UnsupportedPluginTypeException
from ivory.plugin.plugin_factory import PluginFactory
from ivory.utils.struct import Struct
from test.plugin import simple_plugin

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestPluginFactory:

    @patch('ivory.plugin.plugin_factory.importlib')
    @patch.object(PluginFactory, '_get_plugin_attribute')
    def test_create_instance_when_context_empty(self, mock_get_plugin_attribute, mock_importlib):
        plugin = PluginFactory.create_instance(plugin_name='plugin_name', ctx=Struct())
        mock_importlib.import_module.assert_called_once_with('plugin_name')
        mock_get_plugin_attribute.assert_called_once_with(mock_importlib.import_module())
        mock_get_plugin_attribute().assert_called_once()
        assert mock_get_plugin_attribute()() == plugin

    @patch('ivory.plugin.plugin_factory.importlib')
    @patch.object(PluginFactory, '_get_plugin_attribute')
    def test_create_instance(self, mock_get_plugin_attribute, mock_importlib):
        mock_config = {'mock': Mock()}
        context = Struct({
            ConfigKeys.PARAMS.value: {'plugin_name': mock_config},

        })
        mock_get_plugin_attribute.return_value.name = 'plugin_name'
        plugin = PluginFactory.create_instance(plugin_name='plugin_name', ctx=context)
        mock_importlib.import_module.assert_called_once_with('plugin_name')
        mock_get_plugin_attribute.assert_called_once_with(mock_importlib.import_module())
        mock_get_plugin_attribute().assert_called_once_with(**mock_config)
        assert mock_get_plugin_attribute()() == plugin

    def test_get_plugin_attribute(self):
        mock_module = Mock()
        mock_module.AbstractPlugin = Mock()  # this must be ignored
        mock_module.MockPlugin = Mock()
        assert mock_module.MockPlugin == PluginFactory._get_plugin_attribute(module=mock_module)

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

    def test_get_plugin_attribute_when_two_valid_plugins_expect_value_error(self):
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

    def test_get_plugin_attribute_when_no_valid_plugin_expect_value_error(self):
        mock_module = MagicMock(__dir__=MagicMock(return_value=[
            '_invalid',
            'MockPluginn',
            'AbstractInvalidPlugin',
            'SecondMockIsNotSeenPluginn'
        ]))
        try:
            PluginFactory._get_plugin_attribute(module=mock_module)
            assert False
        except ValueError:
            assert True


if __name__ == '__main__':
    pytest.main()
