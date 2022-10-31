import os

import pytest

from ivy import context
from ivy.context import ctx
from ivy.context_provider import DefaultContextProvider
from ivy.context_provider import PickleContextProvider
from ivy.utils.struct import ImmutableStruct
from ivy.utils.struct import Struct
from ivy.workflow_manager import WorkflowManager
from test.ctx_sensitive_test import ContextSensitiveTest


class TestContextProvider(ContextSensitiveTest):

    def test_create_ctx(self):
        ctx = DefaultContextProvider.create_context()
        assert isinstance(ctx, Struct)

        ctx = DefaultContextProvider.create_context(a=3)
        assert isinstance(ctx, Struct)
        assert ctx.a == 3

        args = {"a": 3}
        ctx = DefaultContextProvider.create_context(**args)
        assert isinstance(ctx, Struct)
        assert ctx.a == 3

    def test_create_immu_ctx(self):
        ctx = DefaultContextProvider.create_immutable_context()
        assert isinstance(ctx, ImmutableStruct)

        ctx = DefaultContextProvider.create_immutable_context(a=3)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3

        args = {"a": 3}
        ctx = DefaultContextProvider.create_immutable_context(**args)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3


class TestPickleContextProvider(ContextSensitiveTest):

    def test_cust_ctx_provider(self):
        context.global_ctx = None
        args = ["test.config.workflow_config_cust"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        from ivy.context import get_context_provider
        assert get_context_provider() == PickleContextProvider

    def test_storeContext(self, tmpdir):
        path = str(tmpdir.join("le_ctx"))
        ctx().ctx_file_name = path
        PickleContextProvider.store_context()
        assert os.path.exists(path)

    def teardown(self):
        # tidy up
        print("tearing down " + __name__)
        context.global_ctx = None


if __name__ == '__main__':
    pytest.main()
