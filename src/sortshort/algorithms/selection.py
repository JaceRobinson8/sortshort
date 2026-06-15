"""Selection sort: find the max of the unsorted region and place it at the end."""

from __future__ import annotations

from collections.abc import Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def selection_sort(arr: TrackedArray) -> Iterator[Highlight]:
    n = len(arr)
    for end in range(n - 1, 0, -1):
        largest = 0
        for j in range(1, end + 1):
            if (yield from arr.compare(j, largest)):
                largest = j
        if largest != end:
            yield from arr.swap(largest, end)
