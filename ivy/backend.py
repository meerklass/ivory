# IVY is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# IVY is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with IVY.  If not, see <http://www.gnu.org/licenses/>.


'''
Created on Mar 18, 2014

author: jakeret
'''
import time
from multiprocessing import Pool

from ivy.context import get_context_provider
from ivy.utils.timing import SimpleTiming
from ivy.utils.timing import TimingCollection


class SimpleMapPlugin:
    def __init__(self, ctx):
        self.ctx = ctx

    def get_workload(self):
        return [self.ctx]


class SequentialBackend:
    """
    Simple implementation of a backend executing the plugins in a sequential order
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop, map_plugin=None):
        if map_plugin is None: map_plugin = SimpleMapPlugin(self.ctx)

        return list(map(LoopWrapper(loop), map_plugin.get_workload()))


class MultiprocessingBackend:
    """
    Backend based on Python's multiprocessing. 
    Will instantiate a multiprocessing pool with ``ctx.params.cpu_count`` processes.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop, map_plugin):
        pool = Pool(self.ctx.params.cpu_count)
        try:
            ctx_list = pool.map(LoopWrapper(loop, True), map_plugin.get_workload())
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
            return view.map_sync(LoopWrapper(loop), map_plugin.get_workload())
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
            ctx_list = parallel(joblib.delayed(LoopWrapper(loop, True))(ctx)
                                for ctx in map_plugin.get_workload())
            timing_collection = TimingCollection(str(loop))
            for ctx in ctx_list:
                for timing in ctx.timings:
                    timing_collection.add_timing(timing)
            self.ctx.timings.append(timing_collection)
            return ctx_list


class LoopWrapper:
    """
    Callable wrapper for the loop execution
    """

    def __init__(self, loop, parallel=False):
        self.loop = loop
        self.parallel = parallel

    def __call__(self, ctx):
        #         print("working pid:%s" %(os.getpid()))
        if self.parallel:
            ctx.timings = []
        self.loop.ctx = ctx
        for plugin in self.loop:
            start = time.time()
            #             print("(%s, '%s'),"%(time.time(), plugin))
            plugin()
            #             time.sleep(5)
            ctx.timings.append(SimpleTiming(str(plugin), time.time() - start))

            get_context_provider().store_context()

        #         self.loop()
        self.loop.reset()
        return ctx


BACKEND_NAME_MAP = {"sequential": SequentialBackend,
                    "multiprocessing": MultiprocessingBackend,
                    "ipcluster": IpClusterBackend,
                    "joblib": JoblibBackend,
                    }


def create(ctx, force=None):
    '''
    Simple factory instantiating backends for the given name in ``ctx.params.backend``
    '''
    backend_name = ctx.params.backend if force is None else force
    return BACKEND_NAME_MAP[backend_name](ctx)
