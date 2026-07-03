"""Tests for cross-team peer orchestration protocol glue."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import run_peer_match as rpm  # noqa: E402


class _Gatekeeper:
    def __init__(self, model=None) -> None:
        self.model = model


class _FakeClient:
    calls: list[tuple[str, dict]] = []

    def __init__(self, url: str, auth: object = None) -> None:
        self.url = url
        self.auth = auth

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args) -> None:
        return None

    async def call_tool(self, name: str, args: dict):
        self.calls.append((name, args))
        return SimpleNamespace(content=[SimpleNamespace(text="{}")])


class _FakeRunMatch:
    _SYSTEM_THIEF = "thief"
    _SYSTEM_COP = "cop"
    _API_KEY = "stale"

    @staticmethod
    def _derive_positions(seed, grid):
        return [0, 0], [1, 1]

    @staticmethod
    async def _propose_match(client, args):
        await client.call_tool("propose_match_tool", args)

    @staticmethod
    async def _actor_turn(*args):
        return {"success": True, "game_over": True, "winner": "cop"}


def test_play_forwards_canonical_proposal_values(monkeypatch, tmp_path):
    _FakeClient.calls = []
    mod = ModuleType("game.shared.gatekeeper")
    mod.Gatekeeper = _Gatekeeper
    monkeypatch.setitem(sys.modules, "game.shared.gatekeeper", mod)
    monkeypatch.setattr(rpm.mcp_client_loader, "client_auth",
                        lambda: (_FakeClient, lambda key: ("auth", key)))
    monkeypatch.setattr(rpm, "_run_match", lambda: _FakeRunMatch)
    monkeypatch.setenv("MCP_API_KEY", "fresh")
    result = asyncio.run(rpm.play(
        "http://local", "thief", "g1", 7, (5, 5), str(tmp_path),
        25, 1.0, 0.01, 1, 25, 3,
    ))
    payload = _FakeClient.calls[0][1]
    assert result["winner"] == "cop"
    assert payload["max_moves"] == 25
    assert payload["view_radius"] == 1
    assert payload["grid_size"] == [5, 5]


def test_play_allows_recoverable_forfeit(monkeypatch, tmp_path):
    calls = [{"forfeit": True, "reason": "timeout"},
             {"success": True, "game_over": True, "winner": "thief"}]

    class RunMatch(_FakeRunMatch):
        @staticmethod
        async def _actor_turn(*args):
            return calls.pop(0)

    mod = ModuleType("game.shared.gatekeeper")
    mod.Gatekeeper = _Gatekeeper
    monkeypatch.setitem(sys.modules, "game.shared.gatekeeper", mod)
    monkeypatch.setattr(rpm.mcp_client_loader, "client_auth",
                        lambda: (_FakeClient, lambda key: ("auth", key)))
    monkeypatch.setattr(rpm, "_run_match", lambda: RunMatch)
    monkeypatch.setattr(rpm.peer_sync, "wait_for_opponent",
                        lambda *a: asyncio.sleep(0, {"status": "moved"}))
    result = asyncio.run(rpm.play(
        "http://local", "thief", "g1", 7, (5, 5), str(tmp_path),
        25, 1.0, 0.01, 1, 25, 3,
    ))
    assert result["winner"] == "thief"


def test_play_reports_technical_loss_after_forfeit_threshold(monkeypatch, tmp_path):
    class RunMatch(_FakeRunMatch):
        @staticmethod
        async def _actor_turn(*args):
            return {"forfeit": True, "reason": "timeout"}

    mod = ModuleType("game.shared.gatekeeper")
    mod.Gatekeeper = _Gatekeeper
    monkeypatch.setitem(sys.modules, "game.shared.gatekeeper", mod)
    monkeypatch.setattr(rpm.mcp_client_loader, "client_auth",
                        lambda: (_FakeClient, lambda key: ("auth", key)))
    monkeypatch.setattr(rpm, "_run_match", lambda: RunMatch)
    monkeypatch.setattr(rpm.peer_sync, "wait_for_opponent",
                        lambda *a: asyncio.sleep(0, {"status": "moved"}))
    result = asyncio.run(rpm.play(
        "http://local", "thief", "g1", 7, (5, 5), str(tmp_path),
        25, 1.0, 0.01, 1, 25, 2,
    ))
    assert result == {"technical_loss": True, "reason": "consecutive_forfeits:thief"}
