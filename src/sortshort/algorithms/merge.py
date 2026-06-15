"""Merge sort: recursively sort halves, then merge them back in order."""

from __future__ import annotations

from collections.abc import Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def merge_sort(arr: TrackedArray) -> Iterator[Highlight]:
    yield from _merge_sort(arr, 0, len(arr))


def _merge_sort(arr: TrackedArray, lo: int, hi: int) -> Iterator[Highlight]:
    if hi - lo <= 1:
        return
    mid = (lo + hi) // 2
    yield from _merge_sort(arr, lo, mid)
    yield from _merge_sort(arr, mid, hi)
    yield from _merge(arr, lo, mid, hi)


def _merge(arr: TrackedArray, lo: int, mid: int, hi: int) -> Iterator[Highlight]:
    left = [arr.get(i) for i in range(lo, mid)]
    right = [arr.get(i) for i in range(mid, hi)]
    i = j = 0
    k = lo
    while i < len(left) and j < len(right):
        if (yield from arr.compare_values(left[i], right[j], k)):
            yield from arr.write(k, right[j])
            j += 1
        else:
            yield from arr.write(k, left[i])
            i += 1
        k += 1
    while i < len(left):
        yield from arr.write(k, left[i])
        i += 1
        k += 1
    while j < len(right):
        yield from arr.write(k, right[j])
        j += 1
        k += 1
