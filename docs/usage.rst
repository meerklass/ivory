========
Usage
========

To use ivory workflow engine in a project::

	from ivory.workflow_manager import WorkflowManager
	args = ["--size-x=100",
		"--size-y=100", 
		"ufig.config.random"]
        
	mgr = WorkflowManager(args)
	mgr.launch()
    
alternatively ivory can also be used from the command line::

	$ ivory --size-x=100 --size-y=100 ufig.config.random
	
	
A configuration can range form very simple to arbitrarily complex. 

In the simplest case the configuration file would look something like::

	from ivory.config import base_config

	plugins = ["test.plugin.simple_plugin",
           	"test.plugin.simple_plugin"
                ]

Importing basic functionality from `base_config` and defining a list of plugins.


A slightly more complex use case would look something like::

	from ivory.config import base_config
	from ivory.loop import Loop
	from ivory.utils.stop_criteria import RangeStopCriteria

	context_provider = "ivory.context_provider.PickleContextProvider"
	ctx_file_name = "ivory_cxt.dump"

	plugins = Loop(["test.plugin.simple_plugin",
			Loop(["test.plugin.simple_plugin",
			      "test.plugin.simple_plugin"], 
			      stop=RangeStopCriteria(max_iter=5)),
			"test.plugin.simple_plugin"], 
			stop=RangeStopCriteria(max_iter=2))

	a=1.5
	b=["omega", "lambda", "gamma"]
	c=None

Configures the 'PickleContextProvider' as context provider which ensures that 
the context is persisted to the file "ivory_ctx.dump" after every execution of a plugin

The list of plugins consists of two nested loops. Each having two plugins. The inner lopp will be 
executed 5 times and the outer loop twice.

Furthermore the config defines the attributes 'a', 'b' and c where 'a' is a float and 'b' a list of strings
and c is a NoneType. The type of c will automatically be inferred from the given value from the command line.

Calling this config and overriding the attributes from the command line would look something like this::

	$ ivory --a=1.75 --b=zeta,beta,gamma --c=False package.subpackage.module