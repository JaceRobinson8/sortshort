"""Tests for the argparse CLI layer (no display required)."""

from __future__ import annotations

import pytest

from sortshort.__main__ import _parse_args, main
from sortshort.algorithms import ALGORITHMS


def test_defaults() -> None:
    args = _parse_args([])
    assert args.size == 80
    assert args.fps == 60
    assert args.algo == "Bubble"
    assert args.seed is None


def test_parses_all_options() -> None:
    args = _parse_args(["--size", "12", "--fps", "30", "--algo", "Heap", "--seed", "7"])
    assert args.size == 12
    assert args.fps == 30
    assert args.algo == "Heap"
    assert args.seed == 7


@pytest.mark.parametrize("algo", list(ALGORITHMS))
def test_every_registered_algo_is_accepted(algo: str) -> None:
    # Ties --algo's accepted values to the registry, so adding/renaming an
    # algorithm is covered here rather than relying on hardcoded names.
    assert _parse_args(["--algo", algo]).algo == algo


def test_unknown_algo_is_rejected() -> None:
    with pytest.raises(SystemExit):
        _parse_args(["--algo", "Nope"])


@pytest.mark.parametrize("flag", ["--size", "--fps", "--seed"])
def test_non_integer_values_are_rejected(flag: str) -> None:
    with pytest.raises(SystemExit):
        _parse_args([flag, "abc"])


def test_help_exits_cleanly() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_args(["--help"])
    assert exc.value.code == 0


def _patch_visualizer(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    calls: dict[str, object] = {}

    class FakeVisualizer:
        def __init__(self, **kwargs: object) -> None:
            calls["init"] = kwargs

        def run(self) -> None:
            calls["ran"] = True

    # `main` imports Visualizer lazily from `sortshort.visualizer` (so --help
    # needs no display), binding the name at call time. We therefore patch the
    # attribute on its source module, not on `sortshort.__main__`. If that lazy
    # import is ever moved to module top-level, update this target — otherwise
    # the test would silently construct the real pygame Visualizer.
    import sortshort.visualizer as visualizer

    monkeypatch.setattr(visualizer, "Visualizer", FakeVisualizer)
    return calls


def test_main_drives_the_visualizer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _patch_visualizer(monkeypatch)
    main(["--size", "5", "--algo", "Quick", "--seed", "1"])

    assert calls["ran"] is True
    assert calls["init"] == {"size": 5, "fps": 60, "algo": "Quick", "seed": 1}


def test_main_passes_none_seed_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _patch_visualizer(monkeypatch)
    main([])

    assert calls["init"] == {"size": 80, "fps": 60, "algo": "Bubble", "seed": None}
