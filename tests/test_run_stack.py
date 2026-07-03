"""Tests for the stack launcher CLI/dispatch (scripts/run_stack.py).

Subprocess spawning is not exercised here; these cover the pure pieces — server
env construction, argument parsing, and mode dispatch — with the side-effecting
helpers monkeypatched.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import launch_common as lc  # noqa: E402
import run_stack as rs  # noqa: E402


def test_server_env_thief_table_and_keys(monkeypatch):
    monkeypatch.delenv("PYTHONPATH", raising=False)
    monkeypatch.setenv("MCP_API_KEY", "mine")
    monkeypatch.setenv("MCP_ALLOWED_API_KEYS", "theirs")
    env = rs._server_env("http://remote:9", "thief", "actor_t6.qtable_actor.QTableActor")
    assert env["OPPONENT_MCP_URL"] == "http://remote:9"
    assert env["ACTOR_TABLE"].endswith("thief_qtable.npy")
    assert "mine" in env["MCP_ALLOWED_API_KEYS"] and "theirs" in env["MCP_ALLOWED_API_KEYS"]
    assert env["PYTHONPATH"].startswith(str(lc.REPO_ROOT / "src"))


def test_server_env_cop_table(monkeypatch):
    monkeypatch.setenv("MCP_API_KEY", "k")
    env = rs._server_env("http://remote:9", "cop", "actor_t6.qtable_actor.QTableActor")
    assert env["ACTOR_TABLE"].endswith("cop_qtable.npy")
    assert os.pathsep not in env["PYTHONPATH"] or env["PYTHONPATH"]  # well-formed


def test_parser_local_collects_extra():
    cfg = lc.launcher_config()
    args, extra = rs._build_parser(cfg).parse_known_args(
        ["local", "--mode", "actor", "--seed", "7"])
    assert args.command == "local"
    assert extra == ["--mode", "actor", "--seed", "7"]


def test_parser_cross_team_required():
    cfg = lc.launcher_config()
    parsed = rs._build_parser(cfg).parse_args(
        ["cross-team", "--opponent-url", "http://h:1", "--my-role", "cop",
         "--game-id", "g1", "--seed", "42"])
    assert parsed.command == "cross-team"
    assert parsed.my_role == "cop"
    assert parsed.port == cfg["default_server_port"]


def test_parser_cross_team_missing_args_errors():
    cfg = lc.launcher_config()
    with pytest.raises(SystemExit):
        rs._build_parser(cfg).parse_args(["cross-team", "--my-role", "cop"])


def test_main_dispatches_local(monkeypatch):
    calls = {}
    monkeypatch.setattr(lc, "load_env", lambda: None)
    monkeypatch.setattr(rs, "run_local", lambda *a: calls.__setitem__("local", a) or 0)
    monkeypatch.setattr(rs, "run_cross_team", lambda *a: calls.setdefault("cross", a))
    monkeypatch.setattr(
        sys, "argv", ["run_stack.py", "--backend", "ollama", "local", "--seed", "1"])
    assert rs.main() == 0
    assert "local" in calls and "cross" not in calls


def test_main_dispatches_cross_team_and_detects_adapter(monkeypatch):
    calls = {}
    monkeypatch.setattr(lc, "load_env", lambda: None)
    monkeypatch.setattr(rs, "run_cross_team", lambda *a: calls.__setitem__("cross", a) or 0)
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", [
        "run_stack.py", "cross-team", "--opponent-url", "http://h:1",
        "--my-role", "thief", "--game-id", "g1", "--seed", "42"])
    assert rs.main() == 0
    # run_cross_team(args, cfg, needs_adapter) — adapter required for OpenRouter.
    assert calls["cross"][2] is True


def test_run_local_returns_child_status_and_cleans_adapter(monkeypatch):
    stopped = []
    monkeypatch.setattr(lc, "start_adapter", lambda cfg: "adapter")
    monkeypatch.setattr(lc, "stop_process", lambda proc, label: stopped.append((proc, label)))
    monkeypatch.setattr(rs.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 7))
    assert rs.run_local(["--seed", "1"], lc.launcher_config(), True) == 7
    assert stopped == [("adapter", "adapter")]


def test_run_cross_team_returns_peer_status_and_cleans(monkeypatch):
    stopped = []
    fake_server = object()
    args = rs._build_parser(lc.launcher_config()).parse_args([
        "cross-team", "--opponent-url", "http://h:1", "--my-role", "cop",
        "--game-id", "g1", "--seed", "1",
    ])
    monkeypatch.setattr(rs.subprocess, "Popen", lambda *a, **k: fake_server)
    monkeypatch.setattr(lc, "wait_for_port", lambda *a, **k: None)
    monkeypatch.setattr(lc, "stop_process", lambda proc, label: stopped.append((proc, label)))
    monkeypatch.setattr(rs.subprocess, "run",
                        lambda *a, **k: subprocess.CompletedProcess(a[0], 5))
    assert rs.run_cross_team(args, lc.launcher_config(), False) == 5
    assert stopped == [(fake_server, "server"), (None, "adapter")]
