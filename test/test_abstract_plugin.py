import pytest

from ivy.plugin.abstract_plugin import AbstractPlugin
from ivy.utils.struct import Struct


class MockPlugin(AbstractPlugin):

    @classmethod
    @property
    def name(cls):
        return 'MockPlugin'

    def run(self):
        self.save_to_context(result_dict={'mock_output': 'mock_result'})


class TestAbstractPlugin:
    def test_ini(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': Struct({'mock_parameter': 1})})})
        MockPlugin(ctx=mock_ctx)
        assert 1 == mock_ctx.params.MockPlugin.mock_parameter

    def test_str(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        assert 'MockPlugin' == str(MockPlugin(ctx=mock_ctx))

    def test_run(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        mock_plugin = MockPlugin(ctx=mock_ctx)
        mock_plugin.run()
        assert 'mock_result' == mock_ctx.MockPlugin.mock_output

    def test_output_of_plugin(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        mock_plugin = MockPlugin(ctx=mock_ctx)
        assert 'mock_result' not in mock_plugin.output_of_plugin(plugin=MockPlugin)
        mock_plugin.run()
        assert 'mock_result' == mock_plugin.output_of_plugin(plugin=MockPlugin)['mock_output']

    def test_save_to_context(self):
        mock_ctx = Struct({'params': Struct({'MockPlugin': 'mock_struct'})})
        mock_plugin = MockPlugin(ctx=mock_ctx)
        mock_plugin.save_to_context(result_dict={'mock_output': 'mock_result'})
        assert 'mock_result' == mock_ctx.MockPlugin.mock_output


if __name__ == '__main__':
    pytest.main()
