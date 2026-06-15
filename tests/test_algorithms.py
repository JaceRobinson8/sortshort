"""Every registered algorithm must sort correctly and do real work."""

from __future__ import annotations

import random

import pytest

from sortshort.algorithms import ALGORITHMS, Algorithm
from sortshort.array import TrackedArray

CASES: dict[str, list[int]] = {
    "empty": [],
    "single": [42],
    "two_sorted": [1, 2],
    "two_reversed": [2, 1],
    "sorted": list(range(1, 21)),
    "reversed": list(range(20, 0, -1)),
    "duplicates": [5, 1, 5, 3, 1, 3, 5, 1, 2, 2],
}


def _run(algorithm: Algorithm, values: list[int]) -> TrackedArray:
    arr = TrackedArray(values)
    for _ in algorithm(arr):  # drive the generator to completion
        pass
    return arr


@pytest.mark.parametrize("algorithm", ALGORITHMS.values(), ids=ALGORITHMS.keys())
@pytest.mark.parametrize("values", CASES.values(), ids=CASES.keys())
def test_sorts_correctly(algorithm: Algorithm, values: list[int]) -> None:
    arr = _run(algorithm, values)
    assert arr.snapshot() == sorted(values)
    assert arr.is_sorted()


@pytest.mark.parametrize("algorithm", ALGORITHMS.values(), ids=ALGORITHMS.keys())
def test_sorts_many_random_arrays(algorithm: Algorithm) -> None:
    rng = random.Random(1234)
    for _ in range(50):
        values = [rng.randint(0, 99) for _ in range(rng.randint(2, 60))]
        arr = _run(algorithm, values)
        assert arr.snapshot() == sorted(values)


@pytest.mark.parametrize("algorithm", ALGORITHMS.values(), ids=ALGORITHMS.keys())
def test_records_work(algorithm: Algorithm) -> None:
    arr = _run(algorithm, list(range(15, 0, -1)))
    assert arr.stats.comparisons > 0
    assert arr.stats.accesses > 0
