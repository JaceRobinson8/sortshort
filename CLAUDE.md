# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

SortShort — an interactive, visual-only sorting-algorithm visualizer (Python 3.13). A pygame-ce window animates a shuffled array as bars; six algorithms (bubble, insertion, selection, merge, quick, heap) are selectable at runtime. Run it with `uv run sortshort`.

## Architecture

The central design is that **algorithms are decoupled from rendering** via generator-based instrumentation:

- [array.py](src/sortshort/array.py) — `TrackedArray` wraps a `list[int]` and counts comparisons/accesses. Its mutating ops (`compare`, `compare_values`, `swap`, `write`) are **generators**: they `yield` a `Highlight` and, for the compare variants, `return` the boolean result. Algorithms consume them with `yield from` (e.g. `if (yield from arr.compare(i, j)): ...`). The compare methods are typed `Generator[Highlight, None, bool]` so the `yield from` result is `bool` under mypy strict.
- [events.py](src/sortshort/events.py) — `Action` enum + frozen `Highlight(action, indices)`. One highlight describes which indices were touched this step and how; the visualizer colors those bars.
- [algorithms/](src/sortshort/algorithms/) — one generator per file, each `(TrackedArray) -> Iterator[Highlight]`, written close to textbook form. [algorithms/__init__.py](src/sortshort/algorithms/__init__.py) exposes the `ALGORITHMS` registry (name → fn) and the `Algorithm` type alias; the visualizer and tests both iterate over it.
- [visualizer.py](src/sortshort/visualizer.py) — pygame-ce app. Owns no sorting logic: each frame it pulls `speed` steps from the active generator, remembers the last `Highlight`, and redraws bars. State machine `RUNNING ⇄ PAUSED`, then `RUNNING → VERIFYING → DONE` (the verify sweep lights the array green when the generator is exhausted). Lazily imported by the CLI command so `--help` needs no display.
- [cli.py](src/sortshort/cli.py) — Typer CLI (`--size/--fps/--algo/--seed`); `--algo` is validated against the `ALGORITHMS` registry via a callback. Exposes `app` and the `main` entry point (`sortshort = "sortshort.cli:main"`).
- [__main__.py](src/sortshort/__main__.py) — thin shim that calls `cli.main()` so `python -m sortshort` works.

**To add an algorithm:** write a generator in `algorithms/`, register it in `ALGORITHMS`. Tests in [tests/test_algorithms.py](tests/test_algorithms.py) are parametrized over the registry, so they cover it automatically.

## Tooling

Uses [uv](https://docs.astral.sh/uv/) for dependency and environment management. Run all commands through `uv run` so they execute inside the project's locked `.venv`.

```bash
uv sync                              # install/sync deps from uv.lock
uv run pytest                        # run tests (with coverage, configured in pyproject.toml)
uv run pytest tests/test_version.py::test_version   # run a single test
uv run ruff check .                  # lint
uv run ruff format .                 # format
uv run mypy src                      # type check (strict mode)
pre-commit install                   # enable ruff auto-fix/format on commit
```

## Conventions

- **Strict typing** — mypy runs in `strict` mode over `src`. All functions need type annotations.
- **Ruff** enforces lint rules `E, F, I, UP, B, SIM, RUF` at line length 88. Pre-commit runs ruff with `--fix` plus ruff-format on every commit.
- **Coverage** is on by default (`--cov=sortshort` in `pyproject.toml`); `pytest` reports term-missing.
- CI (`.github/workflows/ci.yml`) gates PRs on: ruff check, ruff format `--check`, `mypy src`, and `pytest`. Match these locally before pushing.
- Package layout is `src/`-based; the importable package is `sortshort`.
