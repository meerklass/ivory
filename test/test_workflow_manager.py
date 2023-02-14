from getopt import GetoptError
from operator import eq

import pytest

from ivory.config_keys import ConfigKeys
from ivory.context import ctx
from ivory.exceptions.exceptions import InvalidAttributeException, IllegalAccessException
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.struct import Struct
from ivory.workflow_manager import WorkflowManager
from test.ctx_sensitive_test import ContextSensitiveTest
from test.plugin.simple_plugin import SimplePlugin


class TestWorkflowManager(ContextSensitiveTest):

    def test_launch(self):
        args = ["test.config.workflow_config"]

        mgr = WorkflowManager(args)
        mgr.launch()

        assert ctx() is not None
        assert ctx().params is not None
        assert ctx().params.Pipeline.plugins is not None

    # TODO: add test for launch with context loaded from hard disc

    def test_parse_args(self):
        args = ["--MockPlugin-a=True",
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
                "test.config.workflow_config"]

        mgr = WorkflowManager(args)

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
        args = ['test.config.workflow_config_empty']
        try:
            WorkflowManager(args)
            pytest.fail("config without plugins not allowed", True)
        except ValueError:
            assert True

    def test_missing_plugins(self):
        args = ["test.config.workflow_config_missing_plugins"]

        try:
            mgr = WorkflowManager(args)
            pytest.fail("config without plugins not allowed", True)
        except InvalidAttributeException:
            assert True

    def test_missing_config(self):
        try:
            mgr = WorkflowManager(None)
            pytest.fail("missing config not allowed", True)
        except ValueError:
            assert True

        try:
            mgr = WorkflowManager([])
            pytest.fail("missing config not allowed", True)
        except ValueError:
            assert True

    def test_invalid_config(self):
        args = ["test.config.workflow_config_simple", "test.config.workflow_config_simple"]
        try:
            mgr = WorkflowManager(args)
            pytest.fail("two configs not allowed", True)
        except InvalidAttributeException:
            assert True

    def test_invalid_args(self):
        args = ["-a=1",
                "test.config.workflow_config_simple"]
        try:
            mgr = WorkflowManager(args)
            pytest.fail("wrong argument format", True)
        except GetoptError:
            assert True

    def test_unknown_args(self):
        args = ["--a=1",
                "test.config.workflow_config_simple"]
        try:
            mgr = WorkflowManager(args)
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
        config = WorkflowManager._config_immutable({'Section': ConfigSection(a=2)})
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
        config = WorkflowManager._config_immutable({'Section': ConfigSection(a=2)})
        assert config.Section.a == 2

    def test_config_immutable_when_opt_given(self):
        config = WorkflowManager._config_immutable(config_sections={'Section': ConfigSection(a=2)},
                                                   opt_parameter_dict={'Section': ConfigSection(a=3)})
        assert config.Section.a == 3

    def test_config_immutable_when_list_expect_loop(self):
        config = WorkflowManager._config_immutable(
            config_sections={'Pipeline': ConfigSection({ConfigKeys.PLUGINS.value: [SimplePlugin(Struct())]})}
        )
        assert isinstance(config.Pipeline.plugins, Loop)

    def test_copy_results_from_context(self):
        from enum import Enum
        class MockEnum(Enum):
            mock = 'mock'

        WorkflowManager._copy_results_from_context(context_=Struct({'key': 'value',
                                                                    MockEnum.mock: 'mock'}))
        assert 'key' not in ctx()
        assert MockEnum.mock in ctx()


if __name__ == '__main__':
    pytest.main()
