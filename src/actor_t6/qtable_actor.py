"""QTableActor — tabular Q-learning Cop/Thief backend (PRD §3.4 FR-03).

Replaces the submodule's ``RLActorBackend`` stub. Action selection is
epsilon-greedy over legal moves; learning is an off-policy Q-learning (Bellman)
update applied through ``on_result``. Because the live match path loads a fresh
actor every turn and never calls ``on_result``, learning happens offline in
``scripts/train_qtable.py``; matches load a trained table with epsilon=0.

Depends on ``state_encoder``, ``config`` (never on ``heuristic_actor``).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from actor.base_actor import BaseActor
from game.constants import BARRIER_ACTION, COP, DEFAULT_GRID_SIZE, DIRECTIONS

from actor_t6.config import load_config
from actor_t6.state_encoder import StateEncoder

if TYPE_CHECKING:
    from game.state import ActionResult, ObservationState

# Canonical action order for Q-table columns (PLAN §6.2).
ACTIONS: list[str] = [*DIRECTIONS, BARRIER_ACTION]
_ACTION_INDEX: dict[str, int] = {a: i for i, a in enumerate(ACTIONS)}


class QTableActor(BaseActor):
    """Epsilon-greedy tabular Q-learning actor for both roles."""

    def __init__(self, role: str | None = None, grid_size: tuple[int, int] = DEFAULT_GRID_SIZE,
                 **overrides: float) -> None:
        """Create with RL hyperparameters (config defaults, override per-key).

        Args:
            role: ``"cop"``/``"thief"``; detected from ``obs.actor`` if None.
            grid_size: Board (cols, rows) — fixes the Q-table shape.
            **overrides: Optional numeric overrides for any ``rl`` config key.
        """
        rl = {**load_config()["rl"], **overrides}
        self._role = role
        self._grid = grid_size
        self._alpha = rl["learning_rate"]
        self._gamma = rl["discount_factor"]
        self._epsilon = rl["epsilon_start"]
        self._eps_decay = rl["epsilon_decay"]
        self._eps_min = rl["epsilon_min"]
        self._rewards = (rl["win_reward"], rl["lose_reward"], rl["step_cost"])
        self._rng = np.random.default_rng()
        self.q_table = np.zeros((StateEncoder.num_states(grid_size), len(ACTIONS)))
        self._last: tuple[int, int] | None = None
        self._pending: tuple[int, int, float] | None = None

    @property
    def epsilon(self) -> float:
        """Current exploration rate."""
        return self._epsilon

    @epsilon.setter
    def epsilon(self, value: float) -> None:
        self._epsilon = float(value)

    def get_action(self, obs: ObservationState) -> str:
        """Select an epsilon-greedy legal action and flush any pending update.

        Args:
            obs: Current observation (its ``legal_moves`` bound the choice).

        Returns:
            An action string from ``obs.legal_moves``.
        """
        state = StateEncoder.encode(obs, self._grid)
        if self._pending is not None:
            self._bellman_bootstrap(state)
        if self._rng.random() < self._epsilon:
            chosen = obs.legal_moves[self._rng.integers(len(obs.legal_moves))]
        else:
            chosen = max(obs.legal_moves, key=lambda a: self.q_table[state, _ACTION_INDEX[a]])
        self._last = (state, _ACTION_INDEX[chosen])
        return chosen

    def on_result(self, obs: ObservationState, action: str, result: ActionResult) -> None:
        """Record reward; apply the terminal Bellman update at game over.

        Args:
            obs: Observation that led to the action.
            action: The submitted action.
            result: The engine's ActionResult.
        """
        if self._last is None:
            return
        state, act_idx = self._last
        reward = self._reward(obs.actor, result)
        if result.game_over:
            self.q_table[state, act_idx] += self._alpha * (reward - self.q_table[state, act_idx])
            self._pending = None
            self._last = None
            self._epsilon = max(self._eps_min, self._epsilon * self._eps_decay)
        else:
            self._pending = (state, act_idx, reward)

    def _bellman_bootstrap(self, next_state: int) -> None:
        """Apply Q(s,a) += α·(r + γ·max Q(s') − Q(s,a)) for the pending step."""
        state, act_idx, reward = self._pending
        target = reward + self._gamma * float(self.q_table[next_state].max())
        self.q_table[state, act_idx] += self._alpha * (target - self.q_table[state, act_idx])
        self._pending = None

    def _reward(self, me: str, result: ActionResult) -> float:
        """Return this actor's reward: win/lose at terminal, else a step cost."""
        win, lose, step = self._rewards
        if result.game_over:
            return win if result.winner == me else lose
        return -step if me == COP else step

    def save(self, path: Path | str) -> None:
        """Persist the Q-table as a ``.npy`` file (PLAN §6.2)."""
        np.save(str(path), self.q_table)

    @classmethod
    def load(cls, role: str, path: Path | str, **kwargs: object) -> QTableActor:
        """Load a Q-table (ε=0); tolerate a missing/mismatched file (cold start).

        Args:
            role: ``"cop"`` or ``"thief"`` from the server.
            path: ``.npy`` path (may be absent on a cold start).
            **kwargs: Extra constructor overrides (e.g. ``grid_size``).

        Returns:
            A ``QTableActor`` in pure-exploitation mode (epsilon=0).
        """
        actor = cls(role=role, **kwargs)
        p = Path(str(path))
        if not p.suffix:
            p = p.with_suffix(".npy")
        if p.exists():
            loaded = np.load(str(p))
            if loaded.shape == actor.q_table.shape:
                actor.q_table = loaded
        actor.epsilon = 0.0
        return actor
