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
    Return usage of the main ivory call and examples.
    """

    usage = """
    **Ivory Workflow Engine**
    
    Usage:
        ivory [--argument=value ...] <configuration>
    
    Configuration:
        The configuration can be specified in two ways:
        
        1. Python module path:
           - Example: ivory.config.workflow
           - Requires the module to be installed or in PYTHONPATH
        
        2. File path (new in v3.0.0):
           - Absolute path: /home/user/my_config.py
           - Relative path: ./my_config.py
           - Home directory: ~/my_config.py
           - Allows configs to be placed anywhere without installation
    
    Arguments:
        Command-line arguments override configuration file values.
        Format: --SectionName-parameter=value
        
        Note: Dashes '-' in argument names are converted to underscores '_'
    
    Examples:
        # Using module path
        ivory --SimplePlugin-value=100 mypackage.config.workflow
        
        # Using file paths
        ivory --param=value /home/user/config.py
        ivory ./workflow_config.py
        ivory ~/my_workflow.py
        
    Help:
        ivory --help    Show this help message
        ivory -h        Show this help message
    """
    print(usage)


if __name__ == "__main__":
    _main(*sys.argv[1:])
