"""Render each sorting algorithm headlessly to an animated GIF for the README.

The script reuses the real :class:`~sortshort.visualizer.Visualizer` rendering
(driving its ``_update``/``_draw`` directly) but runs under SDL's ``dummy`` video
driver, so it needs no display and produces deterministic output. One GIF per
entry in ``ALGORITHMS`` is written to ``assets/<name>.gif``.

    uv run --group docs python scripts/record.py
"""

from __future__ import annotations

import os
import random
from pathlib import Path

# Render offscreen: read by pygame's display init, so set before any window is
# created (the Visualizer calls set_mode in __init__).
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
from PIL import Image

from sortshort.algorithms import ALGORITHMS
from sortshort.array import TrackedArray
from sortshort.visualizer import State, Visualizer

SEED = 7
SIZE = 48
WIDTH = 760
HEIGHT = 400
TARGET_FRAMES = 100
FRAME_MS = 50  # ~20 fps playback
PALETTE_COLORS = 48
ASSETS = Path(__file__).resolve().parent.parent / "assets"


def _count_steps(name: str) -> int:
    """Run the algorithm once (no rendering) to size the per-frame step count.

    Uses the same seed/size as the recorded run so the shuffle matches.
    """
    arr = TrackedArray.shuffled(SIZE, random.Random(SEED))
    return sum(1 for _ in ALGORITHMS[name](arr))


def _capture(viz: Visualizer) -> Image.Image:
    surface = viz.screen
    data = pygame.image.tobytes(surface, "RGB")
    return Image.frombytes("RGB", surface.get_size(), data)


def record(name: str) -> Path:
    steps = _count_steps(name)
    viz = Visualizer(
        size=SIZE, fps=60, algo=name, seed=SEED, width=WIDTH, height=HEIGHT
    )
    # Pack the whole sort into ~TARGET_FRAMES frames regardless of its length.
    viz.speed = max(1, steps // TARGET_FRAMES)

    frames: list[Image.Image] = []
    # Drive the same update/draw the interactive loop uses until the verify
    # sweep finishes (RUNNING -> VERIFYING -> DONE).
    while True:
        viz._update()
        viz._draw()
        frames.append(_capture(viz))
        if viz.state == State.DONE:
            break

    # Quantize to a shared palette so the GIF stays small.
    palette = frames[0].quantize(colors=PALETTE_COLORS)
    frames = [f.quantize(palette=palette) for f in frames]

    out = ASSETS / f"{name.lower()}.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    return out


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for name in ALGORITHMS:
        path = record(name)
        print(f"wrote {path} ({path.stat().st_size // 1024} KiB)")
    pygame.quit()


if __name__ == "__main__":
    main()
