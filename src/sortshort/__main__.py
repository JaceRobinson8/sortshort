"""Command-line entry point: ``python -m sortshort`` / ``sortshort``."""

from __future__ import annotations

import argparse

from sortshort.algorithms import ALGORITHMS


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sortshort",
        description="Interactive visualization of sorting algorithms.",
    )
    parser.add_argument(
        "--size", type=int, default=80, help="number of elements (default: 80)"
    )
    parser.add_argument(
        "--fps", type=int, default=60, help="render frame rate (default: 60)"
    )
    parser.add_argument(
        "--algo",
        choices=list(ALGORITHMS),
        default="Bubble",
        help="algorithm to start with (default: Bubble)",
    )
    parser.add_argument(
        "--seed", type=int, default=None, help="seed for the shuffle (default: random)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    # Imported lazily so the CLI (and --help) does not require a display.
    from sortshort.visualizer import Visualizer

    Visualizer(size=args.size, fps=args.fps, algo=args.algo, seed=args.seed).run()


if __name__ == "__main__":
    main()
