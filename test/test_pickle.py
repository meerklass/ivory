from pickle import dumps, loads

import pytest

from ivory.context import ctx
from ivory.loop import Loop
from ivory.utils.struct import Struct

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
        loads(dumps_struct)

    def test_context_pickle(self):
        l_ctx = ctx()
        s_l_ctx = dumps(l_ctx)
        loads(s_l_ctx)

    def test_iter_list_can_pickle(self):
        list_iter_expect = iter(["a", "b", "c"])
        next(list_iter_expect)

        dumps_list_iter = dumps(list_iter_expect)
        load_list_iter = loads(dumps_list_iter)

        for expect, value in zip(list_iter_expect, load_list_iter):
            assert expect == value


if __name__ == "__main__":
    pytest.main()
