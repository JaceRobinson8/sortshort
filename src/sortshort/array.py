"""An instrumented list that sorting algorithms operate on.

``TrackedArray`` is the seam between algorithms and the visualizer. Its mutating
operations are *generators*: they ``yield`` a :class:`~sortshort.events.Highlight`
describing what was touched and (for ``compare``) ``return`` the comparison
result via ``yield from``. This lets an algorithm read like textbook pseudocode
while the visualizer drives it one step at a time and counts work done.
"""

from __future__ import annotations

import random
from collections.abc import Generator, Iterator
from dataclasses import dataclass

from sortshort.events import Action, Highlight


@dataclass
class Stats:
    """Running tally of work performed, shown in the HUD."""

    comparisons: int = 0
    accesses: int = 0


class TrackedArray:
    """A list of ints that records comparisons and accesses as it is sorted."""

    def __init__(self, values: list[int]) -> None:
        self._data = list(values)
        self.stats = Stats()

    @classmethod
    def shuffled(cls, size: int, rng: random.Random | None = None) -> TrackedArray:
        """Build an array of ``1..size`` in random order."""
        rng = rng or random.Random()
        values = list(range(1, size + 1))
        rng.shuffle(values)
        return cls(values)

    # -- plain reads -------------------------------------------------------

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, i: int) -> int:
        return self._data[i]

    def get(self, i: int) -> int:
        """Read ``data[i]``, counting an access (does not yield)."""
        self.stats.accesses += 1
        return self._data[i]

    def snapshot(self) -> list[int]:
        """A plain copy of the current contents (for rendering/tests)."""
        return list(self._data)

    def is_sorted(self) -> bool:
        return all(
            self._data[i] <= self._data[i + 1] for i in range(len(self._data) - 1)
        )

    # -- instrumented, yielding operations ---------------------------------

    def compare(self, i: int, j: int) -> Generator[Highlight, None, bool]:
        """Yield a COMPARE highlight on ``(i, j)``; return ``data[i] > data[j]``."""
        self.stats.comparisons += 1
        self.stats.accesses += 2
        yield Highlight(Action.COMPARE, (i, j))
        return self._data[i] > self._data[j]

    def compare_values(
        self, a: int, b: int, *indices: int
    ) -> Generator[Highlight, None, bool]:
        """Compare two raw values, highlighting ``indices``; return ``a > b``.

        Used by algorithms (e.g. merge) that compare values held outside the
        array while still wanting the touched positions highlighted.
        """
        self.stats.comparisons += 1
        yield Highlight(Action.COMPARE, indices)
        return a > b

    def swap(self, i: int, j: int) -> Iterator[Highlight]:
        """Swap ``data[i]`` and ``data[j]``, yielding a SWAP highlight."""
        self.stats.accesses += 2
        self._data[i], self._data[j] = self._data[j], self._data[i]
        yield Highlight(Action.SWAP, (i, j))

    def write(self, i: int, value: int) -> Iterator[Highlight]:
        """Set ``data[i] = value``, yielding a WRITE highlight on ``i``."""
        self.stats.accesses += 1
        self._data[i] = value
        yield Highlight(Action.WRITE, (i,))
