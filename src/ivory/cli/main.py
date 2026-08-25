import sys

import ivory
from ivory.workflow_manager import WorkflowManager


def run():
    """
    Called by the entry point script. Delegating call to main()
    """
    _main(*sys.argv[1:])


def _main(*argv):
    if argv is None or len(argv) < 1:
        _usage()
        return
    argv = list(argv)
    # Handle help/version flags before passing to WorkflowManager
    if "--help" in argv or "-h" in argv:
        _usage()
        return
    if "--version" in argv or "-V" in argv:
        _version()
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

    The configuration can be either a dotted module path (e.g. myproject.config.module) or a
    filesystem path to a .py file (absolute, relative, or ~-expanded), which does not need to
    be part of an installed package.

    Only arguments already preconfigured in the given configuration will be accepted.
    Note: Dashed '-' will be converted into underlines '_' for all the arguments

    Other options:
    -h, --help       show this help message and exit
    -V, --version    show the installed ivory version and exit

    example:
    - ivory --size-x=100 --size-y=100 myproject.config.module
    - ivory --size-x=100 --size-y=100 ./my_config.py
    """
    print(usage)


def _version():
    """
    Print the installed ivory version.
    """
    print(ivory.__version__)


if __name__ == "__main__":
    _main(*sys.argv[1:])
