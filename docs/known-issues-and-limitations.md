# Known issues and limitations

Two different kinds of things to know before working on Ivory: bugs/stale references that should
probably just be fixed, and structural design limitations that are working as intended but easy to
assume away if you don't know about them.

## Stale or broken references (bugs)

- **`ivory/examples/config/workflow_config_parallel.py`** imports
  `ivory.plugin.parallel_plugin_collection.ParallelPluginCollection`. That module/class does not exist
  anywhere in the current repository — this example is currently broken and shouldn't be used as a
  template.
- **`test/config/workflow_config_cust.py`** sets
  `context_provider="ivory.context_provider.PickleContextProvider"` in its `Pipeline` section. No such
  class exists in `ivory/context_provider.py` (only `DefaultContextProvider` does), and
  `context.get_context_provider()` (`ivory/context.py`) is hardcoded to always return
  `DefaultContextProvider` regardless of this config key — so this key is silently ignored, not
  honored. Real context persistence works via `AbstractPlugin.store_context_to_disc()` +
  `Pipeline.context`, described in [Architecture](architecture.md#checkpointing-saving-and-resuming-context).
- **`psutil`** is imported directly in `ivory/utils/loop_runner.py` (for the resource-tracking feature)
  but is not listed in `pyproject.toml`'s `dependencies` — a packaging gap. It happens to already be
  present in environments that install it transitively or have it from another package.
- **No `[project.scripts]` entry point** in `pyproject.toml`, so nothing currently installs an `ivory`
  console script. Invoke via `python -m ivory.cli.main [arguments] configuration` instead, or let a
  downstream project wrap it — MuSEEK's `museek/cli/main.py` calls `ivory.cli.main.run()` directly and
  exposes that as the `museek` console script.
- **`ipyparallel`** is listed as a dependency in `pyproject.toml` but is not referenced anywhere in the
  current source — likely vestigial from a planned or removed parallel backend (only
  `SequentialBackend` exists today).
- **`pyproject.toml` declares `readme = "README.rst"`**, but the actual file in the repo is
  `README.md` — this mismatch could break metadata rendering on PyPI or similar if this package is ever
  published there.
- **`pyproject.toml` only declares `packages = ["ivory"]`** under `[tool.setuptools]`, not the
  subpackages (`ivory.cli`, `ivory.plugin`, `ivory.utils`, `ivory.enum`, `ivory.exceptions`) —
  potentially a packaging gap for sdist/wheel builds depending on how setuptools' package discovery is
  configured elsewhere.

## Structural / design limitations

These aren't bugs — they're the trade-offs Ivory's simplicity is built on — but they're easy to run
into if you assume more flexibility than exists.

- **Pickle-based checkpointing only.** `AbstractPlugin.store_context_to_disc()` and `Pipeline.context`
  round-trip the *entire* context object via raw `pickle` (`LoopRunner._store_ctx`,
  `WorkflowManager._copy_results_from_context`). There's no JSON/HDF5/other serialization option, no
  schema or version checking on load, and pickles are neither safe to load from an untrusted source nor
  guaranteed to stay compatible across Python or library version changes. A checkpoint saved under one
  environment may fail to load, or fail silently in a confusing way, under another.
- **Sequential-only execution across plugins.** `SequentialBackend` is the only backend; plugins always
  run one at a time, in list order, in a single process. Parallelism only exists *within* a single
  plugin's `run()` call, via `AbstractParallelJoblibPlugin`/`joblib` (see
  [Plugins](plugins.md#parallel-plugins)) — never across plugins or pipeline stages.
- **No dependency graph or static validation.** Ordering is purely the plugin's position in the
  `Pipeline.plugins` list. A plugin requiring a context key that hasn't been published yet is only
  caught at runtime, as a `ValueError` from `LoopRunner._run_args`, the moment that plugin tries to run
  — not before the pipeline starts, and not by any linting/validation step.
- **Config files are arbitrary executable Python**, not declarative data. This is powerful (you can
  compute config values, import helpers, etc.) but means a config file can do anything Python code can
  do, and there is no schema validation before `WorkflowManager` starts consuming it — a typo in a
  section or key name typically surfaces as a runtime error deep in plugin execution, not an upfront
  config error.
- **Single global mutable context.** `ctx()` (`ivory/context.py`) is a module-level singleton. Ivory is
  not designed for running multiple independent pipelines concurrently within one process.
- **Silent partial-drop on overwrite conflicts.** Covered in detail in
  [Plugins](plugins.md#how-the-engine-wires-plugins-together): the overwrite guard checks
  `allow_overwrite` on the *existing* `Result` already stored under a context key, not on the new
  `Result` being stored. If that already-stored value has `allow_overwrite=False`,
  `LoopRunner._store_to_ctx` prints a message and returns immediately — silently discarding any of that
  plugin's remaining, not-yet-stored `Result`s rather than raising or continuing to store the rest.
- **No structured logging.** All engine-level output (per-step progress, resource timings) goes through
  plain `print()` calls in `LoopRunner`, not the `logging` module — there's no log level control, and
  capturing/redirecting engine output means capturing stdout.
- **No automatic memory management — a poorly designed plugin can blow up memory usage.** The engine
  gives you no help here; it's entirely on the plugin author to be careful:
  - `ctx` never evicts old entries. Every `Result` any plugin has ever published stays referenced in the
    context for the rest of the run (`LoopRunner._store_to_ctx` only ever adds/overwrites keys, never
    deletes them), so a plugin that stores a large array (e.g. a full TOD array) under a `Result` keeps
    it resident in memory for every subsequent plugin, even once nothing needs it anymore.
  - Checkpointing (`LoopRunner._store_ctx`) pickles the *entire* context object in one call. This
    requires building the whole serialized byte stream in memory before it's written to disk, so its
    peak memory cost scales with the sum of everything ever stored in `ctx`, not just what the
    checkpointing plugin itself produced.
  - For `AbstractParallelJoblibPlugin`, whatever `map()` yields is pickled and sent to each joblib
    worker process. If `map()` yields large objects (e.g. full arrays) instead of lightweight references
    (indices, file paths, slices), memory use multiplies by roughly `n_jobs` across worker processes.
    `gather_and_set_result` also receives the full list of every job's output at once — with `n_iter`
    large results in flight simultaneously, before you've even combined them.
