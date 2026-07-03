"""Regression tests for terminal feedback delivery in scripts/selfplay.py."""

from __future__ import annotations

import sys
from pathlib import Path

from actor.base_actor import BaseActor

from tests.conftest import make_result

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import selfplay  # noqa: E402


class RecordingActor(BaseActor):
    """Deterministic actor that records every result callback."""

    def __init__(self, actions: list[str]) -> None:
        """Store the planned legal actions."""
        self.actions = list(actions)
        self.results: list[tuple[str, bool, str | None]] = []

    def get_action(self, obs):
        """Return the next planned action."""
        return self.actions.pop(0)

    def on_result(self, obs, action, result) -> None:
        """Record callback action, terminal flag, and winner."""
        self.results.append((action, result.game_over, result.winner))


def test_cop_terminal_move_notifies_thief_loss() -> None:
    cop = RecordingActor(["NW"])
    thief = RecordingActor(["E"])
    result = selfplay.play_game(
        cop, thief, grid=(3, 3), cop_pos=(2, 1), thief_pos=(0, 0),
        max_rounds=3, learn=True,
    )
    assert result.game_over and result.winner == "cop"
    assert thief.results[-1] == ("E", True, "cop")
    assert cop.results[-1] == ("NW", True, "cop")


def test_each_terminal_feedback_delivered_once() -> None:
    cop = RecordingActor(["NW"])
    thief = RecordingActor(["E"])
    selfplay.play_game(
        cop, thief, grid=(3, 3), cop_pos=(2, 1), thief_pos=(0, 0),
        max_rounds=3, learn=True,
    )
    assert sum(1 for _, terminal, _ in thief.results if terminal) == 1
    assert sum(1 for _, terminal, _ in cop.results if terminal) == 1


def test_non_learning_mode_sends_no_feedback() -> None:
    cop = RecordingActor(["NW"])
    thief = RecordingActor(["E"])
    selfplay.play_game(
        cop, thief, grid=(3, 3), cop_pos=(2, 1), thief_pos=(0, 0),
        max_rounds=3, learn=False,
    )
    assert cop.results == []
    assert thief.results == []


def test_actor_that_never_acted_gets_no_fabricated_terminal_feedback() -> None:
    cop = RecordingActor([])
    thief = RecordingActor(["SE"])
    selfplay.play_game(
        cop, thief, grid=(3, 3), cop_pos=(1, 1), thief_pos=(0, 0),
        max_rounds=3, learn=True,
    )
    assert thief.results == [("SE", True, "cop")]
    assert cop.results == []


def test_terminal_result_helper_shape_stays_compatible() -> None:
    result = make_result(game_over=True, winner="thief")
    assert result.game_over and result.winner == "thief"
