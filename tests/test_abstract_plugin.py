import unittest
from unittest.mock import MagicMock

import pytest

from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result


class MockPlugin(AbstractPlugin):
    def set_requirements(self):
        pass

    def run(self):
        mock_location = MagicMock()
        self.set_result(result=Result(location=mock_location, result="mock_result"))


class MockRequirementPlugin(AbstractPlugin):
    """Appends to `self.requirements` instead of reassigning it, to catch a regression
    of the `requirements` list being a shared mutable class attribute."""

    def set_requirements(self):
        self.requirements.append(Requirement(location="x", variable="x"))

    def run(self):
        pass


class MockBrokenPluginn(AbstractPlugin):
    def set_requirements(self):
        pass

    def run(self):
        pass


class TestAbstractPlugin(unittest.TestCase):
    def test_ini(self):
        assert isinstance(MockPlugin(), MockPlugin)

    def test_str(self):
        assert "MockPlugin" == str(MockPlugin())

    def test_run(self):
        mock_plugin = MockPlugin()
        mock_plugin.run()
        assert "mock_result" == mock_plugin.results[0].result
        assert isinstance(mock_plugin.results[0].location, MagicMock)

    def test_set_result(self):
        mock_plugin = MockPlugin()
        mock_result_1 = MagicMock()
        mock_result_2 = MagicMock()
        mock_plugin.set_result(result=mock_result_1)
        mock_plugin.set_result(result=mock_result_2)
        assert mock_plugin.results == [mock_result_1, mock_result_2]

    def test_ini_when_wrong_name_expect_value_error(self):
        self.assertRaises(ValueError, MockBrokenPluginn)

    def test_requirements_are_not_shared_across_instances_or_classes(self):
        """Regression test for `requirements` being a class-level mutable default:
        appending on one plugin instance must not leak into unrelated plugins."""
        a = MockRequirementPlugin()
        b = MockPlugin()

        assert a.requirements == [Requirement(location="x", variable="x")]
        assert b.requirements == []

        # A second instance of the same plugin must not accumulate the first's entries.
        a2 = MockRequirementPlugin()
        assert a2.requirements == [Requirement(location="x", variable="x")]
        assert a.requirements == [Requirement(location="x", variable="x")]


if __name__ == "__main__":
    pytest.main()
