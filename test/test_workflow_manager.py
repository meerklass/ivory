import os
import tempfile
from getopt import GetoptError
from operator import eq
from pathlib import Path

import pytest

from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import IllegalAccessException, InvalidAttributeException
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.struct import Struct
from ivory.workflow_manager import WorkflowManager
from test.ctx_sensitive_test import ContextSensitiveTest
from test.plugin.simple_plugin import SimpleEnum, SimplePlugin


class TestWorkflowManager(ContextSensitiveTest):
    @classmethod
    def setup_class(cls):
        # Ensure cache directory exists for tests that require it
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_dir.mkdir(exist_ok=True)

    def test_launch(self):
        args = ["test.config.workflow_config"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        assert ctx().params is not None
        assert ctx().params.Pipeline.plugins is not None

    def test_launch_expect_context_stored_to_hard_disc(self):
        args = ["test.config.workflow_config_store_context"]

        mgr = WorkflowManager(args)
        mgr.launch()
        assert ctx()[SimpleEnum.simple].result == 1

    def test_launch_expect_context_loaded_from_hard_disc(self):
        args = ["test.config.workflow_config_load_context"]

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
            "test.config.workflow_config",
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
        args = ["test.config.workflow_config_simple"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        assert ctx().params is not None
        assert ctx().params.Pipeline.plugins is not None
        assert isinstance(ctx().params.Pipeline.plugins, Loop)

    def test_workflow_manager_when_config_empty_expect_value_error(self):
        args = ["test.config.workflow_config_empty"]
        try:
            WorkflowManager(args)
            pytest.fail("config without plugins not allowed", True)
        except ValueError:
            assert True

    def test_missing_plugins(self):
        args = ["test.config.workflow_config_missing_plugins"]

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
        args = ["test.config.workflow_config_simple", "test.config.workflow_config_simple"]
        try:
            WorkflowManager(args)
            pytest.fail("two configs not allowed", True)
        except InvalidAttributeException:
            assert True

    def test_invalid_args(self):
        args = ["-a=1", "test.config.workflow_config_simple"]
        try:
            WorkflowManager(args)
            pytest.fail("wrong argument format", True)
        except GetoptError:
            assert True

    def test_unknown_args(self):
        args = ["--a=1", "test.config.workflow_config_simple"]
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
            config_sections={"Section": ConfigSection(a=2)}, opt_parameter_dict={"Section": ConfigSection(a=3)}
        )
        assert config.Section.a == 3

    def test_config_immutable_when_list_expect_loop(self):
        config = WorkflowManager._config_immutable(
            config_sections={"Pipeline": ConfigSection({ConfigKeys.PLUGINS.value: [SimplePlugin(Struct())]})}
        )
        assert isinstance(config.Pipeline.plugins, Loop)

    def test_copy_results_from_context(self):
        from enum import Enum

        class MockEnum(Enum):
            mock = "mock"

        WorkflowManager._copy_results_from_context(context_=Struct({"key": "value", MockEnum.mock: "mock"}))
        assert "key" not in ctx()
        assert MockEnum.mock in ctx()

    def test_load_config_from_file_path(self):
        """Test that configuration can be loaded from a file path instead of module name"""
        # Create a temporary config file
        config_content = """
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin"],
)

TestSection = ConfigSection(
    test_param="from_file",
)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name

        try:
            # Test loading from absolute path
            args = [temp_config_path]
            WorkflowManager(args)

            assert ctx().params is not None
            assert ctx().params.Pipeline.plugins is not None
            assert ctx().params.TestSection.test_param == "from_file"
        finally:
            # Clean up
            os.unlink(temp_config_path)

    def test_load_config_file_not_found(self):
        """Test that loading a non-existent file path raises appropriate error"""
        args = ["/non/existent/path/config.py"]

        with pytest.raises(FileNotFoundError):
            WorkflowManager(args)

    def test_load_config_from_user_directory(self):
        """Test that config can be loaded from a user-writable directory like home"""
        import shutil

        config_content = """
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = ConfigSection(
    value="loaded_from_user_dir",
)
"""
        # Create config in a temporary user directory
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "user_config.py")

        try:
            # Write config file
            with open(config_path, "w") as f:
                f.write(config_content)

            # Test loading from the user directory
            args = [config_path]
            WorkflowManager(args)

            assert ctx().params is not None
            assert ctx().params.Pipeline.plugins is not None
            assert ctx().params.SimplePlugin.value == "loaded_from_user_dir"
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def test_load_config_with_relative_path(self):
        """Test that config can be loaded from a relative path"""
        config_content = """
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = ConfigSection(
    value="relative_path_config",
)
"""
        # Create config in current working directory
        config_filename = "test_relative_config.py"

        try:
            with open(config_filename, "w") as f:
                f.write(config_content)

            # Test loading with relative path
            args = [f"./{config_filename}"]
            WorkflowManager(args)

            assert ctx().params is not None
            assert ctx().params.SimplePlugin.value == "relative_path_config"
        finally:
            # Clean up
            if os.path.exists(config_filename):
                os.unlink(config_filename)

    def test_load_config_with_command_line_overrides(self):
        """Test that command line arguments properly override file-based config"""
        config_content = """
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = ConfigSection(
    value="original_value",
    count=100,
)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name

        try:
            # Test with command line override
            args = ["--SimplePlugin-value=overridden", "--SimplePlugin-count=200", temp_config_path]
            WorkflowManager(args)

            assert ctx().params.SimplePlugin.value == "overridden"
            assert ctx().params.SimplePlugin.count == 200
        finally:
            os.unlink(temp_config_path)

    def test_load_config_and_run_workflow(self):
        """Integration test: load config from file and run complete workflow"""
        config_content = """
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin"],
)

SimplePlugin = ConfigSection(
    value="workflow_test",
)
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(config_content)
            temp_config_path = f.name

        try:
            # Load and launch workflow
            args = [temp_config_path]
            mgr = WorkflowManager(args)
            mgr.launch()

            # Verify workflow completed successfully
            assert ctx().timings is not None
            assert len(ctx().timings) > 0
        finally:
            os.unlink(temp_config_path)


if __name__ == "__main__":
    pytest.main()
