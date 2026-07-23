# Configuration

## Config files are plain Python modules

Ivory configs are **not** YAML/TOML/JSON — they're ordinary Python modules, imported by dotted path
(e.g. `museek.config.demo`, passed as the last positional CLI argument). A config module defines
module-level variables whose names start with an uppercase letter, holding instances of
`ivory.utils.config_section.ConfigSection` — a plain `dict` subclass. `WorkflowManager` picks these up
automatically by scanning `dir(module)` for capitalized, `ConfigSection`-typed attributes
(`WorkflowManager._get_config_section`).

**Required section**: `Pipeline`, with a `plugins` key — either a list of dotted plugin-module strings,
or a pre-built `ivory.loop.Loop` (see [Architecture](architecture.md#loop-sequencing-and-repetition)).
Missing either raises `ValueError`/`InvalidAttributeException` at startup.

**Optional key**: `Pipeline.context` — a path to a pickle file to resume from (see
[Architecture](architecture.md#checkpointing-saving-and-resuming-context)).

**Every other section** must be named identically to a plugin's class name, and its keys become that
plugin's `__init__` keyword arguments (via `PluginFactory.create_instance`, see
[Plugins](plugins.md#discovery-and-loading)).

## Minimal example

```python
# test/config/workflow_config_simple.py
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=["test.plugin.simple_plugin", "test.plugin.simple_plugin"]
)
```

Runs the same plugin module twice, back to back, with no extra configuration for it.

## Nested loops (repetition)

```python
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection
from ivory.utils.stop_criteria import RangeStopCriteria

Pipeline = ConfigSection(
    plugins=Loop(
        [
            "myproject.plugin.pre_plugin",
            Loop(
                ["myproject.plugin.iterate_plugin", "myproject.plugin.check_plugin"],
                stop=RangeStopCriteria(max_iter=5),
            ),
            "myproject.plugin.post_plugin",
        ],
        stop=RangeStopCriteria(max_iter=2),
    )
)
```

This runs `pre_plugin`, then the inner loop (`iterate_plugin` → `check_plugin`, 5 times), then
`post_plugin` — and repeats that whole sequence twice, because the outer `Loop` also has
`stop=RangeStopCriteria(max_iter=2)`.

## Real end-to-end example: MuSEEK's demo config

```python
# museek/config/demo.py
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=[
        "museek.plugin.demo.demo_load_plugin",
        "museek.plugin.demo.demo_flip_plugin",
        "museek.plugin.demo.demo_plot_plugin",
        "museek.plugin.demo.demo_joblib_plugin",
    ],
)
DemoLoadPlugin = ConfigSection(
    url="https://cdn.openai.com/dall-e-2/demos/text2im/astronaut/horse/photo/9.jpg",
    context_file_name="context.pickle",
    context_folder="./context",
)
DemoPlotPlugin = ConfigSection(do_show=False, do_save=True)
DemoFlipPlugin = ConfigSection(do_flip_right_left=True, do_flip_top_bottom=True)
DemoJoblibPlugin = ConfigSection(n_iter=10, n_jobs=2, verbose=0)
```

Run it with `museek museek.config.demo` (MuSEEK wraps `ivory.cli.main.run()` — see
[Architecture](architecture.md#entry-points)).

## Checkpoint/resume example

```python
# test/config/workflow_config_store_context.py
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(plugins=Loop(["test.plugin.simple_plugin"]))
SimplePlugin = ConfigSection(value="store")   # triggers store_context_to_disc(...) in the plugin
```

```python
# test/config/workflow_config_load_context.py
import os
from ivory.loop import Loop
from ivory.utils.config_section import ConfigSection

Pipeline = ConfigSection(
    plugins=Loop(["test.plugin.simple_plugin"]),
    context=os.path.join(os.getcwd(), "cache/simple_plugin.pickle"),
)
SimplePlugin = ConfigSection(value="load")
```

## CLI overrides

Any config value can be overridden from the shell with `--<SectionName>-<param>=<value>` (dashes in
the parameter name become underscores). Note there is currently no packaged `ivory` console script (see
[Known issues and limitations](known-issues-and-limitations.md)), so invoke via `python -m
ivory.cli.main` unless a downstream project provides its own wrapper, as MuSEEK's `museek` command does:

```bash
python -m ivory.cli.main --SimplePlugin-a=1.75 --SimplePlugin-b=zeta,beta,gamma --SimplePlugin-c=False package.subpackage.module
museek --InPlugin-block-name=1675632179 museek.config.process_uhf_band
```

Only parameters already present in the target config's sections can be overridden this way —
`get_all_longopts` (`ivory/utils/opt_helper.py`) builds the accepted `getopt` longopts strictly from the
keys already defined in the config's `ConfigSection`s, so passing an override for a key that doesn't
exist in the config raises a `getopt` error rather than adding a new key.

The override's type is inferred from the *existing* default's type in the config
(`InferType.infer_type`, `ivory/utils/infer_type.py`). If the default value is anything other than
`None`, the override string is cast directly to that value's type (`str`, `bool`, `list`, `int`, or
`float`). Only when the default value **is** `None` does `InferType` fall back to trial-casting the
override string, in order: bool (`true`/`false`, case-insensitive) → int → float → comma-separated
list → `None` (`none`/`null`) → falls back to `str`.

## Other example/test configs worth knowing about

All under `test/config/` (used by Ivory's own test suite, not meant as production references, but
useful to see edge cases):

- `workflow_config_missing_plugins.py`, `workflow_config_empty.py` — negative-path configs, used to
  test validation errors (missing `Pipeline` section, missing `plugins` key).
- `workflow_config_cust.py` — references `ivory.context_provider.PickleContextProvider`, which
  **does not exist** in the current codebase; don't copy this pattern (see
  [Known issues and limitations](known-issues-and-limitations.md)).
- `ivory/examples/config/workflow_config_parallel.py` — references a `ParallelPluginCollection` class
  that also does not exist; likewise not usable as a reference (see
  [Known issues and limitations](known-issues-and-limitations.md)). For real parallel plugins, use
  `AbstractParallelJoblibPlugin` instead (see [Plugins](plugins.md#parallel-plugins)).
