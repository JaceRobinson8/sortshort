"""Tests for the Typer CLI layer (no display required)."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from sortshort.__main__ import app
from sortshort.algorithms import ALGORITHMS

runner = CliRunner()


def _patch_visualizer(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    calls: dict[str, object] = {}

    class FakeVisualizer:
        def __init__(self, **kwargs: object) -> None:
            calls["init"] = kwargs

        def run(self) -> None:
            calls["ran"] = True

    # The command imports Visualizer lazily from `sortshort.visualizer` (so --help
    # needs no display), binding the name at call time. We therefore patch the
    # attribute on its source module, not on `sortshort.__main__`. If that lazy
    # import is ever moved to module top-level, update this target — otherwise
    # the test would silently construct the real pygame Visualizer.
    import sortshort.visualizer as visualizer

    monkeypatch.setattr(visualizer, "Visualizer", FakeVisualizer)
    return calls


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _patch_visualizer(monkeypatch)
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert calls["init"] == {"size": 80, "fps": 60, "algo": "Bubble", "seed": None}


def test_parses_all_options(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _patch_visualizer(monkeypatch)
    result = runner.invoke(
        app, ["--size", "12", "--fps", "30", "--algo", "Heap", "--seed", "7"]
    )

    assert result.exit_code == 0
    assert calls["ran"] is True
    assert calls["init"] == {"size": 12, "fps": 30, "algo": "Heap", "seed": 7}


@pytest.mark.parametrize("algo", list(ALGORITHMS))
def test_every_registered_algo_is_accepted(
    algo: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Ties --algo's accepted values to the registry, so adding/renaming an
    # algorithm is covered here rather than relying on hardcoded names.
    calls = _patch_visualizer(monkeypatch)
    result = runner.invoke(app, ["--algo", algo])

    assert result.exit_code == 0
    assert calls["init"] == {"size": 80, "fps": 60, "algo": algo, "seed": None}


def test_unknown_algo_is_rejected() -> None:
    result = runner.invoke(app, ["--algo", "Nope"])
    assert result.exit_code != 0


@pytest.mark.parametrize("flag", ["--size", "--fps", "--seed"])
def test_non_integer_values_are_rejected(flag: str) -> None:
    result = runner.invoke(app, [flag, "abc"])
    assert result.exit_code != 0


def test_help_exits_cleanly() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_main_invokes_app(monkeypatch: pytest.MonkeyPatch) -> None:
    # The `sortshort` entry point is `main`; verify it delegates to the Typer app.
    import sortshort.__main__ as cli

    invoked = {}
    monkeypatch.setattr(cli, "app", lambda: invoked.setdefault("called", True))
    cli.main()

    assert invoked["called"] is True


def test_main_passes_none_seed_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _patch_visualizer(monkeypatch)
    result = runner.invoke(app, ["--size", "5", "--algo", "Quick", "--seed", "1"])

    assert result.exit_code == 0
    assert calls["init"] == {"size": 5, "fps": 60, "algo": "Quick", "seed": 1}
