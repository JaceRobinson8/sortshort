"""Registry of available sorting algorithms.

Each algorithm is a generator that operates on a
:class:`~sortshort.array.TrackedArray` and yields a
:class:`~sortshort.events.Highlight` per step. ``ALGORITHMS`` maps a
display name to its function so the visualizer and tests can iterate over
the full set without hard-coding individual names.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

from sortshort.algorithms.bubble import bubble_sort
from sortshort.algorithms.heap import heap_sort
from sortshort.algorithms.insertion import insertion_sort
from sortshort.algorithms.merge import merge_sort
from sortshort.algorithms.quick import quick_sort
from sortshort.algorithms.selection import selection_sort
from sortshort.array import TrackedArray
from sortshort.events import Highlight

Algorithm = Callable[[TrackedArray], Iterator[Highlight]]

ALGORITHMS: dict[str, Algorithm] = {
    "Bubble": bubble_sort,
    "Insertion": insertion_sort,
    "Selection": selection_sort,
    "Merge": merge_sort,
    "Quick": quick_sort,
    "Heap": heap_sort,
}

__all__ = ["ALGORITHMS", "Algorithm"]
