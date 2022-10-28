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
Tests for `ivy.loop ` module.

author: jakeret
"""

from pickle import dumps
from pickle import loads

from ivy import context
from ivy.context import ctx
from ivy.loop import Loop
from ivy.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivy.utils.struct import Struct
from ivy.workflow_manager import WorkflowManager

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestPickle:
    def test_loop_pickle(self):
        loop = Loop([PLUGIN_NAME, PLUGIN_NAME])
        plugin = next(loop)

        dumps_loop = dumps(loop)
        loop2 = loads(dumps_loop)

        for plugin in loop2:
            plugin.run()

        loop.reset()

        dumps_loop = dumps(loop)
        loop2 = loads(dumps_loop)

        for plugin in loop2:
            plugin.run()

    def test_struct_pickle(self):
        struct = Struct(value1=1)
        struct.params = Struct(backend="multiprocessing")

        dumps_struct = dumps(struct)
        struct2 = loads(dumps_struct)

    def test_parallel_plugin_collection_pickle(self):
        ctx = context.ctx()

        parallelPluginCollection = ParallelPluginCollection(
            "ivy.plugin.simple_map_plugin",
            ["ivy.plugin.simple_square_plugin"],
            "ivy.plugin.simple_reduce_plugin")

        sParallelPluginCollection = dumps(parallelPluginCollection)
        parallelPluginCollectio2 = loads(sParallelPluginCollection)

    def test_context_pickle(self):
        l_ctx = ctx()
        s_l_ctx = dumps(l_ctx)
        l_ctx2 = loads(s_l_ctx)

    def test_workflow_context_pickle(self):
        args = ["--backend=multiprocessing",
                "--cpu-count=1",
                "test.config.workflow_config_parallel"]

        mgr = WorkflowManager(args)

        l_ctx = ctx()
        s_l_ctx = dumps(l_ctx)
        l_ctx2 = loads(s_l_ctx)

    def test_iter_list_can_pickle(self):
        list_iter_expect = iter(["a", "b", "c"])
        next(list_iter_expect)

        dumps_list_iter = dumps(list_iter_expect)
        load_list_iter = loads(dumps_list_iter)

        for expect, value in zip(list_iter_expect, load_list_iter):
            assert expect == value


if __name__ == '__main__':
    #     pytest.main()
    test = TestPickle()
    test.test_loop_pickle()
