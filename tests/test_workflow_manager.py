import os
import pickle
import tempfile
from getopt import GetoptError
from operator import eq
from pathlib import Path

import pytest

from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import (
    IllegalAccessException,
    InvalidAttributeException,
)
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.result import Result
from ivory.utils.struct import Struct
from ivory.workflow_manager import WorkflowManager
from tests.ctx_sensitive_test import ContextSensitiveTest
from tests.plugin.simple_plugin import SimpleEnum, SimplePlugin


class TestWorkflowManager(ContextSensitiveTest):
    @staticmethod
    def _write_stored_context_pickle(tmp_path: Path) -> Path:
        """
        Writes a checkpoint pickle equivalent to what `workflow_config_store_context`
        produces at `tmp_path/cache/simple_plugin.pickle`, without going through
        `WorkflowManager.launch()` a second time. `tests.config.workflow_config_store_context`
        is a module-level singleton (Python caches it on first import) whose `Loop` object
        registers itself against whichever global context is live at import time; reusing
        that cached module's `launch()` across more than one test breaks once the context
        singleton is reset between tests, so tests that just need an existing checkpoint on
        disc synthesize it directly instead of re-running the store pipeline.
        """
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        pickle_path = cache_dir / "simple_plugin.pickle"
        stored_ctx = Struct(
            {SimpleEnum.simple: Result(location=SimpleEnum.simple, result=1)}
        )
        with open(pickle_path, "wb") as out_file:
            pickle.dump(stored_ctx, out_file)
        return pickle_path

    def test_launch(self):
        args = ["tests.config.workflow_config"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        assert ctx().params is not None
        assert ctx().params.Pipeline.plugins is not None

    def test_launch_expect_context_stored_to_hard_disc(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "cache").mkdir(exist_ok=True)
        args = ["tests.config.workflow_config_store_context"]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx()[SimpleEnum.simple].result == 1
        assert (tmp_path / "cache" / "simple_plugin.pickle").is_file()

    def test_launch_expect_context_loaded_from_hard_disc(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_stored_context_pickle(tmp_path)
        args = ["tests.config.workflow_config_load_context"]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx()[SimpleEnum.simple].result == 1

    def test_launch_expect_context_overridden_via_cli(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        self._write_stored_context_pickle(tmp_path)
        # `workflow_config_cli_context` does not set `Pipeline.context`, so this
        # only loads the previously stored context if the CLI override works.
        args = [
            "--Pipeline-context=cache/simple_plugin.pickle",
            "tests.config.workflow_config_cli_context",
        ]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx()[SimpleEnum.simple].result == 1

    def test_parse_args(self):
        args = [
            "--MockPlugin-a=True",
            "--MockPlugin-b=False",
            "--MockPlugin-c=-1",
            "--MockPlugin-d=0",
            "--MockPlugin-e=1",
            "--MockPlugin-f=-1.0",
            "--MockPlugin-g=0.0",
            "--MockPlugin-h=1.0",
            "--MockPlugin-i=le_string",
            "--MockPlugin-j=1,2,3,4",
            "--MockPlugin-bool1=True",
            "--MockPlugin-bool2=False",
            "--MockPlugin-bool3=True",
            "--MockPlugin-bool4=False",
            "tests.config.workflow_config",
        ]

        WorkflowManager(args)

        assert ctx().params.MockPlugin.a
        assert not ctx().params.MockPlugin.b
        assert ctx().params.MockPlugin.c == -1
        assert ctx().params.MockPlugin.d == 0
        assert ctx().params.MockPlugin.e == 1
        assert ctx().params.MockPlugin.f == -1.0
        assert ctx().params.MockPlugin.g == 0.0
        assert ctx().params.MockPlugin.h == 1.0
        assert ctx().params.MockPlugin.i == "le_string"
        assert ctx().params.MockPlugin.bool1
        assert not ctx().params.MockPlugin.bool2
        assert ctx().params.MockPlugin.bool3
        assert not ctx().params.MockPlugin.bool4
        assert all(map(eq, ctx().params.MockPlugin.j, [1, 2, 3, 4]))

    def test_simple_launch(self):
        args = ["tests.config.workflow_config_simple"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        assert ctx().params is not None
        assert ctx().params.Pipeline.plugins is not None
        assert isinstance(ctx().params.Pipeline.plugins, Loop)

    def test_workflow_manager_when_config_empty_expect_value_error(self):
        args = ["tests.config.workflow_config_empty"]
        try:
            WorkflowManager(args)
            pytest.fail("config without plugins not allowed", True)
        except ValueError:
            assert True

    def test_missing_plugins(self):
        args = ["tests.config.workflow_config_missing_plugins"]

        try:
            WorkflowManager(args)
            pytest.fail("config without plugins not allowed", True)
        except InvalidAttributeException:
            assert True

    def test_missing_config(self):
        try:
            WorkflowManager(None)
            pytest.fail("missing config not allowed", True)
        except ValueError:
            assert True

        try:
            WorkflowManager([])
            pytest.fail("missing config not allowed", True)
        except ValueError:
            assert True

    def test_invalid_config(self):
        args = [
            "tests.config.workflow_config_simple",
            "tests.config.workflow_config_simple",
        ]
        try:
            WorkflowManager(args)
            pytest.fail("two configs not allowed", True)
        except InvalidAttributeException:
            assert True

    def test_invalid_args(self):
        args = ["-a=1", "tests.config.workflow_config_simple"]
        try:
            WorkflowManager(args)
            pytest.fail("wrong argument format", True)
        except GetoptError:
            assert True

    def test_unknown_args(self):
        args = ["--a=1", "tests.config.workflow_config_simple"]
        try:
            WorkflowManager(args)
            pytest.fail("wrong argument format", True)
        except GetoptError:
            assert True

    def test_config_immutable_invalid(self):
        try:
            _ = WorkflowManager._config_immutable(None)
            pytest.fail("No config name not allowed", True)
        except AttributeError:
            assert True

    def test_config_immutable_when_try_to_overwrite_assert_raise(self):
        config = WorkflowManager._config_immutable({"Section": ConfigSection(a=2)})
        try:
            config.Section = 1
            assert False
        except IllegalAccessException:
            assert True
        try:
            config.Section.a = 1
            assert False
        except IllegalAccessException:
            assert True

    def test_config_immutable(self):
        config = WorkflowManager._config_immutable({"Section": ConfigSection(a=2)})
        assert config.Section.a == 2

    def test_config_immutable_when_opt_given(self):
        config = WorkflowManager._config_immutable(
            config_sections={"Section": ConfigSection(a=2)},
            opt_parameter_dict={"Section": ConfigSection(a=3)},
        )
        assert config.Section.a == 3

    def test_config_immutable_when_list_expect_loop(self):
        config = WorkflowManager._config_immutable(
            config_sections={
                "Pipeline": ConfigSection(
                    {ConfigKeys.PLUGINS.value: [SimplePlugin(Struct())]}
                )
            }
        )
        assert isinstance(config.Pipeline.plugins, Loop)

    def test_load_config_from_file_path_absolute(self):
        config_content = (
            "from ivory.utils.config_section import ConfigSection\n\n"
            "Pipeline = ConfigSection(plugins=['tests.plugin.simple_plugin'])\n"
            "TestSection = ConfigSection(test_param='from_absolute_file')\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name

        try:
            WorkflowManager([temp_config_path])
            assert ctx().params is not None
            assert ctx().params.Pipeline.plugins is not None
            assert ctx().params.TestSection.test_param == "from_absolute_file"
        finally:
            os.unlink(temp_config_path)

    def test_load_config_from_file_path_relative(self, tmp_path, monkeypatch):
        config_content = (
            "from ivory.utils.config_section import ConfigSection\n\n"
            "Pipeline = ConfigSection(plugins=['tests.plugin.simple_plugin'])\n"
            "TestSection = ConfigSection(test_param='from_relative_file')\n"
        )
        config_path = tmp_path / "relative_config.py"
        config_path.write_text(config_content)
        monkeypatch.chdir(tmp_path)

        WorkflowManager([f"./{config_path.name}"])
        assert ctx().params.TestSection.test_param == "from_relative_file"

    def test_load_config_file_not_found(self):
        args = ["/non/existent/path/config.py"]
        with pytest.raises(FileNotFoundError):
            WorkflowManager(args)

    def test_load_config_module_name_still_works(self):
        # Regression: dotted module names must still resolve via the module branch,
        # not be misclassified as a file path.
        args = ["tests.config.workflow_config"]
        WorkflowManager(args)
        assert ctx().params.Pipeline.plugins is not None

    def test_load_config_two_file_based_configs_do_not_collide(self):
        content_a = (
            "from ivory.utils.config_section import ConfigSection\n\n"
            "Pipeline = ConfigSection(plugins=['tests.plugin.simple_plugin'])\n"
            "TestSection = ConfigSection(test_param='config_a')\n"
        )
        content_b = (
            "from ivory.utils.config_section import ConfigSection\n\n"
            "Pipeline = ConfigSection(plugins=['tests.plugin.simple_plugin'])\n"
            "TestSection = ConfigSection(test_param='config_b')\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content_a)
            path_a = f.name
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(content_b)
            path_b = f.name

        try:
            module_a = WorkflowManager._load_config(path_a)
            module_b = WorkflowManager._load_config(path_b)
            assert module_a is not module_b
            assert module_a.TestSection["test_param"] == "config_a"
            assert module_b.TestSection["test_param"] == "config_b"
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_load_config_via_load_config_static_method(self):
        module = WorkflowManager._load_config("tests.config.workflow_config")
        assert module.Pipeline["plugins"] is not None

    def test_load_context_into_ctx(self):
        from enum import Enum

        class MockEnum(Enum):
            mock = "mock"

        WorkflowManager._load_context_into_ctx(
            context_=Struct({"key": "value", MockEnum.mock: "mock"})
        )
        assert "key" not in ctx()
        assert MockEnum.mock in ctx()


if __name__ == "__main__":
    pytest.main()
