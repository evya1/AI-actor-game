# Q-table Retraining Report

Date: 2026-07-03

## Reason

The prior Q-tables were invalidated by two confirmed training defects:

- terminal self-play feedback reached only the actor that made the final move;
- Bellman targets bootstrapped from illegal next-state actions.

## Commands

Baseline hashes/evaluation and final evaluation used fixed seeds `1000..1049`.

Retraining command:

```sh
uv run python scripts/train_qtable.py --episodes 2000 --seed 42 --grid 5 --models-dir models
```

## Artifact Hashes

| Artifact | Old SHA-256 | New SHA-256 |
|---|---|---|
| `models/cop_qtable.npy` | `eee1a68142a5297067cca7c910dad53d16fde69c8f72d0e9e6004997acba3b03` | `7f3fccabe069de3e1876a04adcb32bc82ffd8c96ab9f7d3078503f811b96f36f` |
| `models/thief_qtable.npy` | `94bc3646c76824f98435bdffdafe791defe628da79365d146268250c08a1264b` | `8cd800faefad111aebb47fe5f8f286d2f6a855fd26c3089a6da0f94f337cfc82` |

Both new tables have shape `(649, 10)`, load through `QTableActor.load()`, run
with `epsilon = 0`, and contain no NaN or infinite values.

## Fixed-seed Evaluation

| Role under evaluation | Table | Wins | Losses | Mean rounds | Median rounds | Reasons |
|---|---|---:|---:|---:|---:|---|
| Cop vs heuristic thief | old | 8 | 42 | 21.40 | 25.0 | capture 8, thief_survived 42 |
| Cop vs heuristic thief | new | 9 | 41 | 20.94 | 25.0 | capture 9, thief_survived 41 |
| Thief vs heuristic cop | old | 25 | 25 | 13.28 | 14.0 | capture 25, thief_survived 25 |
| Thief vs heuristic cop | new | 45 | 5 | 22.66 | 25.0 | capture 5, thief_survived 45 |

These metrics are deterministic for the stated seeds and opponents. They are
evidence of corrected retraining, not a broad claim of strategic superiority.
