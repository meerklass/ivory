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

How Context and Data Passing Works
-----------------------------------

Ivory uses an **in-memory context** to pass data between plugins efficiently. This is a key
architectural feature that enables fast, flexible workflows.

In-Memory Context
~~~~~~~~~~~~~~~~~

The context is a shared, mutable dictionary-like object that exists in memory throughout the
workflow execution. All plugins access the same context instance::

	from ivory.context import ctx
	
	# In your plugin's run() method
	def run(self, **kwargs):
	    # Store results in context
	    self.set_result(Result(location=MyEnum.OUTPUT, result=my_data))

When a plugin stores results using ``set_result()``, the data is immediately available to
subsequent plugins through the context. This is **orders of magnitude faster** than writing
to disk between each plugin execution.

**Key characteristics:**

* **Fast**: No serialization or I/O overhead - just Python object references
* **Flexible**: Any Python object can be stored in context
* **Sequential**: Plugins execute in order, each seeing results from previous plugins
* **Persistent in memory**: Context lives for the entire workflow execution

Data Flow Between Plugins
~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's how data flows through a typical workflow:

1. **Plugin A** runs and stores output in context::

	self.set_result(Result(location=DataEnum.PROCESSED_DATA, result=processed_array))

2. **Plugin B** declares it needs this data via requirements::

	from ivory.utils.requirement import Requirement
	
	def set_requirements(self):
	    self.requirements = [
	        Requirement(variable="data", location=DataEnum.PROCESSED_DATA)
	    ]

3. **Plugin B** receives the data automatically in its ``run()`` method::

	def run(self, data):
	    # 'data' is the processed_array from Plugin A
	    result = self.process(data)

The workflow engine automatically:

* Looks up requirements in the context
* Passes them as keyword arguments to ``run()``
* Validates all requirements are met before execution

Performance Benefits
~~~~~~~~~~~~~~~~~~~~

Compared to file-based approaches, in-memory context passing is:

* **1000-100,000x faster** for typical data sizes
* **Zero disk I/O** during workflow execution
* **No serialization overhead** (pickle/JSON/etc.)
* **Lower memory footprint** (no duplicate copies on disk)

This makes ivory ideal for:

* Iterative processing pipelines
* Real-time data processing
* Large-scale scientific workflows
* Rapid prototyping and testing

Context Persistence
-------------------

While the primary data flow is in-memory, ivory also supports **optional disk persistence**
for checkpointing and recovery.

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