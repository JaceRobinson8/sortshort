"""Insertion sort: grow a sorted prefix, sliding each new element into place."""

from __future__ import annotations

from collections.abc import Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def insertion_sort(arr: TrackedArray) -> Iterator[Highlight]:
    n = len(arr)
    for i in range(1, n):
        j = i
        while j > 0 and (yield from arr.compare(j - 1, j)):
            yield from arr.swap(j - 1, j)
            j -= 1
