"""Tests for the dependency-free launcher helpers (scripts/launch_common.py).

These pin the pure logic — backend selection, .env/config parsing, the submodule
command wrapper, and the socket readiness probe — without spawning real game
processes (Popen is monkeypatched).
"""

from __future__ import annotations

import socket
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import launch_common as lc  # noqa: E402


@pytest.mark.parametrize(("choice", "env", "expected"), [
    ("auto", {}, "ollama"),
    ("auto", {"OPENROUTER_API_KEY": "k"}, "openrouter"),
    ("auto", {"ANTHROPIC_API_KEY": "k", "OPENROUTER_API_KEY": "k"}, "anthropic"),
    ("ollama", {"OPENROUTER_API_KEY": "k"}, "ollama"),
    ("openrouter", {}, "openrouter"),
])
def test_select_backend(choice, env, expected):
    assert lc.select_backend(choice, env) == expected


def test_submodule_cmd_wraps_with_uv_project():
    cmd = lc.submodule_cmd(["python", "-m", "x"])
    assert cmd[:3] == ["uv", "run", "--project"]
    assert cmd[3] == str(lc.SUBMODULE_ROOT)
    assert cmd[-3:] == ["python", "-m", "x"]


def test_parse_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('# comment\nFOO=bar\nQUOTED="baz"\n\nNO_EQUALS\nKEY = spaced \n')
    parsed = lc._parse_env_file(env_file)
    assert parsed == {"FOO": "bar", "QUOTED": "baz", "KEY": "spaced"}


def test_parse_env_file_missing(tmp_path):
    assert lc._parse_env_file(tmp_path / "absent.env") == {}


def test_launcher_config_has_defaults_when_section_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(lc, "REPO_ROOT", tmp_path)
    cfg = lc.launcher_config()
    assert cfg["adapter_port"] == 11500
    assert cfg["default_server_port"] == 8080


def test_launcher_config_reads_repo_config():
    cfg = lc.launcher_config()
    assert "adapter_host" in cfg and "turn_poll_interval" in cfg


def test_wait_for_port_succeeds_on_listening_socket():
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()
    port = listener.getsockname()[1]
    try:
        lc.wait_for_port("127.0.0.1", port, timeout=2.0)  # returns without raising
    finally:
        listener.close()


def test_wait_for_port_times_out_on_closed_port():
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()  # port now free => connections refused
    with pytest.raises(RuntimeError, match="did not become reachable"):
        lc.wait_for_port("127.0.0.1", port, timeout=0.3)


class _FakeProc:
    def __init__(self, pid=123, alive=True):
        self.pid = pid
        self._alive = alive
        self.terminated = False
        self.waited = False
        self.killed = False

    def poll(self):
        return None if self._alive else 0

    def terminate(self):
        self.terminated = True
        self._alive = False

    def wait(self, timeout=None):
        self.waited = True

    def kill(self):
        self.killed = True
        self._alive = False


def test_start_adapter_launches_and_waits(monkeypatch):
    fake = _FakeProc()
    seen = {}
    monkeypatch.setattr(lc.subprocess, "Popen",
                        lambda *a, **k: seen.setdefault("env", k["env"]) and fake)
    monkeypatch.setattr(lc, "wait_for_port", lambda *a, **k: None)
    cfg = lc.launcher_config()
    assert lc.start_adapter(cfg) is fake
    assert seen["env"]["ADAPTER_PORT"] == str(cfg["adapter_port"])
    assert seen["env"]["OLLAMA_BASE_URL"].endswith(f":{cfg['adapter_port']}")


def test_stop_process_terminates_running():
    fake = _FakeProc()
    lc.stop_process(fake, "adapter")
    assert fake.terminated and fake.waited


def test_stop_process_noop_when_none_or_dead():
    lc.stop_process(None, "x")  # no error
    dead = _FakeProc(alive=False)
    lc.stop_process(dead, "x")
    assert dead.terminated is False
