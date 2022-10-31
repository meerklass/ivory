import pytest

from ivy.context import loop_ctx
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.exceptions.exceptions import UnsupportedPluginTypeException
from ivy.loop import Loop
from ivy.utils.stop_criteria import RangeStopCriteria
from ivy.utils.struct import Struct, WorkflowStruct
from test.ctx_sensitive_test import ContextSensitiveTest
from test.plugin.simple_plugin import SimplePlugin

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestLoop(ContextSensitiveTest):

    def test_none(self):
        try:
            Loop(None)
            assert False
        except InvalidLoopException:
            assert True

    def test_one_plugin(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        plugin = SimplePlugin(mock_ctx)
        loop = Loop(plugin)

        p = next(loop)
        assert p == plugin

        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_plugin_instances(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        plugin1 = SimplePlugin(mock_ctx)
        plugin2 = SimplePlugin(mock_ctx)
        loop = Loop([plugin1, plugin2])

        assert next(loop) == plugin1
        assert next(loop) == plugin2

        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_plugin_names(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        loop = Loop([PLUGIN_NAME, PLUGIN_NAME], ctx=mock_ctx)

        p = next(loop)
        assert isinstance(p, SimplePlugin)
        p = next(loop)
        assert isinstance(p, SimplePlugin)

        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_inner_loop(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})

        loop = Loop(Loop([PLUGIN_NAME, PLUGIN_NAME], ctx=mock_ctx))

        assert isinstance(next(loop), SimplePlugin)
        assert isinstance(next(loop), SimplePlugin)
        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_complex_loop(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        loop = Loop([PLUGIN_NAME,
                     Loop([PLUGIN_NAME,
                           PLUGIN_NAME], ctx=mock_ctx),
                     PLUGIN_NAME], ctx=mock_ctx)

        assert isinstance(next(loop), SimplePlugin)
        assert isinstance(next(loop), SimplePlugin)
        assert isinstance(next(loop), SimplePlugin)
        assert isinstance(next(loop), SimplePlugin)
        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_loop_iter(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        plugin_list = [PLUGIN_NAME, PLUGIN_NAME]
        loop = Loop(plugin_list, ctx=mock_ctx)

        cnt = 0
        for p in loop:
            assert isinstance(p, SimplePlugin)
            cnt += 1

        assert cnt == len(plugin_list)

    def test_loop_max_iter(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        max_iter = 3
        plugin_list = [PLUGIN_NAME, PLUGIN_NAME]

        loop = Loop(plugin_list, ctx=mock_ctx, stop=RangeStopCriteria(max_iter=max_iter))

        cnt = 0
        for p in loop:
            assert isinstance(p, SimplePlugin)
            cnt += 1

        assert cnt == len(plugin_list) * max_iter

    def test_loop_max_iter_nested(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})}),
                           'value': None})
        max_iter = 3
        plugin_list = [SimplePlugin(mock_ctx), SimplePlugin(mock_ctx)]

        loop = Loop(
            Loop(plugin_list,
                 stop=RangeStopCriteria(max_iter=max_iter),
                 ctx=mock_ctx),
            stop=RangeStopCriteria(max_iter=max_iter)
        )

        cnt = 0
        for plugin in loop:
            assert isinstance(plugin, SimplePlugin)
            plugin.run()
            cnt += 1

        assert cnt == len(plugin_list) * max_iter * max_iter

    def test_loop_ctx(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        loop = Loop(PLUGIN_NAME, ctx=mock_ctx)
        ctx_ = loop_ctx(loop)
        assert isinstance(ctx_, WorkflowStruct)

    def test_unknown_plugin(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        plugin = "unknown.plugin.invalid"
        loop = Loop(plugin, ctx=mock_ctx)
        try:
            next(loop)
            assert False
        except UnsupportedPluginTypeException as ex:
            print(ex)
            assert True

        plugin = {}
        try:
            Loop(plugin, ctx=mock_ctx)
            assert False
        except ValueError as ex:
            assert True


if __name__ == '__main__':
    pytest.main()
