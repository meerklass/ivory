from pickle import dumps
from pickle import loads

from ivory import context
from ivory.context import ctx
from ivory.loop import Loop
from ivory.plugin.parallel_plugin_collection import ParallelPluginCollection
from ivory.utils.struct import Struct
from ivory.workflow_manager import WorkflowManager

PLUGIN_NAME = "test.plugin.simple_plugin"


class TestPickle:
    def test_loop_pickle(self):
        loop = Loop([PLUGIN_NAME, PLUGIN_NAME])
        next(loop)

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
            "ivory.plugin.simple_map_plugin",
            ["ivory.plugin.simple_square_plugin"],
            "ivory.plugin.simple_reduce_plugin")

        sParallelPluginCollection = dumps(parallelPluginCollection)
        parallelPluginCollectio2 = loads(sParallelPluginCollection)

    def test_context_pickle(self):
        l_ctx = ctx()
        s_l_ctx = dumps(l_ctx)
        l_ctx2 = loads(s_l_ctx)

    def test_workflow_context_pickle(self):
        args = ["--Pipeline-backend=multiprocessing",
                "--Pipeline-cpu-count=1",
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
