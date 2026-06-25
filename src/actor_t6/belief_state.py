"""BeliefState — opponent-position tracker under partial observability.

Shared utility composed by both actor backends (ADR-003) so the partial-
observability logic lives in exactly one place. It keeps a single point
estimate of the opponent's cell: refreshed whenever ``opponent_pos`` is visible
and cleared at the start of a new sub-game (detected via ``round == 1``).

Leaf module — depends on nothing inside actor_t6.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.state import ObservationState


class BeliefState:
    """Tracks the best-known estimate of the opponent's position.

    The estimate is a point (col, row) tuple or ``None`` when the opponent has
    never been observed in the current sub-game. The tracker is intentionally
    simple: under full observability it mirrors ``opponent_pos`` each turn;
    under partial observability it retains the last sighting until refreshed.
    """

    def __init__(self) -> None:
        """Initialise with no estimate and no observed round yet."""
        self._estimate: tuple[int, int] | None = None
        self._last_round: int = 0

    def update(self, obs: ObservationState) -> None:
        """Incorporate a new observation, resetting on a new sub-game.

        A ``round == 1`` observation marks a fresh sub-game, so any stale
        estimate from the previous sub-game is discarded first. When the
        opponent is visible the estimate is refreshed to the exact position;
        otherwise the previous estimate (last known sighting) is retained.

        Args:
            obs: The current observation for this actor.
        """
        if obs.round <= 1:
            self.reset()
        self._last_round = obs.round
        if obs.opponent_pos is not None:
            self._estimate = tuple(obs.opponent_pos)

    def get_estimate(self) -> tuple[int, int] | None:
        """Return the current best estimate of the opponent position.

        Returns:
            The estimated (col, row), or ``None`` if never observed this
            sub-game.
        """
        return self._estimate

    def reset(self) -> None:
        """Clear the estimate for the start of a new sub-game."""
        self._estimate = None
        self._last_round = 0
