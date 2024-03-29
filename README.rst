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

Run
--------
The dependencies are listed in `ivory/requirements.txt` and can either be installed with

.. code-block:: bash

    pip install -r ivory/requirements.txt`


or using

.. code-block:: bash

    pip install .

from within the `ivory` root directory. `Ivory` is run from the main script `ivory/cli/main.py` and the usage is

.. code-block:: bash

    python ivory/cli/main.py [arguments] configuration
