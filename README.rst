=============================
Ivory workflow engine
=============================

Simple and flexible workflow engine

This **ivory** package has been developed at the `Centre for Radio Cosmology` at UWC and at the `Jodrell Bank Centre for Astrophysics` at `UoM`.
It is based on the original `python 2.7` **ivy** package developed at ETH Zurich in the `Software Lab of the Cosmology Research Group <http://www.cosmology.ethz.ch/research/software-lab.html>`_ of the `ETH Institute of Astronomy <http://www.astro.ethz.ch>`_.

The development is coordinated on `GitHub <https://github.com/meerklass/ivory>`_ and contributions are welcome. The documentation of **ivory** is not yet available at `readthedocs.org <http://ivory.readthedocs.io/>`_ .


Features
--------

* Helps to design and execute workflows
* Clear and flexible API
* Supports very simple to arbitrarily complex workflows

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
