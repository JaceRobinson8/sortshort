# SortShort

Sorting Visualization

## Development

```bash
uv sync
uv run pytest
pre-commit install
```

## Quality checks

```bash
uv run ruff check .       # lint
uv run ruff format .      # format
uv run mypy src           # type check
uv run pytest             # tests + coverage
```

