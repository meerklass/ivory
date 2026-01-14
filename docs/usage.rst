========
Usage
========

Command Line Usage
------------------

Ivory can be used from the command line with either module paths or file paths:

**Using a Python module path (traditional)**::

	$ ivory --size-x=100 --size-y=100 mypackage.config.workflow

**Using a file path (new in v3.0.0)**::

	$ ivory --size-x=100 --size-y=100 /path/to/config.py
	$ ivory --param=value ./my_config.py
	$ ivory ~/workflow_config.py

The file path approach allows you to place configuration files anywhere on your filesystem
without requiring them to be part of an installed Python package.

Programmatic Usage
------------------

To use ivory workflow engine in a project::

	from ivory.workflow_manager import WorkflowManager
	
	# Using module path
	args = ["--size-x=100", "--size-y=100", "mypackage.config.workflow"]
	mgr = WorkflowManager(args)
	mgr.launch()
	
	# Using file path
	args = ["--size-x=100", "--size-y=100", "/path/to/config.py"]
	mgr = WorkflowManager(args)
	mgr.launch()
	

Configuration Files
-------------------

A configuration can range from very simple to arbitrarily complex.

In the simplest case, the configuration file would look something like::

	from ivory.utils.config_section import ConfigSection

	Pipeline = ConfigSection(
	    plugins=[
	        "test.plugin.simple_plugin",
	        "test.plugin.simple_plugin"
	    ],
	)

This defines a Pipeline section with a list of plugins to execute.

Each plugin can have its own configuration section::

	SimplePlugin = ConfigSection(
	    parameter1="value1",
	    parameter2=100,
	)


A more complex use case with nested loops would look like::

	from ivory.utils.config_section import ConfigSection
	from ivory.loop import Loop
	from ivory.utils.stop_criteria import RangeStopCriteria

	Pipeline = ConfigSection(
	    plugins=Loop([
	        "test.plugin.simple_plugin",
	        Loop([
	            "test.plugin.simple_plugin",
	            "test.plugin.simple_plugin"
	        ], stop=RangeStopCriteria(max_iter=5)),
	        "test.plugin.simple_plugin"
	    ], stop=RangeStopCriteria(max_iter=2)),
	)

	SimplePlugin = ConfigSection(
	    a=1.5,
	    b=["omega", "lambda", "gamma"],
	    c=None,
	)

This creates nested loops where the inner loop executes 5 times and the outer loop twice.

The SimplePlugin configuration defines parameters 'a', 'b', and 'c'. Parameter types are
automatically inferred from values. These can be overridden from the command line::

	$ ivory --SimplePlugin-a=1.75 --SimplePlugin-b=zeta,beta,gamma --SimplePlugin-c=False /path/to/config.py

Note that command-line arguments use the format ``--SectionName-parameter=value``.

Context Persistence
-------------------

To save the workflow context after specific plugins, use the ``store_context_to_disc`` method
in your plugin's ``run()`` method::

	self.store_context_to_disc(
	    context_directory='./results/',
	    context_file_name='workflow_checkpoint.pickle'
	)

To resume from a saved context, specify it in your Pipeline configuration::

	Pipeline = ConfigSection(
	    plugins=[...],
	    context='./results/workflow_checkpoint.pickle',
	)