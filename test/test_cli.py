import pytest

from ivy import context
from ivy.cli.main import _main
from ivy.context import ctx
from test.ctx_sensitive_test import ContextSensitiveTest


class TestCli(ContextSensitiveTest):

    def test_launch_empty(self):
        _main(*[])
        assert context.global_ctx is None  # empty

    def test_launch_loop(self):
        _main(*["test.config.workflow_config_cli"])
        assert ctx().params.Pipeline.plugins is not None
        assert len(ctx().timings) == 2


if __name__ == '__main__':
    pytest.main()
