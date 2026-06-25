"""HeuristicActor — rule-based Cop/Thief decision backend (PRD §3.3 FR-02).

A single :class:`~actor.base_actor.BaseActor` subclass that plays both roles
(ADR-001). Each turn it scores every legal move with a weighted heuristic
(:mod:`actor_t6.heuristic_scoring`) and returns the best one — fast,
deterministic, and dependency-free of any learning state. It composes a
:class:`~actor_t6.belief_state.BeliefState` to cope with a hidden opponent.

Depends only on ``belief_state`` and ``config`` (never on ``qtable_actor``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from actor.base_actor import BaseActor
from game.constants import COP, DEFAULT_GRID_SIZE, THIEF

from actor_t6 import heuristic_scoring as scoring
from actor_t6.belief_state import BeliefState
from actor_t6.config import load_config

if TYPE_CHECKING:
    from game.state import ActionResult, ObservationState


class HeuristicActor(BaseActor):
    """Weighted-scoring actor for both the Cop and Thief roles."""

    def __init__(self, role: str | None = None, weights: dict | None = None,
                 grid_size: tuple[int, int] = DEFAULT_GRID_SIZE) -> None:
        """Create the actor with optional role, weight, and grid overrides.

        Args:
            role: ``"cop"`` or ``"thief"``; if ``None`` it is detected at
                runtime from ``obs.actor`` (FR-01.5).
            weights: Heuristic weight overrides; defaults come from
                ``config/actor_config.json`` (``heuristic`` section).
            grid_size: Board (cols, rows); defaults to the submodule's
                ``DEFAULT_GRID_SIZE`` physical constant.
        """
        self._role = role
        self._weights = weights or load_config()["heuristic"]
        self._grid = grid_size
        self._belief = BeliefState()

    def _target(self, obs: ObservationState) -> tuple[int, int] | None:
        """Return the best opponent-position estimate for this observation.

        Prefers the directly observed ``opponent_pos`` and falls back to the
        belief state's last sighting when the opponent is hidden.

        Args:
            obs: Current observation.

        Returns:
            Estimated opponent (col, row), or ``None`` if never seen.
        """
        self._belief.update(obs)
        if obs.opponent_pos is not None:
            return tuple(obs.opponent_pos)
        return self._belief.get_estimate()

    def get_action(self, obs: ObservationState) -> str:
        """Return the highest-scoring legal move (always within legal_moves).

        Args:
            obs: Current observation (its ``legal_moves`` bound the choice).

        Returns:
            The best action string from ``obs.legal_moves``.
        """
        role = self._role or obs.actor
        target = self._target(obs)
        barriers = {tuple(b) for b in obs.barriers}
        my_pos = tuple(obs.my_pos)
        return max(
            obs.legal_moves,
            key=lambda action: scoring.score_move(
                my_pos, action, target, role, self._weights, barriers, self._grid,
            ),
        )

    def on_result(self, obs: ObservationState, action: str,
                  result: ActionResult) -> None:
        """Refresh the belief state after an action resolves.

        Args:
            obs: Observation that led to the action.
            action: The submitted action (unused; kept for the contract).
            result: The engine's ActionResult (unused by the heuristic).
        """
        self._belief.update(obs)

    def save(self, path: Path | str) -> None:
        """Persist the heuristic weights as JSON (optional, FR-01.4).

        Args:
            path: Destination file path.
        """
        Path(path).write_text(json.dumps({"weights": self._weights}))

    @classmethod
    def load(cls, role: str, path: Path | str, **kwargs: object) -> HeuristicActor:
        """Load an actor, tolerating a missing weights file (cold start).

        The submodule's loader always supplies ``ACTOR_TABLE`` in actor mode,
        so this is called even when no weights file exists; in that case the
        default config weights are used.

        Args:
            role: ``"cop"`` or ``"thief"`` from the server.
            path: Path to a JSON weights file (may not exist).
            **kwargs: Extra constructor overrides (e.g. ``grid_size``).

        Returns:
            A ready-to-use ``HeuristicActor``.
        """
        weights = None
        p = Path(path)
        if p.exists():
            weights = json.loads(p.read_text()).get("weights")
        valid_role = role if role in (COP, THIEF) else None
        return cls(role=valid_role, weights=weights, **kwargs)
