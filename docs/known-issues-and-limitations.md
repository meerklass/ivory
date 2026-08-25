# Known issues and limitations

This page used to track a set of stale/broken references found during the initial documentation pass
(a broken `workflow_config_parallel.py` example, a `test/config/workflow_config_cust.py` fixture
referencing a nonexistent `PickleContextProvider`, missing/vestigial `pyproject.toml` dependencies, no
packaged console script, and an incomplete `packages` declaration). All of those were fixed and the
stale files removed in [PR #32](https://github.com/meerklass/ivory/pull/32) — see `CHANGELOG.md`'s
`[2.2.0]` entry for the itemized history. What's left below are structural design limitations: things
that are working as intended, but easy to assume away if you don't know about them. See also
[Deferred to a future major version](#deferred-to-a-future-major-version) below for a second category:
verified defects that *aren't* working as intended, but were deliberately left unfixed in `v3.0.0`
because fixing them would change public API behaviour.

## Structural / design limitations

These aren't bugs — they're the trade-offs Ivory's simplicity is built on — but they're easy to run
into if you assume more flexibility than exists.

- **Pickle-based checkpointing only.** `AbstractPlugin.store_context_to_disc()` and `Pipeline.context`
  round-trip the *entire* context object via raw `pickle` (`LoopRunner._store_ctx`,
  `WorkflowManager._load_context_into_ctx`). There's no JSON/HDF5/other serialization option, no
  schema or version checking on load, and pickles are neither safe to load from an untrusted source nor
  guaranteed to stay compatible across Python or library version changes. A checkpoint saved under one
  environment may fail to load, or fail silently in a confusing way, under another.
- **Context provider seam is not actually pluggable.** `context.get_context_provider()`
  (`src/ivory/context.py`) is hardcoded to always return `DefaultContextProvider` — there's no config option
  that changes this, and no alternative provider implementation exists in the codebase. If you need
  different context-creation or persistence behavior, you currently have to modify this function
  directly rather than configure it (see [Architecture](architecture.md#the-context-how-data-flows-between-plugins)).
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
- **Single global mutable context.** `ctx()` (`src/ivory/context.py`) is a module-level singleton. Ivory is
  not designed for running multiple independent pipelines concurrently within one process.
- **Silent drop of individual results on overwrite conflicts.** Covered in detail in
  [Plugins](plugins.md#how-the-engine-wires-plugins-together): the overwrite guard checks
  `allow_overwrite` on the *existing* `Result` already stored under a context key, not on the new
  `Result` being stored. If that already-stored value has `allow_overwrite=False`,
  `LoopRunner._store_to_ctx` prints a message and skips storing that one result, rather than raising —
  so a plugin can silently end up missing exactly the one output whose key collided.
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

## Deferred to a future major version

Found during a `v3.0.0` pre-release audit and confirmed by executing each against the repo (not
speculative), but deliberately **not** fixed here: each of these would change a public exception type,
a return type, or otherwise-observable behaviour, so fixing them belongs in a release that's allowed to
break callers — not a release whose other goal was to be behaviour-preserving. Filed for future work
rather than lost in a conversation:

- **No common exception base class.** `src/ivory/exceptions/exceptions.py` — `IllegalAccessException`,
  `NotImplementedException`, `InvalidAttributeException`, `UnsupportedPluginTypeException`, and
  `InvalidLoopException` all derive directly from `Exception`, so downstream code cannot
  `except IvoryError` to catch anything Ivory-specific.
- **`Struct.copy()` loses subclass type.** `src/ivory/utils/struct.py:126-128` hardcodes
  `return Struct(self)`; `WorkflowStruct().copy()` returns a plain `Struct` (verified), silently
  losing `.increment()`/`.stop()`/`.reset()`. Same pattern in `ImmutableStruct.copy()`. Should be
  `type(self)(self)`.
- **`del struct.attr` raises the wrong exception type.** `struct.py:117-124` — `Struct.__delattr__`
  delegates to `__delitem__`, so `del s.missing` raises `KeyError` (verified), not `AttributeError`,
  inconsistent with attribute *reads*, which correctly raise `AttributeError`.
- **`WorkflowStruct.iter`/`.state` are invisible to the `Mapping` protocol.** `struct.py:136-138` — both
  are class attributes, not stored via `__setitem__`. Verified: a fresh `WorkflowStruct()` has
  `.iter == 0` but `len(ws) == 0`, `'iter' in ws` is `False`, and `dict(ws) == {}`; the mapping view
  changes shape depending on call history.
- **`classproperty` is a non-data descriptor.** `src/ivory/utils/classproperty.py` — `plugin.name = "x"`
  silently creates a shadowing instance attribute instead of raising (verified). Since `name` is the
  config-resolution lookup key (see [Plugins](plugins.md#discovery-and-loading)), a stray assignment
  anywhere corrupts config resolution with no error. Needs a `__set__` that raises.
- **Plugin discovery has no `issubclass` check.** `src/ivory/plugin/plugin_factory.py:59-73` — scans
  `dir(module)` for any name ending in `"Plugin"` without checking it's actually a class, let alone an
  `AbstractPlugin` subclass; a module that merely *imports* another plugin class fails with a
  misleading "more than one valid Plugin" error. The same file's `:34-41` also rewrites *any* exception
  raised while executing a plugin module (not just import failures) into a generic
  `UnsupportedPluginTypeException`, masking the real cause.
- **`WorkflowState.EXIT` doesn't work.** `src/ivory/loop.py:116-126` — `loop_ctx(inner_loop).exit()`
  does not stop the loop early (verified: it runs to completion regardless), because
  `RangeStopCriteria.is_stop()` overwrites `EXIT` with `STOP` before the `StopIteration` that would
  check it ever propagates. The iteration counter also overshoots by one on the final iteration, and
  `Loop.__next__` recurses instead of looping, so a pathological empty/all-skipped plugin list raises
  `RecursionError` instead of terminating cleanly.
- **`WorkflowManager.launch()` can't support two managers at once.** `src/ivory/workflow_manager.py:37-44`
  is a `@staticmethod` that reads the *global* `ctx()`, despite being documented and called as an
  instance method (`mgr.launch()`); constructing a second `WorkflowManager` and calling the first's
  `launch()` runs the second's pipeline.
- **CLI value inference mangles paths and short lists.** `src/ivory/utils/infer_type.py:36-38` strips
  *all* spaces and single quotes from a CLI override value, and `listify` requires at least one comma —
  so `--Pipeline-context='/my path/f.pkl'` becomes `/mypath/f.pkl` (verified), and overriding a
  list-typed value with a single element raises `ValueError: Not a string!`. Directly affects the
  `Pipeline.context` CLI override feature.
- **Dead code**, safe to delete whenever this list is next acted on: `NotImplementedException`
  (referenced nowhere); `TimingCollection`/`ResourceTimingCollection` (referenced nowhere in `src/` or
  `tests/`, and `ResourceTimingCollection.__str__` would `ZeroDivisionError` on an empty collection);
  `Loop._load_iter` (never called); the `copyreg` bound-method-pickling hook installed as an import
  side effect in `src/ivory/__init__.py` (duplicates CPython's own `method_reduce` behaviour); and the
  unreachable `None: cls.noneify` entry in `InferType._type_converter_dict` (the dict is keyed by
  `type(config_value)`, and `config_value is not None` is already guaranteed by the caller).
