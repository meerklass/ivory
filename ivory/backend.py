from ivory.loop import Loop
from ivory.utils.loop_runner import LoopRunner
from ivory.utils.struct import Struct


class SequentialBackend:
    """
    Simple implementation of a backend executing the plugins in a sequential order
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def run(self, loop: Loop) -> list[Struct]:
        """ Run the sequential backend. """
        return [LoopRunner(loop)(self.ctx)]
