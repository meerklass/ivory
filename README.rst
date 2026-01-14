=============================
Ivory workflow engine
=============================

.. image:: https://github.com/meerklass/ivory/workflows/CI/badge.svg
    :target: https://github.com/meerklass/ivory/actions
    :alt: CI Status

.. image:: https://readthedocs.org/projects/ivory/badge/?version=latest
    :target: https://ivory.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/ivory.svg
    :target: https://pypi.org/project/ivory/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/ivory.svg
    :target: https://pypi.org/project/ivory/
    :alt: Python versions

Simple and flexible workflow engine

This **ivory** package has been developed at the `Centre for Radio Cosmology` at UWC and at the `Jodrell Bank Centre for Astrophysics` at `UoM`.
It is based on the original `python 2.7` **ivy** package developed at ETH Zurich in the `Software Lab of the Cosmology Research Group <http://www.cosmology.ethz.ch/research/software-lab.html>`_ of the `ETH Institute of Astronomy <http://www.astro.ethz.ch>`_.

The development is coordinated on `GitHub <https://github.com/meerklass/ivory>`_ and contributions are welcome.

**Documentation:** https://ivory.readthedocs.io/


Features
--------

* Helps to design and execute workflows
* Clear and flexible API
* Supports very simple to arbitrarily complex workflows
* **Fast in-memory context passing** between plugins (1000x faster than disk I/O)
* Optional context persistence for checkpointing and recovery
* Flexible configuration from files or Python modules

Installation
------------

Install ivory using pip:

.. code-block:: bash

    pip install .

from within the `ivory` root directory.

For development mode:

.. code-block:: bash

    pip install -e .

Usage
-----

Ivory can be run from the command line:

.. code-block:: bash

    ivory [arguments] configuration

The configuration can be specified in two ways:

1. **Python module path** (traditional):

   .. code-block:: bash

       ivory --param=value mypackage.config.workflow

2. **File path** (new in v3.0.0):

   .. code-block:: bash

       ivory --param=value /path/to/config.py
       ivory --param=value ./config.py
       ivory --param=value ~/my_workflow_config.py

This allows you to place configuration files anywhere without requiring them to be part of an installed Python package.

Architecture
------------

Ivory uses an **in-memory context** to pass data between plugins:

* **High Performance**: Data flows through memory (Python object references), not disk I/O
* **Simple**: Plugins store results in context; subsequent plugins read from it
* **Automatic**: Workflow engine handles data passing based on plugin requirements
* **Optional Persistence**: Context can be saved to disk for checkpointing when needed

This design makes ivory ideal for iterative processing pipelines and large-scale scientific workflows where performance matters.

See the `documentation <http://ivory.readthedocs.io/>`_ for detailed usage and examples.
