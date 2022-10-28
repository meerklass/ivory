# Copyright 2013 ETHZ.ch Lukas Gamper <lukas.gamper@usystems.ch>
from ivy.exceptions.exceptions import InvalidLoopException
from ivy.utils.struct import WorkflowStruct

__all__ = ["ctx", "loop_ctx", "get_context_provider"]

global_ctx = None


def ctx():
    """
    Returns the current global namespace context.
    
    :return: reference to the context module
    
    """
    global global_ctx
    if (global_ctx is None):
        global_ctx = _create_ctx()

    return global_ctx


def register(loop):
    try:
        l = ctx()[loop]
        raise InvalidLoopException()
    except KeyError or AttributeError:
        ctx()[loop] = WorkflowStruct()


def loop_ctx(loop):
    return ctx()[loop]


def _create_ctx(**args):
    return get_context_provider().create_context(**args)


def _create_immutable_ctx(**args):
    return get_context_provider().create_immutable_context(**args)


def get_context_provider():
    from ivy.context_provider import DefaultContextProvider
    return DefaultContextProvider
