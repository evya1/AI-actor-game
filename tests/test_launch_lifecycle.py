"""Focused launcher lifecycle failure-path tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import launch_common as lc  # noqa: E402


class _FakeProc:
    def __init__(self, alive=True) -> None:
        self.pid = 123
        self._alive = alive
        self.terminated = False
        self.waited = False
        self.killed = False

    def poll(self):
        return None if self._alive else 0

    def terminate(self) -> None:
        self.terminated = True
        self._alive = False

    def wait(self, timeout=None) -> None:
        self.waited = True

    def kill(self) -> None:
        self.killed = True
        self._alive = False


def test_start_adapter_cleans_up_when_readiness_fails(monkeypatch):
    fake = _FakeProc()

    def fail_ready(*args, **kwargs):
        raise RuntimeError("no")

    monkeypatch.setattr(lc.subprocess, "Popen", lambda *a, **k: fake)
    monkeypatch.setattr(lc, "wait_for_port", fail_ready)
    with pytest.raises(RuntimeError, match="no"):
        lc.start_adapter(lc.launcher_config())
    assert fake.terminated and fake.waited


def test_stop_process_kills_after_timeout():
    fake = _FakeProc()

    def wait(timeout=None):
        if not fake.killed:
            raise lc.subprocess.TimeoutExpired("cmd", timeout)
        fake.waited = True

    fake.wait = wait
    lc.stop_process(fake, "x")
    assert fake.terminated and fake.killed and fake.waited


def test_wait_for_port_fails_when_process_exits():
    proc = _FakeProc(alive=False)
    with pytest.raises(RuntimeError, match="process exited"):
        lc.wait_for_port("127.0.0.1", 9, timeout=0.1, proc=proc)
