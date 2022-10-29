# IVY is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# IVY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with IVY.  If not, see <http://www.gnu.org/licenses/>.


"""
Tests for `ivy.Loop` module.

author: jakeret
"""
import pytest

from ivy.context import loop_ctx
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.exceptions.exceptions import UnsupportedPluginTypeException
from ivy.loop import Loop
from ivy.utils.stop_criteria import RangeStopCriteria
from ivy.utils.struct import Struct, WorkflowStruct
from test.ctx_sensitive_test import ContextSensitiveTest
from test.plugin.simple_plugin import Plugin

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestLoop(ContextSensitiveTest):

    def test_none(self):
        try:
            loop = Loop(None)
            assert False
        except InvalidLoopException:
            assert True

    def test_one_plugin(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        plugin = Plugin(mock_ctx)
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
        plugin1 = Plugin(mock_ctx)
        plugin2 = Plugin(mock_ctx)
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
        assert isinstance(p, Plugin)
        p = next(loop)
        assert isinstance(p, Plugin)

        try:
            next(loop)
            assert False
        except StopIteration:
            assert True

    def test_inner_loop(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})

        loop = Loop(Loop([PLUGIN_NAME, PLUGIN_NAME], ctx=mock_ctx))

        assert isinstance(next(loop), Plugin)
        assert isinstance(next(loop), Plugin)
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

        assert isinstance(next(loop), Plugin)
        assert isinstance(next(loop), Plugin)
        assert isinstance(next(loop), Plugin)
        assert isinstance(next(loop), Plugin)
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
            assert isinstance(p, Plugin)
            cnt += 1

        assert cnt == len(plugin_list)

    def test_loop_max_iter(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})})})
        max_iter = 3
        plugin_list = [PLUGIN_NAME, PLUGIN_NAME]

        loop = Loop(plugin_list, ctx=mock_ctx, stop=RangeStopCriteria(max_iter=max_iter))

        cnt = 0
        for p in loop:
            assert isinstance(p, Plugin)
            cnt += 1

        assert cnt == len(plugin_list) * max_iter

    def test_loop_max_iter_nested(self):
        mock_ctx = Struct({'params': Struct({'SimplePlugin': Struct({'mock_parameter': 1})}),
                           'value': None})
        max_iter = 3
        plugin_list = [Plugin(mock_ctx), Plugin(mock_ctx)]

        loop = Loop(
            Loop(plugin_list,
                 stop=RangeStopCriteria(max_iter=max_iter),
                 ctx=mock_ctx),
            stop=RangeStopCriteria(max_iter=max_iter)
        )

        cnt = 0
        for plugin in loop:
            assert isinstance(plugin, Plugin)
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
