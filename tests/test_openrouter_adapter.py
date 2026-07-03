"""Tests for the OpenRouter adapter's request/response translation.

The adapter is tooling (not part of the actor_brains package), but the protocol
translation is the one piece worth pinning down, so a match never breaks on a
malformed bridge. No network or API key is used — urlopen is monkeypatched.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import openrouter_adapter as adapter  # noqa: E402


class _FakeResp:
    def __init__(self, payload: dict) -> None:
        self._raw = json.dumps(payload).encode()

    def read(self) -> bytes:
        return self._raw

    def __enter__(self) -> _FakeResp:
        return self

    def __exit__(self, *_a: object) -> bool:
        return False


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        adapter._forward_to_openrouter({"model": "m", "messages": []})


def test_translates_request_and_response(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    captured: dict = {}

    def fake_urlopen(req, timeout=0):  # noqa: ANN001, ANN202
        captured["url"] = req.full_url
        captured["auth"] = req.headers.get("Authorization")
        captured["body"] = json.loads(req.data)
        return _FakeResp({
            "choices": [{"message": {"role": "assistant", "content": "Moving north"}}],
            "usage": {"prompt_tokens": 7, "completion_tokens": 2},
        })

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    out = adapter._forward_to_openrouter({
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "messages": [{"role": "user", "content": "Complete: Moving north___"}],
        "stream": False,
    })

    assert captured["url"].endswith("/chat/completions")
    assert captured["auth"] == "Bearer test-key"
    assert captured["body"]["model"] == "meta-llama/llama-3.2-3b-instruct:free"
    assert captured["body"]["stream"] is False
    # Ollama-shaped response so Gatekeeper._call_ollama works unchanged.
    assert out["message"]["content"] == "Moving north"
    assert out["prompt_eval_count"] == 7
    assert out["eval_count"] == 2
    assert out["done"] is True
