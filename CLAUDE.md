# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ivory is a simple, pure-Python, plugins-based workflow engine. It is primarily used as a workflow engine for MuSEEK

## Build & Development Commands

- Always use `uv` when running Python commands for development.

- Ask if any development tools should be added with `uv add --dev`.

- Perform lint and format (ruff) after code changes before running tests

```bash
uv run ruff check                          # lint
uv run ruff check --fix                    # lint with auto-fix
uv run ruff format                         # format
```

- Run tests with pytest

```bash
uv run pytest tests/                      # all tests
```

- Do not run `git add` or `git commit` unless instructed to do so