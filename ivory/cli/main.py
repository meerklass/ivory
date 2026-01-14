import sys

from ivory.workflow_manager import WorkflowManager


def run():
    """
    Called by the entry point script. Delegating call to main()
    """
    _main(*sys.argv[1:])


def _main(*argv):
    if (argv is None or len(argv) < 1):
        _usage()
        return
    argv = list(argv)
    # Handle help flag before passing to WorkflowManager
    if '--help' in argv or '-h' in argv:
        _usage()
        return
    mgr = WorkflowManager(argv)
    mgr.launch()


def _usage():
    """
    Return usage of the main ivory call and an example.
    """

    usage = """
    **ivory workflow engine**
    
    Usage:
    ivory [arguments] configuration
    
    The configuration can be either:
    - A Python module path (e.g., ivory.config.workflow)
    - A file path (e.g., /path/to/config.py or ./config.py)
    
    Only arguments already preconfigured in the given configuration will be accepted.
    Note: Dashed '-' will be converted into underlines '_' for all the arguments
    
    Examples:
    - ivory --size-x=100 --size-y=100 ivory.config.random
    - ivory --size-x=100 --size-y=100 /home/user/my_config.py
    - ivory ./workflow_config.py
    """
    print(usage)


if __name__ == "__main__":
    _main(*sys.argv[1:])
