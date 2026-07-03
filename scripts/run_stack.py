"""One-command launcher for the Cop & Thief LLM stack.

The MCP server never calls the LLM itself — the Gatekeeper lives in the
orchestrator/client. This launcher wires the missing pieces together so an
OpenRouter (or Ollama/Anthropic) match "just works". It is stdlib-only and runs
from the main repo; the game processes run under the submodule interpreter.

* ``local``      — boot the adapter, then run_match.py (spawns both servers + the
                   LLM orchestrator). Forwards any extra args to run_match.
* ``cross-team`` — boot the adapter + your own MCP server (pointed at a remote
                   opponent), then drive your side via run_peer_match.

Examples::

    uv run python scripts/run_stack.py local --mode actor --seed 42
    uv run python scripts/run_stack.py cross-team --opponent-url http://host:port \
        --my-role thief --game-id m42_sg01 --seed 42
"""

from __future__ import annotations

import argparse
import os
import subprocess

import launch_common

# The submodule's run_match.py hard-codes a stale --actor-class default, so we
# always pass our own package's dotted path (both launch modes) rather than
# relying on that default.
DEFAULT_ACTOR_CLASS = "actor_brains.qtable_actor.QTableActor"


def _server_env(opponent_url: str, my_role: str, actor_class: str) -> dict:
    """Build the env for the local MCP server subprocess (cross-team mode).

    Mirrors run_match.py's actor-mode env: opponent URL, MCP auth keys, and the
    actor backend (with main ``src`` on PYTHONPATH so actor_brains is importable).

    Args:
        opponent_url: Base URL of the remote partner's server.
        my_role: "cop" or "thief" — selects the Q-table file.
        actor_class: Dotted path for the ACTOR_CLASS backend.

    Returns:
        A complete environment mapping for the server subprocess.
    """
    api = os.environ.get("MCP_API_KEY", "demo-key")
    allowed = {k for k in os.environ.get("MCP_ALLOWED_API_KEYS", "").split(",") if k} | {api}
    existing = os.environ.get("PYTHONPATH", "")
    parent_src = str(launch_common.REPO_ROOT / "src")
    table = "cop_qtable.npy" if my_role == "cop" else "thief_qtable.npy"
    return {
        **os.environ,
        "OPPONENT_MCP_URL": opponent_url,
        "MCP_API_KEY": api,
        "MCP_ALLOWED_API_KEYS": ",".join(sorted(allowed)),
        "ACTOR_CLASS": actor_class,
        "ACTOR_TABLE": str(launch_common.REPO_ROOT / "models" / table),
        "PYTHONPATH": parent_src + (os.pathsep + existing if existing else ""),
    }


def run_local(extra: list[str], cfg: dict, needs_adapter: bool) -> int:
    """Start the adapter (if needed) and run the submodule run_match.py."""
    adapter = launch_common.start_adapter(cfg) if needs_adapter else None
    try:
        script = launch_common.SUBMODULE_ROOT / "scripts" / "run_match.py"
        if not any(a == "--actor-class" or a.startswith("--actor-class=") for a in extra):
            extra = [*extra, "--actor-class", DEFAULT_ACTOR_CLASS]
        result = subprocess.run(launch_common.submodule_cmd(["python", str(script), *extra]),
                                cwd=str(launch_common.REPO_ROOT), check=False)
        return int(result.returncode)
    finally:
        launch_common.stop_process(adapter, "adapter")


def run_cross_team(args: argparse.Namespace, cfg: dict, needs_adapter: bool) -> int:
    """Start the adapter + own server, then drive the local side vs a remote peer."""
    adapter = launch_common.start_adapter(cfg) if needs_adapter else None
    server: subprocess.Popen | None = None
    try:
        server = subprocess.Popen(
            launch_common.submodule_cmd(
                ["python", "-m", "game.wrappers.mcp_server",
                 "--port", str(args.port), "--games-dir", args.games_dir]),
            env=_server_env(args.opponent_url, args.my_role, args.actor_class),
            cwd=str(launch_common.REPO_ROOT),
        )
        launch_common.wait_for_port(cfg["adapter_host"], args.port,
                                    float(cfg["adapter_ready_timeout"]), server)
        print(f"[run_stack] local server up on port {args.port}")  # noqa: T201
        peer = launch_common.REPO_ROOT / "scripts" / "run_peer_match.py"
        result = subprocess.run(
            launch_common.submodule_cmd(
                ["python", str(peer), "--local-url", f"http://localhost:{args.port}",
                 "--my-role", args.my_role, "--game-id", args.game_id,
                 "--seed", str(args.seed), "--games-dir", args.games_dir,
                 "--max-rounds", str(args.max_rounds), "--turn-timeout", str(args.turn_timeout)]),
            cwd=str(launch_common.REPO_ROOT), env=os.environ.copy(), check=False,
        )
        return int(result.returncode)
    finally:
        launch_common.stop_process(server, "server")
        launch_common.stop_process(adapter, "adapter")


def _build_parser(cfg: dict) -> argparse.ArgumentParser:
    """Construct the CLI with ``local`` and ``cross-team`` subcommands."""
    parser = argparse.ArgumentParser(description="Cop & Thief stack launcher")
    parser.add_argument("--backend", choices=["auto", "openrouter", "ollama", "anthropic"],
                        default="auto", help="LLM backend; auto-detects from env keys")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("local", help="run_match.py (unrecognised args are forwarded)")
    ct = sub.add_parser("cross-team", help="drive local side vs a remote opponent")
    ct.add_argument("--opponent-url", required=True)
    ct.add_argument("--my-role", choices=["cop", "thief"], required=True)
    ct.add_argument("--game-id", required=True)
    ct.add_argument("--seed", type=int, required=True)
    ct.add_argument("--port", type=int, default=cfg["default_server_port"])
    ct.add_argument("--games-dir", default=cfg["default_games_dir"])
    ct.add_argument("--actor-class", default=DEFAULT_ACTOR_CLASS)
    ct.add_argument("--max-rounds", type=int, default=30)
    ct.add_argument("--turn-timeout", type=float, default=30.0)
    return parser


def main() -> int:
    """Resolve the backend and dispatch to the requested launch mode."""
    launch_common.load_env()
    cfg = launch_common.launcher_config()
    args, extra = _build_parser(cfg).parse_known_args()
    backend = launch_common.select_backend(args.backend, dict(os.environ))
    needs_adapter = backend == "openrouter"
    print(f"[run_stack] backend={backend} adapter={'yes' if needs_adapter else 'no'}")  # noqa: T201
    if args.command == "local":
        return run_local(extra, cfg, needs_adapter)
    return run_cross_team(args, cfg, needs_adapter)


if __name__ == "__main__":
    raise SystemExit(main())
