import pytest

import ivory
from ivory import context
from ivory.cli.main import _main
from ivory.context import ctx
from tests.ctx_sensitive_test import ContextSensitiveTest


class TestCli(ContextSensitiveTest):
    def test_launch_empty(self):
        _main(*[])
        assert context.global_ctx is None  # empty

    def test_launch_loop(self):
        _main(*["tests.config.workflow_config_cli"])
        assert ctx().params.Pipeline.plugins is not None
        assert len(ctx().timings) == 2

    def test_version_flag_prints_installed_version(self, capsys):
        _main(*["--version"])
        assert capsys.readouterr().out.strip() == ivory.__version__
        assert context.global_ctx is None  # did not attempt to launch a workflow

    def test_short_version_flag_prints_installed_version(self, capsys):
        _main(*["-V"])
        assert capsys.readouterr().out.strip() == ivory.__version__
        assert context.global_ctx is None


if __name__ == "__main__":
    pytest.main()
