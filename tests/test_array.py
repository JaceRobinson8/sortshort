"""Unit tests for the instrumented ``TrackedArray`` itself."""

from __future__ import annotations

import random
from collections.abc import Generator

from sortshort.array import TrackedArray
from sortshort.events import Action, Highlight


def _exhaust[T](gen: Generator[Highlight, None, T]) -> tuple[list[Highlight], T]:
    """Drain a generator, returning its highlights and ``return`` value."""
    highlights: list[Highlight] = []
    try:
        while True:
            highlights.append(next(gen))
    except StopIteration as stop:
        return highlights, stop.value


def test_shuffled_is_a_permutation_of_1_to_size() -> None:
    arr = TrackedArray.shuffled(10)
    assert sorted(arr.snapshot()) == list(range(1, 11))


def test_shuffled_is_deterministic_with_a_seeded_rng() -> None:
    a = TrackedArray.shuffled(20, random.Random(7))
    b = TrackedArray.shuffled(20, random.Random(7))
    assert a.snapshot() == b.snapshot()


def test_getitem_reads_without_counting_an_access() -> None:
    arr = TrackedArray([3, 1, 2])
    assert arr[0] == 3
    assert arr[2] == 2
    assert arr.stats.accesses == 0


def test_get_counts_an_access() -> None:
    arr = TrackedArray([3, 1, 2])
    assert arr.get(1) == 1
    assert arr.stats.accesses == 1


def test_compare_yields_highlight_and_returns_result() -> None:
    arr = TrackedArray([5, 2])
    highlights, result = _exhaust(arr.compare(0, 1))
    assert highlights == [Highlight(Action.COMPARE, (0, 1))]
    assert result is True  # 5 > 2
    assert arr.stats.comparisons == 1
    assert arr.stats.accesses == 2


def test_compare_values_highlights_given_indices() -> None:
    arr = TrackedArray([0, 0])
    highlights, result = _exhaust(arr.compare_values(1, 4, 0, 1))
    assert highlights == [Highlight(Action.COMPARE, (0, 1))]
    assert result is False  # 1 > 4 is False
    assert arr.stats.comparisons == 1


def test_swap_mutates_and_highlights() -> None:
    arr = TrackedArray([1, 2, 3])
    highlights = list(arr.swap(0, 2))
    assert arr.snapshot() == [3, 2, 1]
    assert highlights == [Highlight(Action.SWAP, (0, 2))]
    assert arr.stats.accesses == 2


def test_write_sets_value_and_highlights() -> None:
    arr = TrackedArray([1, 2, 3])
    highlights = list(arr.write(1, 99))
    assert arr.snapshot() == [1, 99, 3]
    assert highlights == [Highlight(Action.WRITE, (1,))]
    assert arr.stats.accesses == 1


def test_is_sorted() -> None:
    assert TrackedArray([1, 2, 3]).is_sorted()
    assert not TrackedArray([3, 1, 2]).is_sorted()
    assert TrackedArray([]).is_sorted()
