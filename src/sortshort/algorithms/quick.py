"""Quick sort: partition around a pivot, then recurse on each side (Lomuto)."""

from __future__ import annotations

from collections.abc import Generator, Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def quick_sort(arr: TrackedArray) -> Iterator[Highlight]:
    yield from _quick_sort(arr, 0, len(arr) - 1)


def _quick_sort(arr: TrackedArray, lo: int, hi: int) -> Iterator[Highlight]:
    if lo >= hi:
        return
    pivot = yield from _partition(arr, lo, hi)
    yield from _quick_sort(arr, lo, pivot - 1)
    yield from _quick_sort(arr, pivot + 1, hi)


def _partition(arr: TrackedArray, lo: int, hi: int) -> Generator[Highlight, None, int]:
    # Pivot is the last element; gather everything <= pivot to the left.
    store = lo
    for j in range(lo, hi):
        if not (yield from arr.compare(j, hi)):
            if store != j:
                yield from arr.swap(store, j)
            store += 1
    if store != hi:
        yield from arr.swap(store, hi)
    return store
