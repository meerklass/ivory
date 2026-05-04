# Ivory workflow engine

Simple and flexible workflow engine

This **ivory** package has been developed at the [Centre for Radio Cosmology](http://www.astro.ethz.ch) at UWC and at the [Jodrell Bank Centre for Astrophysics](http://www.astro.ethz.ch) at UoM.

It is based on the original Python 2.7 **ivy** package developed at ETH Zurich in the [Software Lab of the Cosmology Research Group](http://www.cosmology.ethz.ch/research/software-lab.html) of the [ETH Institute of Astronomy](http://www.astro.ethz.ch).

The development is coordinated on [GitHub](https://github.com/meerklass/ivory) and contributions are welcome.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Credits](#credits)

## Installation

The project is hosted on GitHub. Get a copy by running:

```bash
pip install git+https://github.com/meerklass/ivory.git
```

or clone and build.

```bash
git clone https://github.com/meerklass/ivory.git
cd ivory
pip install .
```

## Usage

Ivory can be run from the command line or as a Python module.

### Command Line

```bash
ivory [arguments] configuration
```

### Python Module

```python
from ivory.workflow_manager import WorkflowManager

args = ["--size-x=100", "--size-y=100", "ufig.config.random"]
mgr = WorkflowManager(args)
mgr.launch()
```

### Configuration

A configuration can range from very simple to arbitrarily complex.

#### Simple Configuration

In the simplest case the configuration file would look something like:

```python
from ivory.config import base_config

plugins = [
    "test.plugin.simple_plugin",
    "test.plugin.simple_plugin"
]
```

Importing basic functionality from `base_config` and defining a list of plugins.

#### Complex Configuration

A slightly more complex use case would look something like:

```python
from ivory.config import base_config
from ivory.loop import Loop
from ivory.utils.stop_criteria import RangeStopCriteria

context_provider = "ivory.context_provider.PickleContextProvider"
ctx_file_name = "ivory_cxt.dump"

plugins = Loop(
    [
        "test.plugin.simple_plugin",
        Loop(
            [
                "test.plugin.simple_plugin",
                "test.plugin.simple_plugin"
            ],
            stop=RangeStopCriteria(max_iter=5)
        ),
        "test.plugin.simple_plugin"
    ],
    stop=RangeStopCriteria(max_iter=2)
)

a = 1.5
b = ["omega", "lambda", "gamma"]
c = None
```

This configuration:

- Configures the `PickleContextProvider` as context provider which ensures that the context is persisted to the file `ivory_ctx.dump` after every execution of a plugin
- Defines a list of plugins consisting of two nested loops, each having two plugins. The inner loop will be executed 5 times and the outer loop twice
- Defines the attributes `a`, `b` and `c` where `a` is a float, `b` is a list of strings, and `c` is a NoneType
- The type of `c` will automatically be inferred from the given value from the command line

#### Command Line Usage

Calling this config and overriding the attributes from the command line:

```bash
ivory --a=1.75 --b=zeta,beta,gamma --c=False package.subpackage.module
```

## Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

### Types of Contributions

#### Report Bugs

If you are reporting a bug, please include:

- Your operating system name and version
- Any details about your local setup that might be helpful in troubleshooting
- Detailed steps to reproduce the bug

#### Submit Feedback

If you are proposing a feature:

- Explain in detail how it would work
- Keep the scope as narrow as possible, to make it easier to implement
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

### Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md
3. The pull request should work for Python 3.10 and for PyPy. Make sure that the tests pass for all supported Python versions

## Credits

### Development lead

- Piyanat Kittiwisit <piyanat.kittiwisit@gmail.com>
- Amadeus Wild <amadeus.wild@manchester.ac.uk> (former)

### Development lead of original package ivy

- Joel Akeret

### Contributors

- Lukas Gamper <gamperl@gmail.com>
