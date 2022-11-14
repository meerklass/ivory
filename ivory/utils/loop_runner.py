import time
from struct import Struct
from typing import Any

from ivory.context import get_context_provider
from ivory.loop import Loop
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.result import Result
from ivory.utils.timing import SimpleTiming


class LoopRunner:
    """ Runs all plugins in a loop. """

    def __init__(self, loop: Loop, parallel: bool = False):
        self.loop = loop
        self.parallel = parallel

    def __call__(self, ctx: Struct) -> Struct:
        """ Runs all plugins in `self.loop` on `ctx` and returns `ctx` afterwards. """
        if self.parallel:
            ctx.timings = []
        self.loop.ctx = ctx
        for plugin in self.loop:
            start = time.time()
            print(f'\n--> Running {str(plugin)}...')
            plugin.run(**self._run_args(plugin=plugin, ctx=ctx))
            self._store_to_ctx(results=plugin.results, ctx=ctx)
            ctx.timings.append(SimpleTiming(str(plugin), time.time() - start))

            get_context_provider().store_context()

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
            if result.location in ctx and not ctx[result.location].allow_overwrite:
                print('Overwriting is not allowed. Discard result...')
                return
            ctx[result.location] = result

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
    def _print_timings(timings_list: list[SimpleTiming]):
        """" Print a `list` of `SimpleTiming`s nicely. """
        print('\n--> Timings:')
        for timing in timings_list:
            print(timing)
