# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] (2026-08-25)

### Added

- Support for Python 3.13 and 3.14
- `classproperty` descriptor (`src/ivory/utils/classproperty.py`) for attributes that need to work on
  both the class and an instance
- `ResourceSampler` (`src/ivory/utils/resource_sampler.py`): background-thread poller that samples
  memory and CPU throughout a plugin's execution, aggregating RSS across the main process and all of
  its live child processes
- `src/ivory/py.typed` (PEP 561 marker), so downstream type checkers pick up this package's annotations
- `[tool.ruff]` and `[tool.pytest.ini_options]` in `pyproject.toml`, pinning the lint rule set and
  enabling `filterwarnings = ["error"]` so interpreter deprecation warnings fail CI instead of passing
  silently
- Tag-triggered `.github/workflows/release.yml`: builds the sdist/wheel, installs the built wheel into
  a clean venv and runs the test suite against it, verifies `ivory.__version__` matches the pushed tag,
  and attaches the artifacts to a GitHub Release (no PyPI upload yet)
- A `## Deferred to a future major version` section in `docs/known-issues-and-limitations.md`,
  cataloguing verified defects that are intentionally out of scope for this release because fixing them
  would change public API behaviour

### Changed

- Refactored package layout to `src/ivory`, and renamed `test/` to `tests/`
- Widened `requires-python` to `>=3.10,<3.15` and added Python 3.11-3.14 classifiers
- Pinned `psutil` to `>=5.9.0` and `joblib` to `>=1.3`
- Declared `ruff` and `pytest` as explicit dev dependencies; removed the now-redundant
  `[project.optional-dependencies] test` extra (it duplicated `[dependency-groups] dev` with a looser,
  unpinned `pytest` floor)
- `LoopRunner._store_to_ctx` now skips only the individual result whose context key is protected by
  `allow_overwrite=False`, instead of discarding every remaining result of that plugin
- `setuptools-scm` build requirement raised to `setuptools-scm[simple]>=9.2` (the `simple` extra, which
  makes an explicit `[tool.setuptools_scm]` section optional, does not exist before 9.2 — the previous
  `>=8.0` floor could silently resolve to an unbuildable `0.0.0` version)
- CI (`.github/workflows/tests.yml`): checkout now uses `fetch-depth: 0` so `setuptools-scm` can see
  tags; added a lint job running `ruff check`/`ruff format --check`; added `fail-fast: false` so all
  five Python versions report their own result; bumped `actions/checkout`/`actions/setup-python` to
  their current major versions; added steps exercising the `ivory` console script and the
  `tests/smoke/` scripts
- `uv.lock` and `CLAUDE.md` are now tracked in git instead of gitignored
- PyPI metadata: added `authors`, `[project.urls]`, `keywords`; bumped
  `Development Status` from `3 - Alpha` to `4 - Beta`; replaced the deprecated `License ::` classifier
  with a PEP 639 `license`/`license-files` declaration
- `docs/architecture.md` and `docs/plugins.md` updated to describe `ResourceSampler`'s background
  polling instead of the old single-snapshot measurement; `docs/known-issues-and-limitations.md`
  updated to describe the `_store_to_ctx` `continue` behaviour above
- Removed the orphaned, empty `ivory.examples`/`ivory.examples.config` packages (their only content
  was already deleted in 2.2.0; they were still tracked and shipped in the wheel)

### Fixed

- Replaced the deprecated `@classmethod @property` stacking pattern, removed in Python 3.13, in
  `ConfigSection.name` and `AbstractPlugin.name` with the new `classproperty` descriptor;
  `InferType._type_converter_dict` converted to a plain `@classmethod`
- Memory reporting was inaccurate: `LoopRunner` took a single memory/CPU snapshot of the main process
  only, taken after each plugin had already finished running. It now uses `ResourceSampler` to sample
  continuously during execution and includes memory used by child processes (e.g. `joblib`/`loky`
  workers spawned by `AbstractParallelJoblibPlugin`), which was previously invisible to the reported peak
- `AbstractPlugin.requirements` was a mutable class-level default shared by every plugin subclass —
  appending to `self.requirements` in one plugin's `set_requirements()` leaked into unrelated plugin
  classes and across repeated instantiations. Now initialised per instance
- `except KeyError or AttributeError` (`context.register`) and `except ValueError or TypeError`
  (`InferType.infer_type`) each silently caught only the first exception type, since `X or Y` evaluates
  to `X`; both now correctly catch both types
- A walrus-operator precedence bug in `WorkflowManager._parse_args` made the "exactly one config file"
  error message always report `got True` instead of the actual number of positional arguments given
- `ResourceSampler` could not be reused across more than one `with` block (`_stop_event` and the sample
  lists were never reset in `__enter__`); its background poll thread could also die silently the first
  time `process.children()` raised (e.g. a `joblib`/`loky` worker exiting mid-poll), truncating the
  reported peak with no warning; and an exception from its own final sample in `__exit__` could mask a
  real exception raised by the wrapped plugin
- `v2.3.0` was tagged but had no changelog entry; see below

## [2.3.0] (2026-07-27)

### Added

- Support for loading pipeline configs from a filesystem path (absolute, relative, or `~`-expanded
  `.py` file), in addition to the existing dotted module path — configs no longer need to be part of an
  installed/importable package (`WorkflowManager._load_config`)
- `tests/smoke/` executable smoke-test scripts (`run_file_path_config.sh`, `run_module_config.sh`) that
  exercise the `ivory` CLI end-to-end

### Changed

- CLI usage text and `docs/configuration.md` updated to document file-path configs

## [2.2.0] (2026-07-23)

### Added

- Internal developer documentation in `docs/`: architecture, plugin contract, configuration format, and known issues/limitations
- `ivory` console-script entry point, so `ivory [arguments] configuration` works directly from the shell after install
- CLI override support for Pipeline context: `--Pipeline-context=/path/to/pickle` now works on all configs
- Automatic context parameter initialization in Pipeline for seamless CLI overrides

### Changed

- Pipeline configuration now automatically defaults `context=None` if not explicitly set
- Renamed `_copy_results_from_context` to `_load_context_into_ctx` for improved clarity
- Declared `psutil` as a direct dependency (previously imported but undeclared) and dropped the unused `ipyparallel` dependency
- Corrected `pyproject.toml` readme path from `README.rst` to `README.md`
- Switched `pyproject.toml` package declaration to auto-discovery so subpackages are no longer silently dropped from the build

### Fixed

- Context loading now uses defensive `.get()` for robust null handling
- Workflow context can now be loaded and overridden via command-line arguments without config modifications
- Removed broken `ivory/examples/config/workflow_config_parallel.py` example, which referenced a long-removed `ParallelPluginCollection` class
- Removed stale `test/config/workflow_config_cust.py` fixture, which referenced a nonexistent `PickleContextProvider`
- Removed unused `.settings/` Eclipse/PyDev IDE metadata

## [2.1.0] (2026-05-04)

### Added

- `ivory.__version__` attribute to package for version reporting
- Resource tracking for plugin execution: tracks peak and average memory (GB) and CPU (%) usage per plugin
- Per-step resource summary output during pipeline execution
- `ResourceTiming` class to store and display memory and CPU metrics alongside execution timing
- `ResourceTimingCollection` class for aggregating resource statistics across multiple runs

### Changed

- `LoopRunner` now captures resource metrics using `psutil` for each plugin execution
- Plugin execution output now includes per-step resource usage in addition to execution time

### Fixed

- Changed setuptool-scm mode from toml to simple so that version is reflected correctly

## [2.0.0] (2026-01-15)

### Added

- Build updates and improvements

### Changed

- Properly handle `--help` and `-h` flags in input arguments
- Updated dependencies in pyproject.toml

### Fixed

- Fixed bugs in various tests

## [1.0.0] (2025-12-15)

### Added

- Nested config classes support
- Refactored backend with restriction of context access to plugins
- Abstract plugin class for parallelization support
- Setup installation improvements
- Error handling for invalid plugin names

### Changed

- Rename project to ivory
- Hand over plugin config directly instead of entire context
- Refactored backend.py with improved context management
- Updated gitignore and README

### Fixed

- Load context from disc
- Fixed bug when storing context to disc
- Fixed context entries cleanup before storage
- Fixed bug in _store_to_ctx method
- Removed all file headers for cleaner code

## [0.1.0] (2014-01-01)

### Added

- First release on PyPI
- Consistent time recording
- Syntactic sugar for Workflowmgr calls
- Parallel execution of workflows on IPython clusters

## [0.1.0dev] (2014-07-22)

### Added

- Consistent time recording
- Syntactic sugar for Workflowmgr calls
- Parallel execution of workflows on IPython clusters
