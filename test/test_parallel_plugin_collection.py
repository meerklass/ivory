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
Tests for `ivy.plugin.parallel_plugin_collection ` module.
 
author: jakeret
"""

import pytest

from ivy import context
from ivy.context import ctx
from ivy.exceptions.exceptions import InvalidAttributeException
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivy.workflow_manager import WorkflowManager
from test.ctx_sensitive_test import ContextSensitiveTest
from test.plugin import range_map_plugin
from test.plugin import sum_reduce_plugin

PLUGIN_NAME = "test.plugin.simple_square_plugin"


class TestParallelPluginCollection(ContextSensitiveTest):

    def test_setup(self):
        try:
            ParallelPluginCollection(None, "test.plugin.range_map_plugin")
            pytest.fail("No list provided")
        except InvalidLoopException:
            assert True

        try:
            ParallelPluginCollection([], None)
            pytest.fail("No map plugin provided")
        except InvalidAttributeException:
            assert True

    def test_sequential(self):
        mock_ctx = context.ctx()
        mock_ctx.timings = []
        params_context = context.create_immutable_ctx(
            RangeMapPlugin=context.create_immutable_ctx(values_min=1, values_max=10),
            Pipeline=context.create_immutable_ctx(backend='sequential')
        )
        mock_ctx.params = params_context

        map_plugin = range_map_plugin.RangeMapPlugin(mock_ctx)
        plugin_list = [PLUGIN_NAME]
        reduce_plugin = sum_reduce_plugin.SumReducePlugin(mock_ctx)

        parallel_plugin_collection = ParallelPluginCollection(plugin_list, map_plugin, reduce_plugin)
        parallel_plugin_collection.run()
        assert mock_ctx.SumReducePlugin.values_sum == 285

    def test_multiprocessing(self):
        mock_ctx = context.ctx()
        mock_ctx.timings = []
        params_context = context.create_immutable_ctx(
            RangeMapPlugin=context.create_immutable_ctx(values_min=1, values_max=10),
            Pipeline=context.create_immutable_ctx(backend='multiprocessing', cpu_count=8)
        )
        mock_ctx.params = params_context

        map_plugin = range_map_plugin.RangeMapPlugin(mock_ctx)
        plugin_list = [PLUGIN_NAME]
        reduce_plugin = sum_reduce_plugin.SumReducePlugin(mock_ctx)

        parallel_plugin_collection = ParallelPluginCollection(plugin_list, map_plugin, reduce_plugin)
        parallel_plugin_collection.run()
        assert mock_ctx.SumReducePlugin.values_sum == 285

    #
    def test_parallel_workflow(self):
        args = ["--Pipeline-backend=multiprocessing",
                "--Pipeline-cpu-count=1",
                "test.config.workflow_config_parallel"]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx().SumReducePlugin.values_sum == 204


if __name__ == '__main__':
    pytest.main()
