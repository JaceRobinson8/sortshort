"""Highlight events yielded by sorting algorithms as they run.

Algorithms operate on a :class:`~sortshort.array.TrackedArray` and ``yield`` a
``Highlight`` after each comparison, swap, or write. The visualizer reads the
most recent highlight each frame to decide which bars to color, keeping the
algorithms completely decoupled from the rendering layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Action(Enum):
    """The kind of array operation a highlight describes."""

    COMPARE = "compare"
    SWAP = "swap"
    WRITE = "write"


@dataclass(frozen=True, slots=True)
class Highlight:
    """A snapshot of which indices an algorithm just touched, and how.

    ``indices`` are the array positions involved in ``action`` this step. The
    visualizer colors these bars; everything else renders in the idle color.
    """

    action: Action
    indices: tuple[int, ...] = field(default_factory=tuple)
