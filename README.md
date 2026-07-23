# Ivory workflow engine

Simple and flexible workflow engine

This **ivory** package has been developed at the [Centre for Radio Cosmology](http://www.astro.ethz.ch) at UWC and at the [Jodrell Bank Centre for Astrophysics](http://www.astro.ethz.ch) at UoM.

It is based on the original Python 2.7 **ivy** package developed at ETH Zurich in the [Software Lab of the Cosmology Research Group](http://www.cosmology.ethz.ch/research/software-lab.html) of the [ETH Institute of Astronomy](http://www.astro.ethz.ch).

The development is coordinated on [GitHub](https://github.com/meerklass/ivory) and contributions are welcome.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
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

Downstream projects can also wrap `ivory.cli.main.run()` in their own console script — e.g. MuSEEK's
`museek` command delegates straight into it.

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
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=[
        "test.plugin.simple_plugin",
        "test.plugin.simple_plugin"
    ]
)
```

Every configuration must define a `Pipeline` section (a `ConfigSection`) with a `plugins` key, listing
the plugins to run in order by their dotted module path.

#### Complex Configuration

A slightly more complex use case would look something like:

```python
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.stop_criteria import RangeStopCriteria

Pipeline = ConfigSection(
    plugins=Loop(
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
)

SimplePlugin = ConfigSection(a=1.5, b=["omega", "lambda", "gamma"], c=None)
```

This configuration:

- Defines a list of plugins consisting of two nested loops, each having two plugins. The inner loop will be executed 5 times and the outer loop twice
- Defines a `SimplePlugin` section with attributes `a`, `b` and `c`, passed to `SimplePlugin.__init__()` as keyword arguments, where `a` is a float, `b` is a list of strings, and `c` is a NoneType
- The type of an overridden attribute is automatically inferred from the type of its default value in the config

A pipeline can also be resumed from a previously saved run by setting `Pipeline.context` to the path of
a context file saved via a plugin's `store_context_to_disc()` call — or by passing
`--Pipeline-context=<path>` on the command line without touching the config file at all, since `context`
defaults to `None` and is always overridable. See the [internal documentation](#documentation) for
details on checkpointing.

#### Command Line Usage

Calling this config and overriding `SimplePlugin`'s attributes from the command line (section and
parameter name joined with a dash; dashes in the parameter name itself become underscores):

```bash
ivory --SimplePlugin-a=1.75 --SimplePlugin-b=zeta,beta,gamma --SimplePlugin-c=False package.subpackage.module
```

## Documentation

For a deeper look at how Ivory works internally — the execution model, the plugin contract, the
configuration format, and known issues/limitations — see the docs in [`docs/`](docs/README.md):

- [Architecture](docs/architecture.md) — how a pipeline run executes end to end, and how the context/state model works
- [Plugins](docs/plugins.md) — the plugin contract, discovery/loading, and how to write a new plugin
- [Configuration](docs/configuration.md) — the config file format, CLI overrides, and worked examples
- [Known issues and limitations](docs/known-issues-and-limitations.md) — structural design limitations worth knowing up front

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
