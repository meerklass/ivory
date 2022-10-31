# register custom reduce method for type MethodType
import copyreg
import types

from ivory import context
from ivory.workflow_manager import WorkflowManager


def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))


copyreg.pickle(types.MethodType, reduce_method)


def execute(args):
    """
    Runs a workflow for the given arguments.
    :param args: list of arguments which should be passed to ivory. The last argument has to be the config
    
    :returns: the global_ctx
    """
    mgr = WorkflowManager(args)
    mgr.launch()
    return context.global_ctx
