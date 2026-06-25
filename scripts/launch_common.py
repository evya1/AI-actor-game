"""Shared, dependency-free launcher helpers for run_stack / run_peer_match.

These run from the *main* repo's environment (numpy + stdlib only), while the
game stack (run_match, mcp_server, Gatekeeper) lives in the submodule's own uv
environment. So this module avoids third-party imports entirely: it parses
``.env`` and config with the stdlib and launches game processes with the
submodule interpreter (:func:`submodule_python`).
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SUBMODULE_ROOT = REPO_ROOT / "agent-orchestration-course-t6-common"

# Fallback launcher settings, mirrored in config/actor_config.json. Used only
# when the file omits the section so the launcher never hard-fails on config.
_LAUNCHER_DEFAULTS: dict = {
    "adapter_host": "localhost",
    "adapter_port": 11500,
    "adapter_script": "scripts/openrouter_adapter.py",
    "adapter_ready_timeout": 20.0,
    "local_server_ports": [8001, 8002],
    "default_server_port": 8080,
    "default_games_dir": "games/server_a",
    "turn_poll_interval": 0.5,
}


def launcher_config() -> dict:
    """Return the ``launcher`` config section with built-in fallbacks."""
    cfg_path = REPO_ROOT / "config" / "actor_config.json"
    section: dict = {}
    if cfg_path.exists():
        section = json.loads(cfg_path.read_text()).get("launcher", {})
    return {**_LAUNCHER_DEFAULTS, **section}


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a ``.env`` file into a dict (stdlib; ignores comments/blank lines)."""
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, val = stripped.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def load_env() -> None:
    """Populate os.environ from the main and submodule ``.env`` files.

    Both are loaded so the OpenRouter adapter and the Gatekeeper find their keys
    wherever they live. Existing environment values always win (setdefault).
    """
    for env_path in (REPO_ROOT / ".env", SUBMODULE_ROOT / ".env"):
        for key, val in _parse_env_file(env_path).items():
            os.environ.setdefault(key, val)


def submodule_cmd(args: list[str]) -> list[str]:
    """Wrap a command to run under the submodule's uv environment.

    The game stack (fastmcp, dotenv, the ``game`` package) lives in the
    submodule's project, so its processes must run there — not in the main repo's
    minimal env. ``uv run --project`` resolves/creates that env on demand.

    Args:
        args: The command tail, e.g. ``["python", "-m", "game.wrappers.mcp_server"]``.

    Returns:
        The full ``uv run --project <submodule> ...`` argument list.
    """
    return ["uv", "run", "--project", str(SUBMODULE_ROOT), *args]


def select_backend(choice: str, env: dict) -> str:
    """Resolve the effective LLM backend from an explicit choice or env vars.

    Args:
        choice: One of ``auto``, ``openrouter``, ``ollama``, ``anthropic``.
        env: Environment mapping to inspect when ``choice`` is ``auto``.

    Returns:
        The resolved backend name (never ``auto``).
    """
    if choice != "auto":
        return choice
    if env.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if env.get("OPENROUTER_API_KEY"):
        return "openrouter"
    return "ollama"


def wait_for_port(host: str, port: int, timeout: float) -> None:
    """Block until a TCP connection to host:port succeeds or timeout elapses.

    A socket probe is used (not HTTP) so a readiness check never triggers a real
    LLM call on the adapter, nor needs an HTTP client dependency.

    Args:
        host: Target host.
        port: Target port.
        timeout: Maximum seconds to wait.

    Raises:
        RuntimeError: If the port is not accepting connections in time.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2.0):
                return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"{host}:{port} did not become reachable within {timeout}s")


def start_adapter(cfg: dict) -> subprocess.Popen:
    """Start the (stdlib-only) OpenRouter adapter and wait until it is ready."""
    script = str(REPO_ROOT / cfg["adapter_script"])
    proc = subprocess.Popen([sys.executable, script], cwd=str(REPO_ROOT))
    print(f"[run_stack] starting OpenRouter adapter (pid {proc.pid})")  # noqa: T201
    wait_for_port(cfg["adapter_host"], int(cfg["adapter_port"]),
                  float(cfg["adapter_ready_timeout"]))
    print(f"[run_stack] adapter ready on {cfg['adapter_host']}:{cfg['adapter_port']}")  # noqa: T201
    return proc


def stop_process(proc: subprocess.Popen | None, label: str) -> None:
    """Terminate a subprocess if running and wait for it to exit."""
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    proc.wait()
    print(f"[run_stack] {label} stopped")  # noqa: T201
