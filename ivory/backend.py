from multiprocessing import Pool

from ivory.loop import Loop
from ivory.utils.loop_runner import LoopRunner
from ivory.utils.struct import Struct
from ivory.utils.timing import TimingCollection


class SequentialBackend:
    """
    Simple implementation of a backend executing the plugins in a sequential order
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop: Loop) -> list[Struct]:
        return [LoopRunner(loop)(self.ctx)]


class MultiprocessingBackend:
    """
    Backend based on Python's multiprocessing. 
    Will instantiate a multiprocessing pool with ``ctx.params.cpu_count`` processes.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop, map_plugin):
        pool = Pool(self.ctx.params.Pipeline.cpu_count)
        try:
            ctx_list = pool.map(LoopRunner(loop, True), map_plugin.run())
            timing_collection = TimingCollection(str(loop))
            for ctx in ctx_list:
                for timing in ctx.timings:
                    timing_collection.add_timing(timing)
            self.ctx.timings.append(timing_collection)
            return ctx_list
        finally:
            pool.close()


class IpClusterBackend:
    """
    Backend based on IPython cluster. 
    Will distribute the workload among the available engines.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def run(loop, map_plugin):
        import ipyparallel

        client = ipyparallel.Client()
        view = client.load_balanced_view()
        try:
            return view.map_sync(LoopRunner(loop), map_plugin.run())
        finally:
            pass


#             view.close()

class JoblibBackend:
    """
    Backend based on the joblib package 
    Will instantiate a multiprocessing pool with ``ctx.params.cpu_count`` processes.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop, map_plugin):
        import joblib
        with joblib.Parallel(n_jobs=self.ctx.params.cpu_count) as parallel:
            ctx_list = parallel(joblib.delayed(LoopRunner(loop, True))(ctx)
                                for ctx in map_plugin.run())
            timing_collection = TimingCollection(str(loop))
            for ctx in ctx_list:
                for timing in ctx.timings:
                    timing_collection.add_timing(timing)
            self.ctx.timings.append(timing_collection)
            return ctx_list


BACKEND_NAME_MAP = {"sequential": SequentialBackend,
                    "multiprocessing": MultiprocessingBackend,
                    "ipcluster": IpClusterBackend,
                    "joblib": JoblibBackend}


def create(ctx, force=None):
    """
    Simple factory instantiating backends for the given name in ``ctx.params.backend``
    """
    backend_name = ctx.params.Pipeline.backend if force is None else force
    return BACKEND_NAME_MAP[backend_name](ctx)
