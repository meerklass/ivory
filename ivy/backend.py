import time
from multiprocessing import Pool
from typing import Optional

from ivy.context import get_context_provider
from ivy.loop import Loop
from ivy.plugin.abstract_plugin import AbstractPlugin
from ivy.utils.struct import Struct, ImmutableStruct
from ivy.utils.timing import SimpleTiming
from ivy.utils.timing import TimingCollection


class SimpleMapPlugin(AbstractPlugin):
    """ Simplest implementation of a plugin that returns its context when run. """

    def run(self) -> list[ImmutableStruct]:
        return [self.ctx]


class SequentialBackend:
    """
    Simple implementation of a backend executing the plugins in a sequential order
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop: Loop, map_plugin: Optional[AbstractPlugin] = None) -> list[Struct]:
        if map_plugin is None:
            map_plugin = SimpleMapPlugin(self.ctx)
        return list(map(CallableLoop(loop), map_plugin.run()))


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
            ctx_list = pool.map(CallableLoop(loop, True), map_plugin.run())
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
            return view.map_sync(CallableLoop(loop), map_plugin.run())
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
            ctx_list = parallel(joblib.delayed(CallableLoop(loop, True))(ctx)
                                for ctx in map_plugin.run())
            timing_collection = TimingCollection(str(loop))
            for ctx in ctx_list:
                for timing in ctx.timings:
                    timing_collection.add_timing(timing)
            self.ctx.timings.append(timing_collection)
            return ctx_list


class CallableLoop:
    """
    Callable wrapper for the loop execution
    """

    def __init__(self, loop, parallel=False):
        self.loop = loop
        self.parallel = parallel

    def __call__(self, ctx):
        if self.parallel:
            ctx.timings = []
        self.loop.ctx = ctx
        for plugin in self.loop:
            start = time.time()
            print(f'\n--> Running {str(plugin)}...')
            plugin.run()
            ctx.timings.append(SimpleTiming(str(plugin), time.time() - start))

            get_context_provider().store_context()

        self.loop.reset()
        print_timings(timings_list=ctx.timings)
        return ctx


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


def print_timings(timings_list: list[SimpleTiming]):
    """" Print a `list` of `SimpleTiming`s nicely. """
    print('\n--> Timings:')
    for timing in timings_list:
        print(timing)
