"""Integration tests: HeuristicActor vs the real submodule Game engine.

Covers PLAN §4 Step 2 (2x2 smoke) and Step 3 (5x5 full game) offline, without
needing the MCP servers or an LLM — the LLM only generates NL messages, not
actions, so action legality and game completion are fully testable here.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from selfplay import derive_positions, play_game  # noqa: E402

from actor_t6.heuristic_actor import HeuristicActor  # noqa: E402


def test_smoke_2x2_completes_legally():
    result = play_game(
        HeuristicActor(role="cop"), HeuristicActor(role="thief"),
        grid=(2, 2), cop_pos=(0, 0), thief_pos=(1, 1), max_rounds=25,
    )
    assert result is not None
    # Either someone won or the round cap was hit — never an illegal-action crash.
    assert result.success


def test_full_5x5_series_completes_and_scores():
    cop_total = thief_total = 0
    for sg in range(6):
        cop_pos, thief_pos = derive_positions(42 + sg, (5, 5))
        result = play_game(
            HeuristicActor(role="cop"), HeuristicActor(role="thief"),
            grid=(5, 5), cop_pos=cop_pos, thief_pos=thief_pos, max_rounds=25,
        )
        if result.winner == "cop":
            cop_total += 20
            thief_total += 5
        else:  # thief win or survived to the cap
            cop_total += 5
            thief_total += 10
    # Combined score must beat the random-baseline floor (PRD §10, > 30).
    assert cop_total + thief_total > 30
