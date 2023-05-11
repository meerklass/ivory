from typing import Generator, Any

from ivory.plugin.abstract_parallel_joblib_plugin import AbstractParallelJoblibPlugin


class MockPlugin(AbstractParallelJoblibPlugin):

    def run_job(self, anything: Any) -> Any:
        pass

    def map(self, **kwargs) -> Generator[Any, None, None]:
        return [1]

    def gather_and_set_result(self, *args, **kwargs):
        pass

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
