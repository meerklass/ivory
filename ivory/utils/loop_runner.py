import os
import pickle
import time
from typing import Any

import psutil

from ivory.enum.context_storage_enum import ContextStorageEnum
from ivory.loop import Loop
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.result import Result
from ivory.utils.struct import Struct
from ivory.utils.timing import SimpleTiming, ResourceTiming


class LoopRunner:
    """ Runs all plugins in a loop. """

    def __init__(self, loop: Loop):
        self.loop = loop

    def __call__(self, ctx: Struct) -> Struct:
        """ Runs all plugins in `self.loop` on `ctx` and returns `ctx` afterwards. """
        self.loop.ctx = ctx
        process = psutil.Process()
        
        for plugin in self.loop:
            start = time.time()
            print(f'\n--> Running {str(plugin)}...', flush=True)
            
            # Track memory and CPU before plugin execution
            try:
                process.cpu_percent(interval=None)  # Initialize CPU sampling
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            
            peak_memory_gb = 0.0
            peak_cpu_percent = 0.0
            
            # Run the plugin
            plugin.run(**self._run_args(plugin=plugin, ctx=ctx))
            
            # Capture peak resources after execution
            try:
                peak_memory_gb = process.memory_info().rss / (1024 ** 3)  # Convert to GB
                peak_cpu_percent = process.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # If we can't access psutil data, continue without it
                pass
            
            self._store_to_ctx(results=plugin.results, ctx=ctx)
            duration = time.time() - start
            
            # Store resource timing
            ctx.timings.append(
                ResourceTiming(
                    str(plugin),
                    duration,
                    peak_memory_gb=peak_memory_gb,
                    peak_cpu_percent=peak_cpu_percent
                )
            )
            self._store_ctx(ctx=ctx)

        self.loop.reset()
        self._print_timings(timings_list=ctx.timings)
        return ctx

    @staticmethod
    def _store_to_ctx(results: list[Result], ctx: Struct):
        """
        Store `results` to context `ctx`.
        Nothing is done if an entry is already stored under a `location` in `results` and overwriting is disabled.
        """
        for result in results:
            if result.location in ctx and (ctx[result.location] is not None
                                           and not ctx[result.location].allow_overwrite):
                print('Overwriting is not allowed. Discard result...')
                return
            ctx[result.location] = result

    @staticmethod
    def _store_ctx(ctx: Struct):
        """
        Store the `Struct` `ctx` to disc as a `pickle` using storage directory and file name contained in `ctx` itself.
        If either of the keys `ContextStorageEnum.DIRECTORY` or `ContextStorageEnum.FILE_NAME` are missing
        or pointing to `None` entries, nothing is done.
        Both `ctx[ContextStorageEnum.DIRECTORY]` and `ctx[ContextStorageEnum.FILE_NAME]`
        are set to `None` after storage.
        """
        try:
            context_storage_directory = ctx[ContextStorageEnum.DIRECTORY]
            context_file_name = ctx[ContextStorageEnum.FILE_NAME]
        except KeyError:
            return
        if context_storage_directory is not None and context_file_name is not None:
            if context_storage_directory.result is not None and context_file_name.result is not None:
                file_name = os.path.join(context_storage_directory.result, context_file_name.result)
                # replace with `None` to make sure the context is only stored once under this name
                ctx[ContextStorageEnum.DIRECTORY] = None
                ctx[ContextStorageEnum.FILE_NAME] = None
                with open(file_name, "wb") as out_file:
                    pickle.dump(ctx, out_file)

    @staticmethod
    def _run_args(plugin: AbstractPlugin, ctx: Struct) -> dict[str, Any]:
        """
        Looks up the values of `plugin.requirements` in `ctx` and returns them as a `dict`.
        :raise ValueError: if not all requirements can be found in `ctx`.
        """
        arguments = {}
        for requirement in plugin.requirements:
            if requirement.location not in ctx:
                raise ValueError(f'Requirement {requirement.location} of {plugin.name} is not met.')
            arguments[requirement.variable] = ctx[requirement.location].result
        return arguments

    @staticmethod
    def _print_timings(timings_list: list):
        """" Print a list of SimpleTiming or ResourceTiming objects nicely. """
        print('\n--> Timings:', flush=True)
        for timing in timings_list:
            print(timing)
