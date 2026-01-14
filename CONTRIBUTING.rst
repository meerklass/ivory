============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given. 

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Implement Features
~~~~~~~~~~~~~~~~~~

Write Documentation
~~~~~~~~~~~~~~~~~~~

Ivory workflow engine could always use more documentation, whether as part of the
official Ivory workflow engine docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.10, 3.11, and 3.12.
   GitHub Actions will automatically run tests for all supported Python versions.


Development Setup
-----------------

1. Fork the repository and clone your fork
2. Create a virtual environment and install dependencies::

    $ python -m venv venv
    $ source venv/bin/activate  # On Windows: venv\Scripts\activate
    $ pip install -r requirements.txt

3. Run the test suite::

    $ pytest

4. Build the documentation::

    $ cd docs
    $ pip install -r requirements.txt
    $ make html

Tips
----

To run a subset of tests::

    $ pytest test/test_ivory.py

To run tests with coverage::

    $ pytest --cov=ivory --cov-report=html

Continuous Integration
----------------------

GitHub Actions automatically runs on every pull request:

- **Tests**: Runs the test suite on Python 3.10, 3.11, and 3.12
- **Linting**: Checks code style with flake8
- **Documentation**: Verifies that documentation builds successfully

All checks must pass before a pull request can be merged.

Documentation
-------------

Documentation is hosted at https://ivory.readthedocs.io/

For information about setting up Read the Docs access, see ``docs/READTHEDOCS_SETUP.md``