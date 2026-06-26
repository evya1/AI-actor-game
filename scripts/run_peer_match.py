"""Cross-team peer orchestrator — drives only the local side of a remote match.

Unlike run_match.py (which spawns and drives *both* local servers), a cross-team
match means you control one server and your partner controls the other. This
client drives only your actor's turns: on your turn it calls get_actor_action ->
builds the NL message via the Gatekeeper -> calls take_action (which forwards the
move to the opponent). Between your turns it waits for the opponent's move to be
applied locally via their receive_action call.

Run standalone (server already up) or via ``run_stack.py --mode cross-team``::

    uv run python scripts/run_peer_match.py --local-url http://localhost:8080 \
        --my-role thief --game-id match0042_sg01 --seed 42 --games-dir games/server_a
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

import launch_common
import peer_sync
from fastmcp import Client
from fastmcp.client.auth.bearer import BearerAuth

# run_match.py lives in the submodule's scripts dir (not an importable package),
# so add it to sys.path and reuse its building blocks. This guarantees identical
# start positions and turn behaviour to a partner who runs the same orchestrator.
_SUBMODULE_SCRIPTS = launch_common.REPO_ROOT / "agent-orchestration-course-t6-common" / "scripts"
if str(_SUBMODULE_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SUBMODULE_SCRIPTS))

import run_match  # noqa: E402


async def _safe_state(client: Client, actor: str, game_id: str) -> dict:
    """Fetch the local observation for ``actor`` as a dict ({} on empty body)."""
    res = await client.call_tool("get_state", {"game_id": game_id, "actor": actor})
    return json.loads(res.content[0].text if res.content else "{}")


def _classify(res: dict) -> dict | None:
    """Map a take_action result to a technical-loss sentinel, or None if fine."""
    if res.get("forfeit"):
        return {"technical_loss": True, "reason": res.get("reason")}
    if res.get("hash_match") is False:
        return {"technical_loss": True, "reason": "hash_mismatch"}
    if "comm_error" in res:
        return {"technical_loss": True, "reason": f"comm_error:{res['comm_error']}"}
    return None


async def play(
    local_url: str, my_role: str, game_id: str, seed: int,
    grid: tuple[int, int], games_dir: str,
    max_rounds: int, timeout: float, poll: float,
) -> dict:
    """Propose the match and drive the local side until the game ends.

    Args:
        local_url: Base URL of your own MCP server.
        my_role: "cop" or "thief" — the role you play this game.
        game_id: Agreed game identifier (must match the partner's).
        seed: Agreed seed; start positions are derived deterministically.
        grid: (cols, rows) board size.
        games_dir: Your server's games directory (for terminal-log reads).
        max_rounds: Round cap before declaring the game exhausted.
        timeout: Per-turn timeout in seconds (yours and the opponent wait).
        poll: Poll interval while waiting for the opponent's move.

    Returns:
        The final ActionResult/terminal dict, or a technical-loss sentinel.
    """
    from game.shared.gatekeeper import Gatekeeper

    gk = Gatekeeper(model=os.environ.get("LLM_MODEL") or None)
    cop_pos, thief_pos = run_match._derive_positions(seed, grid)
    system = run_match._SYSTEM_COP if my_role == "cop" else run_match._SYSTEM_THIEF
    base = launch_common.REPO_ROOT / games_dir
    auth = BearerAuth(run_match._API_KEY)
    async with Client(local_url + "/mcp", auth=auth) as c:
        await c.call_tool("propose_match_tool", {
            "game_id": game_id, "seed": seed, "cop_pos": cop_pos,
            "thief_pos": thief_pos, "grid_size": list(grid), "my_role": my_role,
        })
        print(f"[peer] match {game_id} proposed; my_role={my_role}")  # noqa: T201
        for round_num in range(1, max_rounds + 1):
            print(f"\n[round {round_num}]")  # noqa: T201
            for side in peer_sync.turn_order():
                if (term := peer_sync.read_terminal(base, game_id)):
                    return term
                if side == my_role:
                    res = await run_match._actor_turn(c, my_role, game_id, gk, system, timeout)
                    print(f"  {my_role}: {res}")  # noqa: T201
                    if (loss := _classify(res)) is not None:
                        return loss
                    if res.get("game_over"):
                        return res
                else:
                    before = peer_sync.state_fingerprint(await _safe_state(c, my_role, game_id))
                    out = await peer_sync.wait_for_opponent(
                        lambda: _safe_state(c, my_role, game_id),
                        lambda: peer_sync.read_terminal(base, game_id),
                        before, timeout, poll,
                    )
                    print(f"  opponent: {out['status']}")  # noqa: T201
                    if out["status"] == "game_over":
                        return out["terminal"]
                    if out["status"] == "timeout":
                        return {"technical_loss": True, "reason": "opponent_timeout"}
    return peer_sync.read_terminal(base, game_id) or {"reason": "max_rounds"}


def main() -> None:
    """Parse CLI args, load env, and run one cross-team sub-game."""
    launch_common.load_env()
    cfg = launch_common.launcher_config()
    grid_cfg = run_match._load_config().get("grid_size", [5, 5])
    parser = argparse.ArgumentParser(description="Cross-team peer orchestrator (local side)")
    parser.add_argument("--local-url", default=f"http://localhost:{cfg['default_server_port']}")
    parser.add_argument("--my-role", choices=["cop", "thief"], required=True)
    parser.add_argument("--game-id", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--games-dir", default=cfg["default_games_dir"])
    parser.add_argument("--max-rounds", type=int, default=30)
    parser.add_argument("--turn-timeout", type=float, default=30.0)
    args = parser.parse_args()
    result = asyncio.run(play(
        args.local_url, args.my_role, args.game_id, args.seed,
        (grid_cfg[0], grid_cfg[1]), args.games_dir,
        args.max_rounds, args.turn_timeout, float(cfg["turn_poll_interval"]),
    ))
    print(f"\n[peer] result: {result}")  # noqa: T201


if __name__ == "__main__":
    main()
