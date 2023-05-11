from abc import abstractmethod
from enum import Enum
from typing import Any, Generator

from joblib import Parallel, delayed

from ivory.plugin.abstract_plugin import AbstractPlugin


class AbstractParallelJoblibPlugin(AbstractPlugin):
    """ Abstract plugin for parallelised execution with the `joblib` library. """

    def __init__(self, n_jobs: int, verbose: int):
        """ Initialise with the number of workers `n_jobs` and the `joblib` verbosity `verbose`. """
        super().__init__()
        self.n_jobs = n_jobs
        self.verbose = verbose

    @abstractmethod
    def run_job(self, anything: Any) -> Any:
        """ Run one job on `anything` and return the result. """
        pass

    @abstractmethod
    def map(self, **kwargs) -> Generator[Any, None, None]:
        """ Map the workload, i.e. return a `Generator` of the individual arguments for `run_job`. """
        pass

    @abstractmethod
    def gather_and_set_result(self, *args, **kwargs):
        """ Gather the results, i.e. take the `list` of outputs of each job and combine. """
        pass

    def run(self, **kwargs):
        """ Run the plugin using `joblib`. """
        print(f'Starting parallel execution with {self.n_jobs} workers.')
        result_list = Parallel(n_jobs=self.n_jobs,
                               verbose=self.verbose)(delayed(self.run_job)(i) for i in self.map(**kwargs))
        print('Finished parallel execution, gathering results...')
        self.gather_and_set_result(result_list, **kwargs)
