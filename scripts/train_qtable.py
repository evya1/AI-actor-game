"""Offline Q-learning trainer for the QTableActor.

Runs many self-play episodes against a HeuristicActor opponent, applying Bellman
updates via ``on_result`` (which the live match path never does), then saves
``models/cop_qtable.npy`` and ``models/thief_qtable.npy`` for exploitation play.

Usage:
    uv run python scripts/train_qtable.py [--episodes N] [--seed S] [--grid 5]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (_REPO_ROOT / "src", _REPO_ROOT / "agent-orchestration-course-t6-common" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from selfplay import derive_positions, play_game  # noqa: E402

from actor_t6.heuristic_actor import HeuristicActor  # noqa: E402
from actor_t6.qtable_actor import QTableActor  # noqa: E402


def train(episodes: int, seed: int, grid: tuple[int, int]) -> dict[str, QTableActor]:
    """Train cop and thief Q-table actors via self-play vs the heuristic.

    Each role learns against a heuristic opponent so the learner sees a
    competent, stationary policy. The learning actor keeps its state across
    episodes (epsilon decays); the heuristic side is rebuilt per game.

    Args:
        episodes: Number of training games per role.
        seed: Base RNG seed for start positions.
        grid: Grid (cols, rows).

    Returns:
        Mapping ``{"cop": QTableActor, "thief": QTableActor}`` post-training.
    """
    cop_learner = QTableActor(role="cop", grid_size=grid)
    thief_learner = QTableActor(role="thief", grid_size=grid)
    for ep in range(episodes):
        cop_pos, thief_pos = derive_positions(seed + ep, grid)
        play_game(cop_learner, HeuristicActor(role="thief"),
                  grid=grid, cop_pos=cop_pos, thief_pos=thief_pos, learn=True)
        play_game(HeuristicActor(role="cop"), thief_learner,
                  grid=grid, cop_pos=cop_pos, thief_pos=thief_pos, learn=True)
    return {"cop": cop_learner, "thief": thief_learner}


def main() -> None:
    """Parse CLI args, train both actors, and save their Q-tables."""
    parser = argparse.ArgumentParser(description="Train QTableActor via self-play.")
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--grid", type=int, default=5)
    parser.add_argument("--models-dir", default=str(_REPO_ROOT / "models"))
    args = parser.parse_args()

    grid = (args.grid, args.grid)
    actors = train(args.episodes, args.seed, grid)
    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)
    for role, actor in actors.items():
        actor.save(models_dir / f"{role}_qtable.npy")
    print(f"[train] saved cop/thief Q-tables to {models_dir} after {args.episodes} episodes")


if __name__ == "__main__":
    main()
