# Plugins

A plugin is one processing step in a pipeline: a plain Python class that reads some inputs from the
shared context, does its work, and publishes some outputs back into the context. This page covers the
plugin contract, how plugins get discovered and wired together, and how to write a new one.

See [Architecture](architecture.md) first if you haven't already, for how the context and the execution
loop work.

## The `AbstractPlugin` contract

Every plugin subclasses `AbstractPlugin` (`ivory/plugin/abstract_plugin.py`):

```python
class AbstractPlugin(ABC):
    requirements: list[Requirement] = []

    def __init__(self):
        self._check_name()
        self.results: list[Result] = []
        self.set_requirements()

    @abstractmethod
    def run(self, **kwargs):
        """Run the plugin and store results."""

    @abstractmethod
    def set_requirements(self):
        """Set the requirements of `self`, i.e. the arguments of `self.run()`."""

    def set_result(self, result: Result):
        self.results.append(result)
```

You must implement two abstract methods:

- **`set_requirements(self)`** — sets `self.requirements` to a list of `Requirement` objects declaring
  what this plugin needs from the context (see below). Called automatically from `__init__`, so if your
  plugin defines its own `__init__`, it must call `super().__init__()`.
- **`run(self, **kwargs)`** — does the actual work. The engine calls this with the resolved requirement
  values as keyword arguments (see "How the engine wires plugins together" below). Publish outputs by
  calling `self.set_result(Result(...))` one or more times.

**Naming convention, enforced at runtime**: your class name must end in `"Plugin"` (e.g.
`GainCalibrationPlugin`). `AbstractPlugin._check_name()` raises a `ValueError` at construction time
otherwise. This isn't just style — it's also how the loader finds your class in its module (next
section).

## Discovery and loading

There's no registry, no entry points, no decorators. A plugin is referred to purely by its **dotted
module path as a string** in the config's `Pipeline.plugins` list, e.g.
`"museek.plugin.demo.demo_flip_plugin"`. `PluginFactory.create_instance()`
(`ivory/plugin/plugin_factory.py`) does the work:

1. `importlib.import_module(plugin_name)` — imports the module.
2. `_get_plugin_attribute(module)` scans `dir(module)` for exactly one attribute whose name ends in
   `"Plugin"` but doesn't start with `"Abstract"` or `"_"` — this excludes the base classes and private
   helpers. It also explicitly skips any matching attribute that is itself a `ConfigSection` instance
   (rather than a class), so a stray `FooPlugin = ConfigSection(...)` constant sitting in the module
   namespace won't be mistaken for the plugin class or trigger the "more than one valid Plugin" error.
   Zero matches or more than one match raises `ValueError`.
3. Instantiates that class with kwargs taken from `ctx.params[<PluginClassName>]` — i.e. the config's
   `ConfigSection` whose name exactly matches the plugin class name. If no such section exists, it's
   instantiated with no arguments.

**Convention this implies: one plugin class per module/file.** If a module has two `*Plugin` classes,
loading it raises `ValueError: ... contains more than one valid Plugin`.

Instantiation happens lazily, one plugin at a time, as `Loop.__next__` is iterated (see
[Architecture](architecture.md#loop-sequencing-and-repetition)) — not all up front.

## How the engine wires plugins together

Plugins don't call each other or pass return values directly. Instead:

- A plugin **declares what it needs** via `Requirement(location, variable)`
  (`ivory/utils/requirement.py`) — `location` is the context key to look up (conventionally a member of
  a project-defined `Enum`, e.g. MuSEEK's `ResultEnum`), and `variable` is the keyword-argument name
  `run()` will receive it as.
- A plugin **publishes what it produces** via `Result(location, result, allow_overwrite=True)`
  (`ivory/utils/result.py`), passed to `self.set_result(...)`.

Each time a plugin runs, `LoopRunner` (`ivory/utils/loop_runner.py`):

```python
@staticmethod
def _run_args(plugin, ctx):
    arguments = {}
    for requirement in plugin.requirements:
        if requirement.location not in ctx:
            raise ValueError(f"Requirement {requirement.location} of {plugin.name} is not met.")
        arguments[requirement.variable] = ctx[requirement.location].result
    return arguments
```

resolves every `Requirement` against `ctx`, calls `plugin.run(**arguments)`, then stores every
published `Result` back into `ctx` (`_store_to_ctx`), keyed by `result.location`.

**Ordering is implicit and only checked at runtime.** There is no dependency graph: if plugin B
declares a `Requirement` for a key that plugin A is supposed to publish, that only works if A appears
*earlier* in the `Pipeline.plugins` list and actually ran. If it didn't, you get a `ValueError` the
moment B tries to run — not before the pipeline starts. Keep your plugin list ordered correctly by
convention; nothing validates it for you.

**Sharp edge — silent partial drop on overwrite conflict.** The guard checks the flag on the *existing*
`Result` already stored in `ctx` under that key, not on the new `Result` being stored. If a key already
holds a non-`None` value and that stored `Result` has `allow_overwrite=False`, `LoopRunner._store_to_ctx`
prints `"Overwriting is not allowed. Discard result..."` and returns *immediately* — discarding not just
that one result, but any other `Result`s later in the same plugin's `self.results` list that hadn't been
stored yet. Setting `allow_overwrite=False` on the new result you're publishing does nothing to protect
it from being overwritten later; it's the previously-stored value's flag that matters. This is worth
knowing when debugging a plugin that seems to be missing some of its outputs.

## Parallel plugins

For embarrassingly-parallel work (e.g. per-file or per-frequency-channel processing), subclass
`AbstractParallelJoblibPlugin` (`ivory/plugin/abstract_parallel_joblib_plugin.py`) instead of
`AbstractPlugin` directly. It implements `run()` for you using `joblib.Parallel`, and asks you to
implement three methods instead:

```python
class AbstractParallelJoblibPlugin(AbstractPlugin):
    def __init__(self, n_jobs: int, verbose: int, prefer: str | None = None): ...

    @abstractmethod
    def map(self, **kwargs) -> Generator[Any, None, None]:
        """Yield the individual argument for each job."""

    @abstractmethod
    def run_job(self, anything: Any) -> Any:
        """Run one job and return its result."""

    @abstractmethod
    def gather_and_set_result(self, *args, **kwargs):
        """Combine the list of per-job results and call self.set_result(...)."""

    def run(self, **kwargs):
        result_list = Parallel(n_jobs=self.n_jobs, verbose=self.verbose, prefer=self.prefer)(
            delayed(self.run_job)(i) for i in self.map(**kwargs)
        )
        self.gather_and_set_result(result_list, **kwargs)
```

Note this only parallelizes *within* one plugin's `run()` call — the pipeline as a whole is still
strictly sequential across plugins (see [Known issues and limitations](known-issues-and-limitations.md)).

## Worked example: MuSEEK's demo plugins

MuSEEK ships a runnable demo pipeline (`museek museek.config.demo`) that's a good template to copy. The
config wires four plugins together (`museek/config/demo.py`):

```python
Pipeline = ConfigSection(
    plugins=[
        "museek.plugin.demo.demo_load_plugin",
        "museek.plugin.demo.demo_flip_plugin",
        "museek.plugin.demo.demo_plot_plugin",
        "museek.plugin.demo.demo_joblib_plugin",
    ],
)
DemoLoadPlugin = ConfigSection(
    url="https://.../horse.jpg", context_file_name="context.pickle", context_folder="./context",
)
DemoFlipPlugin = ConfigSection(do_flip_right_left=True, do_flip_top_bottom=True)
```

`DemoLoadPlugin` (`museek/plugin/demo/demo_load_plugin.py`) runs first, has no requirements (its
`set_requirements` is a no-op), downloads an image, and publishes it:

```python
class DemoLoadPlugin(AbstractPlugin):
    def __init__(self, url: str, context_file_name: str, context_folder: str):
        super().__init__()
        self.url = url
        ...

    def run(self, **kwargs):
        image = Image.open(BytesIO(requests.get(self.url).content))
        self.set_result(Result(location=DemoEnum.ASTRONAUT_RIDING_HORSE_IN_SPACE, result=image))
        ...  # also publishes CONTEXT_STORAGE_DIRECTORY / CONTEXT_FILE_NAME for checkpointing

    def set_requirements(self):
        pass
```

`DemoFlipPlugin` (`museek/plugin/demo/demo_flip_plugin.py`) runs next and consumes that image:

```python
class DemoFlipPlugin(AbstractPlugin):
    def set_requirements(self):
        self.requirements = [
            Requirement(location=DemoEnum.ASTRONAUT_RIDING_HORSE_IN_SPACE, variable="astronaut_image")
        ]

    def run(self, **kwargs):
        astronaut_image = kwargs["astronaut_image"]
        ...
        self.set_result(Result(location=DemoEnum.ASTRONAUT_RIDING_HORSE_IN_SPACE_FLIPPED, result=...))
```

This is the whole pattern: `DemoLoadPlugin` publishes under `DemoEnum.ASTRONAUT_RIDING_HORSE_IN_SPACE`,
`DemoFlipPlugin` requires that exact key and receives it as `astronaut_image`. For MuSEEK's
production-grade plugins with the same pattern at larger scale, see `museek/plugin/in_plugin.py`
(`InPlugin`, first pipeline stage, no requirements, publishes ~7 results under `ResultEnum`) and
`museek/plugin/out_plugin.py` (`OutPlugin`, requires `ResultEnum.BLOCK_NAME` and
`ResultEnum.OUTPUT_PATH`).

## Checklist for writing a new plugin

1. One new module, one class in it, named `<Something>Plugin`.
2. Don't import other plugin modules from within a plugin module (keeps the "exactly one `*Plugin` per
   module" discovery rule unambiguous).
3. If your plugin needs configuration, add a `ConfigSection` to your pipeline config, named *exactly*
   like your plugin class, and accept those as `__init__` keyword arguments (call `super().__init__()`
   first).
4. In `set_requirements()`, declare a `Requirement(location=..., variable=...)` for every value you
   need from an upstream plugin's published `Result`.
5. In `run(self, **kwargs)`, do the work, reading inputs from `kwargs[variable]`.
6. Call `self.set_result(Result(location=..., result=...))` for every output, choosing a `location` key
   downstream plugins will `Requirement`-reference.
7. Add your plugin's module path to `Pipeline.plugins` in the config, in the correct position relative
   to whatever publishes its requirements and whatever consumes its results.

Minimal skeleton:

```python
from ivory.plugin.abstract_plugin import AbstractPlugin
from ivory.utils.requirement import Requirement
from ivory.utils.result import Result

from myproject.enums.result_enum import ResultEnum


class MyNewPlugin(AbstractPlugin):
    def __init__(self, some_param: int):
        super().__init__()
        self.some_param = some_param

    def set_requirements(self):
        self.requirements = [
            Requirement(location=ResultEnum.SOME_UPSTREAM_KEY, variable="upstream_value")
        ]

    def run(self, **kwargs):
        result = kwargs["upstream_value"] * self.some_param
        self.set_result(Result(location=ResultEnum.MY_NEW_RESULT, result=result))
```

plus, in the pipeline config:

```python
MyNewPlugin = ConfigSection(some_param=3)
```

and `"myproject.plugin.my_new_plugin"` added to `Pipeline.plugins`.
