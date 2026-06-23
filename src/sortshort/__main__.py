"""Command-line entry point: ``python -m sortshort`` / ``sortshort``."""

from __future__ import annotations

import typer

from sortshort.algorithms import ALGORITHMS

app = typer.Typer(
    add_completion=False,
    help="Interactive visualization of sorting algorithms.",
)


def _validate_algo(value: str) -> str:
    # Validate against the registry so accepted values track ALGORITHMS with no
    # hardcoded names (replaces argparse's ``choices=list(ALGORITHMS)``).
    if value not in ALGORITHMS:
        choices = ", ".join(ALGORITHMS)
        raise typer.BadParameter(f"{value!r} is not one of: {choices}")
    return value


@app.callback(invoke_without_command=True)
def run(
    size: int = typer.Option(80, help="number of elements"),
    fps: int = typer.Option(60, help="render frame rate"),
    algo: str = typer.Option(
        "Bubble", callback=_validate_algo, help="algorithm to start with"
    ),
    seed: int | None = typer.Option(
        None, help="seed for the shuffle (default: random)"
    ),
) -> None:
    """Run the sorting visualizer."""
    # Imported lazily so the CLI (and --help) does not require a display.
    from sortshort.visualizer import Visualizer

    Visualizer(size=size, fps=fps, algo=algo, seed=seed).run()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
