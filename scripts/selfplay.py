"""Offline self-play harness driving the submodule's Game engine directly.

The submodule's match path loads a *fresh* actor every turn and never calls
``on_result`` (see ``mcp_agent_tools.get_actor_action``), so online learning and
multi-turn validation are impossible through ``run_match.py``. This harness
fills that gap: it instantiates :class:`game.game.Game`, drives full sub-games
between two persistent actors, and (optionally) delivers ``on_result`` feedback
— enabling both integration smoke tests and offline Q-learning training.

This is tooling, not part of the ``actor_t6`` package contract.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Make the read-only submodule engine importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SUBMODULE_SRC = _REPO_ROOT / "agent-orchestration-course-t6-common" / "src"
if str(_SUBMODULE_SRC) not in sys.path:
    sys.path.insert(0, str(_SUBMODULE_SRC))

from game.game import Game  # noqa: E402

if TYPE_CHECKING:
    from actor.base_actor import BaseActor
    from game.state import ActionResult


def derive_positions(seed: int, grid: tuple[int, int]) -> tuple[tuple, tuple]:
    """Derive distinct cop/thief start cells deterministically from a seed.

    Mirrors ``run_match._derive_positions`` so offline games match online ones.

    Args:
        seed: RNG seed.
        grid: Grid (cols, rows).

    Returns:
        A ``(cop_pos, thief_pos)`` tuple of distinct cells.
    """
    rng = random.Random(seed)
    cols, rows = grid
    cop = (rng.randrange(cols), rng.randrange(rows))
    thief = cop
    while thief == cop:
        thief = (rng.randrange(cols), rng.randrange(rows))
    return cop, thief


def play_game(cop: BaseActor, thief: BaseActor, *, grid: tuple[int, int],
              cop_pos: tuple[int, int], thief_pos: tuple[int, int],
              max_rounds: int = 25, learn: bool = False) -> ActionResult:
    """Play one sub-game to termination and return the final ActionResult.

    Each round the thief then the cop observe, act, and (if ``learn``) receive
    ``on_result`` feedback. Every chosen action is asserted legal.

    Args:
        cop: Actor controlling the cop.
        thief: Actor controlling the thief.
        grid: Grid (cols, rows).
        cop_pos: Cop start cell.
        thief_pos: Thief start cell.
        max_rounds: Round cap (thief survives if reached).
        learn: When True, call ``on_result`` after each action.

    Returns:
        The terminal ActionResult (game_over True, or the last result at cap).
    """
    game = Game.new("selfplay", grid, cop_pos, thief_pos, {"max_moves": max_rounds})
    last: ActionResult | None = None
    for _ in range(max_rounds + 2):
        if game.to_dict()["game_over"]:
            break
        for actor, brain in (("thief", thief), ("cop", cop)):
            if game.to_dict()["game_over"]:
                break
            obs = game.get_state(actor)
            action = brain.get_action(obs)
            assert action in obs.legal_moves, f"illegal {action} not in {obs.legal_moves}"
            result = game.submit_action(actor, action)
            assert result.success, result.error
            if learn:
                brain.on_result(obs, action, result)
            last = result
    return last  # type: ignore[return-value]
