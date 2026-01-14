============
Installation
============

Requirements
------------

Ivory requires:

* Python 3.10 or higher (tested with Python 3.12)
* numpy >= 2.0.0
* pytest >= 8.0.0
* joblib
* ipyparallel

Installation from Source
-------------------------

The project is hosted on GitHub. Get a copy by running::

	$ git clone https://github.com/meerklass/ivory.git
	$ cd ivory

Install using pip::

	$ pip install .

Or for development mode (editable install)::

	$ pip install -e .

This will automatically install all required dependencies.

Quick Start
-----------

After installation, verify it works::

	$ ivory --help

You should see the Ivory workflow engine help message.

For a simple test, create a config file ``test_config.py``::

	from ivory.utils.config_section import ConfigSection
	
	Pipeline = ConfigSection(
	    plugins=["test.plugin.simple_plugin"],
	)

Then run::

	$ ivory ./test_config.py
