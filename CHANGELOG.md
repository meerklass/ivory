# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
