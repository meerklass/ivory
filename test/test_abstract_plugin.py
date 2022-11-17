from unittest.mock import MagicMock

import pytest

from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.result import Result
from ivory.utils.struct import Struct


class MockPlugin(AbstractPlugin):

    def set_requirements(self):
        pass

    def run(self):
        mock_location = MagicMock()
        self.set_result(result=Result(location=mock_location,
                                      result='mock_result'))


class TestAbstractPlugin:
    def test_ini(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': Struct({'mock_parameter': 1})})})
        assert isinstance(MockPlugin(ctx=mock_ctx), MockPlugin)

    def test_str(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        assert 'MockPlugin' == str(MockPlugin(ctx=mock_ctx))

    def test_set_config(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': Struct({'mock_parameter': 1})})})
        assert 1 == MockPlugin(ctx=mock_ctx).config.mock_parameter

    def test_run(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        mock_plugin = MockPlugin(ctx=mock_ctx)
        mock_plugin.run()
        assert 'mock_result' == mock_plugin.results[0].result
        assert isinstance(mock_plugin.results[0].location, MagicMock)

    def test_set_result(self):
        mock_plugin = MockPlugin()
        mock_result_1 = MagicMock()
        mock_result_2 = MagicMock()
        mock_plugin.set_result(result=mock_result_1)
        mock_plugin.set_result(result=mock_result_2)
        assert mock_plugin.results == [mock_result_1, mock_result_2]


if __name__ == '__main__':
    pytest.main()
