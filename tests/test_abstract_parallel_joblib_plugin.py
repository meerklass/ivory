from collections.abc import Generator
from typing import Any

from ivory.plugin.abstract_parallel_joblib_plugin import AbstractParallelJoblibPlugin


class MockPlugin(AbstractParallelJoblibPlugin):
    def run_job(self, anything: Any) -> Any:
        return anything * 2

    def map(self, **kwargs) -> Generator[Any, None, None]:
        return [1, 2, 3]

    def gather_and_set_result(self, *args, **kwargs):
        self.gathered = args[0]

    def set_requirements(self):
        pass


class TestAbstractParallelJoblibPlugin:
    def test_ini(self):
        mock_plugin = MockPlugin(n_jobs=1, verbose=0)
        assert mock_plugin.n_jobs == 1
        assert mock_plugin.verbose == 0

    def test_run(self):
        mock_plugin = MockPlugin(n_jobs=2, verbose=0)
        mock_plugin.run()

        # `run_job` doubles each element `map()` yields; `gather_and_set_result` records
        # what it was called with, so this can detect a regression in the dispatch/gather
        # wiring (previously this test called `run()` and asserted nothing).
        assert sorted(mock_plugin.gathered) == [2, 4, 6]
