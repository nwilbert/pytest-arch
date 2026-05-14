# AGENTS.md

This file provides guidance to AI agents working with code in this repository.

See README.md for the full API reference and usage examples.

## Commands

```bash
# Run all default nox sessions (format, lint, mypy, test, audit)
uv run nox

# Run a single nox session
uv run nox -s test              # tests with lockfile pytest version
uv run nox -s pytest_compat     # tests across Python + pytest version matrix (integration only)
uv run nox -s lint
uv run nox -s mypy
uv run nox -s coverage

# Run tests directly (faster, no nox overhead)
uv run pytest

# Run a single test
uv run pytest test/unit/test_query.py::test_name

# Coverage with HTML report
uv run nox -s coverage -- html
```

## Architecture

The plugin registers itself via the `pytest11` entry point in `pyproject.toml`, pointing to `pytest_imports.plugin`.

**Data flow:**
1. `plugin.py` — pytest fixtures + `ImportsFixture.check()`. `imports_project_paths` resolves source roots; `imports_root_node` (session-scoped) builds the model once per session; `imports` wraps both.
2. `parser.py` — `build_import_model()` walks the filesystem with AST analysis to produce a `RootNode`.
3. `model.py` — `RootNode` / `ModuleNode` (tree), `DotPath` (dot-separated path abstraction, pathlib-like), `ImportInModule` (single import record; `level > 0` means relative import).
4. `query.py` — frozen dataclass predicates (`CanImport`, `MustNotImport`, `MustNotImportPrivate`); `Scope` (hashable dict key); factory functions exported from `__init__.py`; `evaluate_rules()` collects all failures before raising.

**Key internals:**
- `scope(path, without=...)` stores exclusions as `tuple[str, ...]` for hashability.
- `CanImport` reports one failure per `.py` file in scope with no match; `MustNotImport` reports one failure per matching import found.
- `project()` returns `Scope(path=None)`, which triggers `root_node.walk()` over all modules.

**Test layout:**
- `test/unit/` — isolated unit tests (no filesystem)
- `test/integration/` — tests using real project files on disk
- `test/arch/` — self-referential architecture tests for this project

## Documentation

- Always update AGENTS.md and README.md when making changes that affect commands, architecture, or usage.

## Verification

- Always run `uv run nox` after making changes to verify all sessions pass.

## Git

- Never add `Co-Authored-By` lines to commit messages.
