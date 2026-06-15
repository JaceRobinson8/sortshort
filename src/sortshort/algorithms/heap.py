"""Heap sort: build a max-heap, then repeatedly extract the root to the end."""

from __future__ import annotations

from collections.abc import Iterator

from sortshort.array import TrackedArray
from sortshort.events import Highlight


def heap_sort(arr: TrackedArray) -> Iterator[Highlight]:
    n = len(arr)
    for root in range(n // 2 - 1, -1, -1):
        yield from _sift_down(arr, root, n)
    for end in range(n - 1, 0, -1):
        yield from arr.swap(0, end)
        yield from _sift_down(arr, 0, end)


def _sift_down(arr: TrackedArray, root: int, size: int) -> Iterator[Highlight]:
    while True:
        child = 2 * root + 1
        if child >= size:
            break
        right = child + 1
        if right < size and (yield from arr.compare(right, child)):
            child = right
        if not (yield from arr.compare(child, root)):
            break
        yield from arr.swap(root, child)
        root = child
