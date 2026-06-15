"""pygame-ce front end: drives an algorithm generator and draws the array.

The visualizer owns no sorting logic. Each frame it pulls a configurable number
of steps from the active algorithm generator, remembers the most recent
:class:`~sortshort.events.Highlight`, and paints every array element as a bar —
coloring the touched indices by the kind of operation. When the generator is
exhausted it plays a left-to-right "verification sweep" that lights the whole
array green.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from enum import Enum, auto

import pygame

from sortshort.algorithms import ALGORITHMS, Algorithm
from sortshort.array import TrackedArray
from sortshort.events import Action, Highlight

# Colors (R, G, B).
BACKGROUND = (16, 18, 27)
BAR_IDLE = (108, 122, 168)
BAR_VERIFIED = (84, 214, 122)
HUD_TEXT = (226, 230, 240)
HUD_DIM = (140, 148, 170)

ACTION_COLOR: dict[Action, tuple[int, int, int]] = {
    Action.COMPARE: (240, 208, 96),  # yellow
    Action.SWAP: (236, 92, 92),  # red
    Action.WRITE: (236, 140, 84),  # orange
}

TOP_MARGIN = 72
BOTTOM_MARGIN = 30
SIDE_MARGIN = 12
MIN_SIZE = 8
MAX_SIZE = 400
MIN_SPEED = 1
MAX_SPEED = 4096


class State(Enum):
    RUNNING = auto()
    PAUSED = auto()
    VERIFYING = auto()
    DONE = auto()


class Visualizer:
    """Interactive window that animates one sorting algorithm at a time."""

    def __init__(
        self,
        *,
        size: int = 80,
        fps: int = 60,
        algo: str = "Bubble",
        width: int = 1000,
        height: int = 640,
        seed: int | None = None,
    ) -> None:
        pygame.init()
        pygame.display.set_caption("SortShort")
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("menlo,consolas,monospace", 18)
        self.small_font = pygame.font.SysFont("menlo,consolas,monospace", 14)

        self.fps = fps
        self.rng = random.Random(seed)
        self.names: list[str] = list(ALGORITHMS)
        self.size = max(MIN_SIZE, min(MAX_SIZE, size))
        self.speed = self._default_speed(self.size)

        self.algo_name = algo if algo in ALGORITHMS else self.names[0]
        self.arr = TrackedArray([])
        self.steps: Iterator[Highlight] = iter(())
        self.last: Highlight | None = None
        self.state = State.RUNNING
        self.verify_index = 0
        self._reset(reshuffle=True)

    # -- lifecycle ---------------------------------------------------------

    @staticmethod
    def _default_speed(size: int) -> int:
        """A starting steps-per-frame that finishes most sorts in a few seconds."""
        return max(MIN_SPEED, size // 16)

    def _reset(self, *, reshuffle: bool, algorithm: Algorithm | None = None) -> None:
        if reshuffle:
            self.arr = TrackedArray.shuffled(self.size, self.rng)
        else:
            self.arr = TrackedArray(self.arr.snapshot())
        fn = algorithm or ALGORITHMS[self.algo_name]
        self.steps = fn(self.arr)
        self.last = None
        self.state = State.RUNNING
        self.verify_index = 0

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and not self._handle_key(event.key)
                ):
                    running = False
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(self.fps)
        pygame.quit()

    # -- input -------------------------------------------------------------

    def _handle_key(self, key: int) -> bool:
        """Return False to quit, True to keep running."""
        if key in (pygame.K_ESCAPE, pygame.K_q):
            return False
        elif key == pygame.K_SPACE:
            if self.state == State.RUNNING:
                self.state = State.PAUSED
            elif self.state == State.PAUSED:
                self.state = State.RUNNING
        elif key == pygame.K_r:
            self._reset(reshuffle=True)
        elif key in (pygame.K_PERIOD, pygame.K_RIGHTBRACKET):
            self.speed = min(MAX_SPEED, self.speed * 2)
        elif key in (pygame.K_COMMA, pygame.K_LEFTBRACKET):
            self.speed = max(MIN_SPEED, self.speed // 2)
        elif key == pygame.K_UP:
            self._resize(self.size * 2)
        elif key == pygame.K_DOWN:
            self._resize(self.size // 2)
        elif pygame.K_1 <= key <= pygame.K_9:
            self._select(key - pygame.K_1)
        return True

    def _select(self, index: int) -> None:
        if 0 <= index < len(self.names):
            self.algo_name = self.names[index]
            self._reset(reshuffle=True)

    def _resize(self, new_size: int) -> None:
        self.size = max(MIN_SIZE, min(MAX_SIZE, new_size))
        self.speed = self._default_speed(self.size)
        self._reset(reshuffle=True)

    # -- update ------------------------------------------------------------

    def _update(self) -> None:
        if self.state == State.RUNNING:
            self._advance(self.speed)
        elif self.state == State.VERIFYING:
            self.verify_index = min(len(self.arr), self.verify_index + self.speed)
            if self.verify_index >= len(self.arr):
                self.state = State.DONE

    def _advance(self, steps: int) -> None:
        for _ in range(steps):
            try:
                self.last = next(self.steps)
            except StopIteration:
                self.last = None
                self.state = State.VERIFYING
                self.verify_index = 0
                return

    # -- drawing -----------------------------------------------------------

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self._draw_bars()
        self._draw_hud()

    def _bar_color(self, index: int, active: frozenset[int]) -> tuple[int, int, int]:
        if self.state == State.DONE:
            return BAR_VERIFIED
        if self.state == State.VERIFYING and index < self.verify_index:
            return BAR_VERIFIED
        if index in active and self.last is not None:
            return ACTION_COLOR[self.last.action]
        return BAR_IDLE

    def _draw_bars(self) -> None:
        values = self.arr.snapshot()
        n = len(values)
        if n == 0:
            return
        peak = max(values)
        w, h = self.screen.get_size()
        usable_w = w - 2 * SIDE_MARGIN
        usable_h = h - TOP_MARGIN - BOTTOM_MARGIN
        slot = usable_w / n
        bar_w = max(1.0, slot - 1.0)
        active = frozenset(self.last.indices) if self.last else frozenset()
        for i, value in enumerate(values):
            bar_h = max(1.0, value / peak * usable_h)
            x = SIDE_MARGIN + i * slot
            y = TOP_MARGIN + (usable_h - bar_h)
            rect = pygame.Rect(round(x), round(y), max(1, round(bar_w)), round(bar_h))
            pygame.draw.rect(self.screen, self._bar_color(i, active), rect)

    def _draw_hud(self) -> None:
        idx = self.names.index(self.algo_name) + 1
        stats = self.arr.stats
        line1 = (
            f"[{idx}] {self.algo_name} sort    {self.state.name.title()}"
            f"    n={self.size}    speed={self.speed}/frame"
        )
        line2 = (
            f"comparisons {stats.comparisons:>8}    array accesses {stats.accesses:>8}"
        )
        self.screen.blit(self.font.render(line1, True, HUD_TEXT), (SIDE_MARGIN, 12))
        self.screen.blit(self.font.render(line2, True, HUD_DIM), (SIDE_MARGIN, 38))

        controls = (
            "1-6 algorithm   space pause   ,/. speed   up/down size   "
            "r reshuffle   q quit"
        )
        surf = self.small_font.render(controls, True, HUD_DIM)
        self.screen.blit(surf, (SIDE_MARGIN, self.screen.get_height() - 22))
