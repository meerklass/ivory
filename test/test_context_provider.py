import pytest

from ivory.context_provider import DefaultContextProvider
from ivory.utils.struct import ImmutableStruct, Struct
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

    def test_create_immutable_ctx(self):
        ctx = DefaultContextProvider.create_immutable_context()
        assert isinstance(ctx, ImmutableStruct)

        ctx = DefaultContextProvider.create_immutable_context(a=3)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3

        args = {"a": 3}
        ctx = DefaultContextProvider.create_immutable_context(**args)
        assert isinstance(ctx, ImmutableStruct)
        assert ctx.a == 3


if __name__ == "__main__":
    pytest.main()
