# Ivory internal documentation

This folder documents how the Ivory workflow engine works internally, for anyone who needs to extend
it or debug a pipeline built on top of it (e.g. MuSEEK). It assumes you're comfortable with Python
classes and the command line, but not necessarily with workflow-engine concepts.

Suggested reading order:

1. [Architecture](architecture.md) — what Ivory is, how a pipeline run actually executes end to end,
   and how state/context flows through it.
2. [Plugins](plugins.md) — the plugin contract, how plugins are discovered and wired together, and how
   to write a new one.
3. [Configuration](configuration.md) — the config file format, CLI overrides, and worked examples.
4. [Known issues and limitations](known-issues-and-limitations.md) — structural limitations that are
   working as intended but worth knowing up front.
