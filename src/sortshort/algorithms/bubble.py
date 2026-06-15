"""Bubble sort: repeatedly swap adjacent out-of-order pairs."""

from __future__ import annotations

from collections.abc import Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def bubble_sort(arr: TrackedArray) -> Iterator[Highlight]:
    n = len(arr)
    for end in range(n - 1, 0, -1):
        swapped = False
        for i in range(end):
            if (yield from arr.compare(i, i + 1)):
                yield from arr.swap(i, i + 1)
                swapped = True
        if not swapped:
            break
