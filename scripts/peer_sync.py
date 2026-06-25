"""Turn-synchronisation helpers for the cross-team peer orchestrator.

In a cross-team match each side runs its own server + orchestrator and controls
only its own actor; the two engines stay in sync because ``take_action`` forwards
each move to the opponent's ``receive_action`` tool. This module isolates the
logic for *detecting the opponent's move* so it can be unit-tested without a live
opponent: the async waiter takes injected fetch/terminal callables.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable
from pathlib import Path

# Thief acts first within each round, matching run_match.py's loop order.
_TURN_ORDER: tuple[str, str] = ("thief", "cop")


def turn_order() -> tuple[str, str]:
    """Return the per-round acting order (thief, then cop)."""
    return _TURN_ORDER


def opponent_of(role: str) -> str:
    """Return the opposing role for ``role`` ("cop" <-> "thief")."""
    return "cop" if role == "thief" else "thief"


def state_fingerprint(obs: dict) -> tuple:
    """Build a hashable digest of an observation that changes on any move.

    Positions and barriers are included (not just ``round``) so the digest
    differs whether the opponent steps or places a barrier, regardless of how
    the engine increments its round counter.

    Args:
        obs: An ObservationState dict (as returned by the get_state tool).

    Returns:
        A hashable tuple summarising the observable state.
    """
    my_pos = obs.get("my_pos")
    opp_pos = obs.get("opponent_pos")
    return (
        obs.get("round"),
        tuple(my_pos) if my_pos is not None else None,
        tuple(opp_pos) if opp_pos is not None else None,
        tuple(sorted(tuple(b) for b in obs.get("barriers", []))),
    )


def read_terminal(games_base: Path | str, game_id: str) -> dict:
    """Return the terminal log entry for ``game_id``, or {} if not finished.

    Args:
        games_base: The server's games directory (e.g. ``games/server_a``).
        game_id: The active game identifier.

    Returns:
        The parsed terminal log dict, or an empty dict if the game is ongoing.
    """
    log_path = Path(games_base) / game_id / "game.log"
    if not log_path.exists():
        return {}
    for raw in reversed(log_path.read_text().splitlines()):
        if raw.strip():
            entry = json.loads(raw)
            if entry.get("type") == "terminal":
                return entry
    return {}


async def wait_for_opponent(
    fetch_state: Callable[[], Awaitable[dict]],
    terminal_check: Callable[[], dict],
    before: tuple,
    timeout: float,
    poll: float,
) -> dict:
    """Poll until the opponent's move lands, the game ends, or timeout elapses.

    Args:
        fetch_state: Async callable returning the latest ObservationState dict.
        terminal_check: Callable returning a terminal log dict (or {} if none).
        before: Fingerprint captured after our own move (the baseline to beat).
        timeout: Maximum seconds to wait for the opponent.
        poll: Seconds to sleep between polls.

    Returns:
        Dict with ``status`` in {"moved", "game_over", "timeout"} and a
        ``terminal`` dict (populated only when the game ended).
    """
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        terminal = terminal_check()
        if terminal:
            return {"status": "game_over", "terminal": terminal}
        obs = await fetch_state()
        if "error" not in obs and state_fingerprint(obs) != before:
            return {"status": "moved", "terminal": {}}
        await asyncio.sleep(poll)
    return {"status": "timeout", "terminal": {}}
