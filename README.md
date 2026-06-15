# SortShort

Interactive, fun, and educational visualization of sorting algorithms. Watch
bubble, insertion, selection, merge, quick, and heap sort animate a shuffled
array as bars, with the active comparisons, swaps, and writes highlighted in
real time.

## Run it

```bash
uv sync
uv run sortshort                 # or: python -m sortshort
uv run sortshort --algo Quick --size 120
```

### Controls

| Key | Action |
| --- | --- |
| `1`–`6` | choose algorithm (Bubble, Insertion, Selection, Merge, Quick, Heap) |
| `space` | pause / resume |
| `,` / `.` | slower / faster (steps per frame) |
| `↑` / `↓` | larger / smaller array |
| `r` | reshuffle and restart |
| `q` / `esc` | quit |

CLI flags: `--size`, `--fps`, `--algo`, `--seed` (see `sortshort --help`).

## How it works

Each algorithm is a generator that operates on an instrumented `TrackedArray`
and `yield`s a `Highlight` after every comparison, swap, or write. The pygame-ce
visualizer pulls a configurable number of steps per frame, so the algorithms
stay decoupled from rendering and read like textbook pseudocode. See
[CLAUDE.md](CLAUDE.md) for the full architecture.

## Development

```bash
uv sync
uv run pytest
pre-commit install
```

### Quality checks

```bash
uv run ruff check .       # lint
uv run ruff format .      # format
uv run mypy src           # type check
uv run pytest             # tests + coverage
```
