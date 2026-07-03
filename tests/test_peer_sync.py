"""Tests for cross-team turn-sync helpers (scripts/peer_sync.py).

The async waiter is exercised with injected fake fetch/terminal callables, so no
live opponent or MCP server is needed.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import peer_sync as ps  # noqa: E402


def test_turn_order_and_opponent():
    assert ps.turn_order() == ("thief", "cop")
    assert ps.opponent_of("thief") == "cop"
    assert ps.opponent_of("cop") == "thief"


def test_fingerprint_changes_on_opponent_move():
    base = {"round": 1, "my_pos": [0, 0], "opponent_pos": None, "barriers": []}
    moved = {"round": 1, "my_pos": [0, 0], "opponent_pos": [2, 2], "barriers": []}
    assert ps.state_fingerprint(base) != ps.state_fingerprint(moved)


def test_fingerprint_changes_on_barrier():
    base = {"round": 2, "my_pos": [1, 1], "opponent_pos": [3, 3], "barriers": []}
    walled = {"round": 2, "my_pos": [1, 1], "opponent_pos": [3, 3], "barriers": [[2, 2]]}
    assert ps.state_fingerprint(base) != ps.state_fingerprint(walled)


def test_fingerprint_stable_for_equal_state():
    obs = {"round": 3, "my_pos": [1, 1], "opponent_pos": [3, 3], "barriers": [[2, 2]]}
    assert ps.state_fingerprint(dict(obs)) == ps.state_fingerprint(dict(obs))


def test_read_terminal_returns_entry(tmp_path):
    game_dir = tmp_path / "g1"
    game_dir.mkdir()
    (game_dir / "game.log").write_text(
        json.dumps({"type": "action"}) + "\n"
        + json.dumps({"type": "terminal", "winner": "cop"}) + "\n"
    )
    assert ps.read_terminal(tmp_path, "g1")["winner"] == "cop"


def test_read_terminal_empty_when_ongoing(tmp_path):
    game_dir = tmp_path / "g2"
    game_dir.mkdir()
    (game_dir / "game.log").write_text(json.dumps({"type": "action"}) + "\n")
    assert ps.read_terminal(tmp_path, "g2") == {}
    assert ps.read_terminal(tmp_path, "missing") == {}


def test_read_terminal_ignores_one_torn_trailing_line(tmp_path):
    game_dir = tmp_path / "g3"
    game_dir.mkdir()
    (game_dir / "game.log").write_text(
        json.dumps({"type": "terminal", "winner": "cop"}) + "\n"
        + '{"type": "terminal"'
    )
    assert ps.read_terminal(tmp_path, "g3")["winner"] == "cop"


def test_read_terminal_raises_on_persistent_corruption(tmp_path):
    game_dir = tmp_path / "g4"
    game_dir.mkdir()
    (game_dir / "game.log").write_text(
        json.dumps({"type": "terminal", "winner": "cop"}) + "\n"
        + "{bad\n{also_bad"
    )
    with pytest.raises(json.JSONDecodeError):
        ps.read_terminal(tmp_path, "g4")


def test_log_position_counts_nonblank_lines(tmp_path):
    game_dir = tmp_path / "g5"
    game_dir.mkdir()
    (game_dir / "game.log").write_text("\n{}\n {bad\n")
    assert ps.log_position(tmp_path, "g5") == 2


def _run(coro):
    return asyncio.run(coro)


def test_wait_for_opponent_detects_move():
    start = {"round": 1, "my_pos": [0, 0], "opponent_pos": None, "barriers": []}
    before = ps.state_fingerprint(start)

    async def fetch():
        return {"round": 1, "my_pos": [0, 0], "opponent_pos": [1, 1], "barriers": []}

    out = _run(ps.wait_for_opponent(fetch, lambda: {}, before, timeout=1.0, poll=0.01))
    assert out["status"] == "moved"


def test_wait_for_opponent_detects_game_over():
    async def fetch():
        return {"round": 1, "my_pos": [0, 0], "opponent_pos": None, "barriers": []}

    out = _run(ps.wait_for_opponent(
        fetch, lambda: {"type": "terminal", "winner": "thief"}, before=(), timeout=1.0, poll=0.01))
    assert out["status"] == "game_over"
    assert out["terminal"]["winner"] == "thief"


def test_wait_for_opponent_times_out():
    same = {"round": 1, "my_pos": [0, 0], "opponent_pos": [2, 2], "barriers": []}
    before = ps.state_fingerprint(same)

    async def fetch():
        return dict(same)

    out = _run(ps.wait_for_opponent(fetch, lambda: {}, before, timeout=0.1, poll=0.02))
    assert out["status"] == "timeout"


def test_wait_for_opponent_uses_log_position_marker():
    start = {"round": 1, "my_pos": [0, 0], "opponent_pos": None, "barriers": []}

    async def fetch():
        return dict(start)

    out = _run(ps.wait_for_opponent(
        fetch, lambda: {}, ps.state_fingerprint(start), timeout=1.0, poll=0.01,
        log_check=lambda: 4, min_log_position=4,
    ))
    assert out["status"] == "moved"
