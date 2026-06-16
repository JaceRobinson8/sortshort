"""Tests for the argparse CLI layer (no display required)."""

from __future__ import annotations

import pytest

from sortshort.__main__ import _parse_args, main


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


def test_unknown_algo_is_rejected() -> None:
    with pytest.raises(SystemExit):
        _parse_args(["--algo", "Nope"])


def test_help_exits_cleanly() -> None:
    with pytest.raises(SystemExit) as exc:
        _parse_args(["--help"])
    assert exc.value.code == 0


def test_main_drives_the_visualizer(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    class FakeVisualizer:
        def __init__(self, **kwargs: object) -> None:
            calls["init"] = kwargs

        def run(self) -> None:
            calls["ran"] = True

    import sortshort.visualizer as visualizer

    monkeypatch.setattr(visualizer, "Visualizer", FakeVisualizer)
    main(["--size", "5", "--algo", "Quick", "--seed", "1"])

    assert calls["ran"] is True
    assert calls["init"] == {"size": 5, "fps": 60, "algo": "Quick", "seed": 1}
