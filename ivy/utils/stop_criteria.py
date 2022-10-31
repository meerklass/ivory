from abc import abstractmethod, ABC

from ivy.context import loop_ctx
from ivy.exceptions.exceptions import InvalidAttributeException
from ivy.utils.struct import WorkflowState


class AbstractStopCriteria(ABC):
    """
    Abstract implementation of stopping criteria
    """

    parent = None

    @abstractmethod
    def is_stop(self):
        pass


class RangeStopCriteria(AbstractStopCriteria):
    """
    Stopping criteria which stops after `max_iter` iterations
    """

    def __init__(self, max_iter):
        if max_iter < 1:
            raise InvalidAttributeException("Minimum iteration is 1")

        self.max_iter = max_iter

    def is_stop(self):
        ctx = loop_ctx(self.parent)
        if (ctx.iter >= self.max_iter):
            ctx.stop()

        return ctx.state == WorkflowState.STOP


class SimpleStopCriteria(RangeStopCriteria):
    """
    Simple implementation of a stopping criteria. Stops after `one` iteration
    """

    def __init__(self):
        super(SimpleStopCriteria, self).__init__(max_iter=1)
