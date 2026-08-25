# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [3.0.0] (2026-08-25)

### Added

- Support for loading pipeline configs from a filesystem path (absolute, relative, or `~`-expanded
  `.py` file), in addition to the existing dotted module path — configs no longer need to be part of an
  installed/importable package (`WorkflowManager._load_config`)
- `tests/smoke/` executable smoke-test scripts (`run_file_path_config.sh`, `run_module_config.sh`) that
  exercise the `ivory` CLI end-to-end
- Support for Python 3.13 and 3.14
- `classproperty` descriptor (`ivory/utils/classproperty.py`) for attributes that need to work on both
  the class and an instance
- `ResourceSampler` (`ivory/utils/resource_sampler.py`): background-thread poller that samples memory
  and CPU throughout a plugin's execution, aggregating RSS across the main process and all of its live
  child processes

### Changed

- Refactored package layout to `src/ivory`, and renamed `test/` to `tests/`
- CLI usage text and `docs/configuration.md` updated to document file-path configs
- Widened `requires-python` to `>=3.10,<3.15` and added Python 3.11-3.14 classifiers
- Pinned `psutil` to `>=5.9.0`
- Declared `ruff` and `pytest` as explicit dev dependencies

### Fixed

- Replaced the deprecated `@classmethod @property` stacking pattern, removed in Python 3.13, in
  `ConfigSection.name` and `AbstractPlugin.name` with the new `classproperty` descriptor;
  `InferType._type_converter_dict` converted to a plain `@classmethod`
- Memory reporting was inaccurate: `LoopRunner` took a single memory/CPU snapshot of the main process
  only, taken after each plugin had already finished running. It now uses `ResourceSampler` to sample
  continuously during execution and includes memory used by child processes (e.g. `joblib`/`loky`
  workers spawned by `AbstractParallelJoblibPlugin`), which was previously invisible to the reported peak

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
