"""Shared test fixtures and observation builders for actor_t6 tests."""

from __future__ import annotations

from game.state import ActionResult, ObservationState


def make_obs(
    actor: str = "cop",
    round: int = 1,
    my_pos: tuple[int, int] = (0, 0),
    opponent_pos: tuple[int, int] | None = (4, 4),
    barriers: list[tuple[int, int]] | None = None,
    legal_moves: list[str] | None = None,
    barriers_remaining: int | None = None,
) -> ObservationState:
    """Build an ObservationState with sensible defaults for tests."""
    return ObservationState(
        actor=actor,
        round=round,
        my_pos=my_pos,
        opponent_pos=opponent_pos,
        barriers=barriers or [],
        legal_moves=legal_moves or ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        barriers_remaining=barriers_remaining,
    )


def make_result(
    success: bool = True,
    game_over: bool = False,
    winner: str | None = None,
    win_reason: str | None = None,
) -> ActionResult:
    """Build an ActionResult for on_result tests."""
    return ActionResult(
        success=success,
        error=None,
        game_over=game_over,
        winner=winner,
        win_reason=win_reason,
    )
