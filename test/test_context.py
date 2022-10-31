import pytest

from ivory import context
from ivory.context import loop_ctx
from ivory.context import register
from ivory.exceptions.exceptions import InvalidLoopException
from ivory.loop import Loop
from ivory.utils.struct import ImmutableStruct
from ivory.utils.struct import Struct
from test.ctx_sensitive_test import ContextSensitiveTest


class TestContext(ContextSensitiveTest):

    def test_register(self):
        loop = Loop("plugin")
        try:
            register(loop)
            pytest.fail("Loop registered twice")
        except InvalidLoopException as ex:
            assert True

        lctx = loop_ctx(loop)
        assert lctx is not None

    def test_create_ctx(self):
        ctx = context._create_ctx()
        assert isinstance(ctx, Struct)

        ctx = context._create_ctx(a=3)
        assert isinstance(ctx, Struct)
        assert ctx.a == 3

        args = {"a": 3}
        ctx = context._create_ctx(**args)
        assert isinstance(ctx, Struct)
        assert ctx.a == 3

    def test_create_immu_ctx(self):
        ctx = context.create_immutable_ctx()
        assert isinstance(ctx, ImmutableStruct)

        ctx = context.create_immutable_ctx(a=3)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3

        args = {"a": 3}
        ctx = context.create_immutable_ctx(**args)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3
