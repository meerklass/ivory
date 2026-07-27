# Architecture

## What Ivory is

Ivory is a small, sequential, config-driven **plugin runner**. You write a pipeline as an ordered list
of "plugins" (plain Python classes, one processing step each), list them in a config file, and Ivory
imports, instantiates, and runs them in that order, passing data between them through a shared
in-memory "context object".

It is **not** a DAG scheduler like Airflow, Luigi, or Snakemake: that is, there is no dependency graph, no task
parallelism across pipeline stages, and no static validation of whether a plugin's inputs will actually
be available before you run it. Ordering is simply the position of a plugin in a Python list. This is a
deliberate trade-off for simplicity — see
[Known issues and limitations](known-issues-and-limitations.md) for what that trade-off costs you.

Ivory is primarily used as a workflow engine for [MuSEEK](https://github.com/meerklass/museek).

## Entry points

- **Library call**: `ivory.execute(args)` (`ivory/__init__.py`) builds a `WorkflowManager` from a list
  of CLI-style argument strings, calls `.launch()`, and returns the resulting global context.
- **CLI function**: `ivory.cli.main.run()` reads `sys.argv[1:]` and delegates to `_main()`, which
  handles `--help`/`-h` and otherwise does `WorkflowManager(argv).launch()`.
- **Packaged console script**: `pyproject.toml` declares `ivory = "ivory.cli.main:run"` under
  `[project.scripts]`, so once installed, `ivory [arguments] configuration` works directly from the
  shell. Downstream projects can also call `ivory.cli.main.run()` directly and wrap it in their own
  console script — MuSEEK's `museek/cli/main.py` does exactly this: it sets
  `sys.argv = ["museek"] + list(args)` and calls Ivory's `run()`, so the `museek` command *is* Ivory
  under the hood.

## Execution flow

A run goes through these stages, in this order:

```
$ museek <config-module> [--Section-param=value ...]
        │
        ▼
WorkflowManager.__init__(argv)
        │
        ▼
WorkflowManager._setup(argv)
   ├─ _parse_args(argv)
   │    ├─ import the config module (last positional arg) and collect its
   │    │  ConfigSection-typed module attributes as "sections"; if a "Pipeline"
   │    │  section exists and doesn't already set "context", auto-seed
   │    │  Pipeline.context=None so --Pipeline-context=... is always a valid
   │    │  CLI override, even for configs that never mention context at all
   │    ├─ getopt() the remaining args against longopts derived from those
   │    │  sections, i.e. --SectionName-param=value
   │    └─ _config_immutable(): merge CLI overrides over file defaults
   │       (via InferType), wrap a plain Pipeline.plugins list in a Loop,
   │       and freeze everything into an ImmutableStruct
   ├─ validate a "Pipeline" section with a "plugins" key exists
   ├─ ctx().params = <the immutable config>
   ├─ ctx().plugins = ctx().params.Pipeline.plugins
   └─ context_file = Pipeline.get("context", None); if not None: unpickle that
      file and copy its Enum-keyed entries into the live ctx() via
      _load_context_into_ctx() (resume-from-checkpoint)
        │
        ▼
WorkflowManager.launch()            (static method)
   ├─ ctx().timings = []
   ├─ executor = SequentialBackend(ctx())
   └─ executor.run(ctx().params.Pipeline.plugins)
        │
        ▼
SequentialBackend.run(loop)
   └─ return [LoopRunner(loop)(self.ctx)]
        │
        ▼
LoopRunner.__call__(ctx)            ── the actual per-step execution engine
   for plugin in self.loop:                      # see "Loop" below
       resolve plugin.requirements from ctx       # -> _run_args()
       plugin.run(**resolved_kwargs)
       store plugin.results into ctx              # -> _store_to_ctx()
       record timing/CPU/memory (psutil)
       pickle the whole ctx to disk, if requested # -> _store_ctx()
```

Source: `ivory/workflow_manager.py` (`WorkflowManager`), `ivory/backend.py` (`SequentialBackend`),
`ivory/utils/loop_runner.py` (`LoopRunner`).

`SequentialBackend` is currently the *only* backend implementation — plugins always run one at a time,
in list order, in a single process.

## The context: how data flows between plugins

There is no direct function-call data passing between plugins. Instead, everything flows through a
single shared, mutable, dict-with-attribute-access object called the **context**, obtained via
`ctx()` (`ivory/context.py`) — a module-level singleton (`global_ctx`). `ctx()` is an instance of
`Struct` (`ivory/utils/struct.py`), which lets you do both `ctx()["x"] = 1` and `ctx().x == 1`.

- `ctx().params` holds the **frozen** configuration — an `ImmutableStruct`, whose `__setitem__` and
  `__setattr__` both raise `IllegalAccessException` if you try to mutate it after the fact.
- Everything else in `ctx()` is mutable runtime state: plugin results (keyed by `Enum` or `str`,
  see [Plugins](plugins.md)), the running list of `ctx.timings`, and per-`Loop` iteration state
  (a `WorkflowStruct` with `iter` and `state ∈ {RUN, STOP, EXIT, RESUME}`, keyed by `str(loop)`).

There is a pluggable seam for how the context is created — `context.get_context_provider()`
(`ivory/context.py`) — but it currently **always returns `DefaultContextProvider`**
(`ivory/context_provider.py`), regardless of anything you put in your config; no alternative provider
implementation exists in the codebase, so this seam isn't actually usable today (see
[Known issues and limitations](known-issues-and-limitations.md)). `DefaultContextProvider` just builds
a plain `Struct`/`ImmutableStruct` and does not persist anything on its own. The real way to
persist/resume context is described below.

## `Loop`: sequencing and repetition

`ivory.loop.Loop` (`ivory/loop.py`) is both the container for a pipeline's plugin list and its
iterator. `Loop.__next__` walks `self.plugin_list` and, for each entry:

- if it's already an `AbstractPlugin` instance, returns it directly;
- if it's a `str` (a dotted module path), instantiates it lazily via
  `PluginFactory.create_instance(plugin_name, self.ctx)` (see [Plugins](plugins.md));
- if it's a nested `Loop`, recurses into it until that inner loop's stop criteria fires.

Repetition is controlled by an `AbstractStopCriteria` (`ivory/utils/stop_criteria.py`) attached to each
`Loop`:

- `SimpleStopCriteria` (the default when you don't pass `stop=`) runs the loop's plugin list exactly
  once.
- `RangeStopCriteria(max_iter=N)` repeats the loop's plugin list `N` times, tracking iteration count in
  the loop's `WorkflowStruct` (via `context.loop_ctx(loop)`).

This is how iterative sub-pipelines (e.g. a self-calibration loop that should run until convergence or
for a fixed number of rounds) are expressed — by nesting `Loop`s, not by any plugin declaring "run me
again". There is no dependency-graph concept here: a `Loop` is just an ordered, possibly-repeating list.

## Checkpointing (saving and resuming context)

A plugin can ask to have the **entire context** pickled to disk right after it finishes, by calling
`self.store_context_to_disc(context_file_name, context_directory)`
(`ivory/plugin/abstract_plugin.py`). This publishes two `Result`s under the reserved keys
`ContextStorageEnum.FILE_NAME` and `ContextStorageEnum.DIRECTORY` (`ivory/enum/context_storage_enum.py`).

After that plugin's results are stored into `ctx`, `LoopRunner._store_ctx` checks whether both of those
keys are present and non-`None`; if so, it `pickle.dump()`s the whole `ctx` object to
`<directory>/<file_name>` and then resets both keys back to `None`, so the same plugin instance won't
trigger a second dump on a later loop iteration.

To resume from a saved context on a later run, set `Pipeline.context = "<path to the pickle file>"` in
your config — or, since `_get_config_sections` auto-seeds `Pipeline.context=None` for every config that
declares a `Pipeline` section, pass it on the command line instead without touching the config file at
all:

```bash
ivory --Pipeline-context=cache/simple_plugin.pickle package.subpackage.module
```

During `WorkflowManager._setup`, Ivory reads `Pipeline.get("context", None)` (defensive, so a config
that never mentions `context` still works) and, if it's not `None`, unpickles that file and copies every
`Enum`-keyed entry from it into the live `ctx()` (`WorkflowManager._load_context_into_ctx`, renamed from
`_copy_results_from_context`) — i.e. it restores previously published `Result`s, not arbitrary state,
before the pipeline starts running.

This whole mechanism is pickle-based with no schema or versioning — see
[Known issues and limitations](known-issues-and-limitations.md) for the implications.

## Timing and resource tracking

`LoopRunner.__call__` wraps every plugin's `run()` call with `time.time()` and `psutil.Process()`
memory/CPU sampling, and appends a `ResourceTiming` (`ivory/utils/timing.py`) to `ctx.timings` after
each step. A running summary is printed after each plugin (`print(resource_timing)`), and a full
timing report is printed once the loop completes (`_print_timings`). There is no structured logging —
all engine output goes through plain `print()`.
