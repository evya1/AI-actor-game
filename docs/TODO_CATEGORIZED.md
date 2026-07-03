# Categorized Task Tracking — Cop & Thief Actors

## Version 1.0 | 2026-06-25

> Derived from [TODO.md](TODO.md), [PLAN.md](PLAN.md), and [PRD.md](PRD.md).
> Current release status is maintained in [TODO.md](TODO.md); this categorized
> view has been synced for implemented actor and remediation work.

---

## 🔧 Infra

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 0.1 | Create `src/actor_t6/` package with `__init__.py` | P0 | Not Started | Package importable via `PYTHONPATH=../src` (see [PLAN §3 Modules](PLAN.md#3-independent-modules)) |
| 0.2 | Create `config/actor_config.json` with default weights | P0 | Not Started | JSON validates, all required keys present |
| 3.6 | Ruff lint — zero violations | P0 | Not Started | `ruff check src/` passes |
| 4.4 | README.md — scientific report | P1 | Not Started | DecPOMDP formalization, orchestration analysis, screenshots |

---

## 💻 Program

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 0.3 | Create `config.py` — config loader with schema validation | P0 | Done | Returns defaults for missing keys, raises on invalid types (see [PLAN §6.1 Config Schema](PLAN.md#61-actor-config-configactor_configjson)) |
| 1.1 | Create `belief_state.py` — point estimate tracker | P0 | Done | Updates on known `opponent_pos`, resets on canonical round regression or explicit reset, testable in isolation (see [PLAN §5.4 BeliefState API](PLAN.md#54-beliefstate)) |
| 1.2 | Create `heuristic_actor.py` — `HeuristicActor(BaseActor)` skeleton | P0 | Done | Passes `isinstance(actor, BaseActor)`, returns legal actions (see [PLAN §5.1 HeuristicActor API](PLAN.md#51-heuristicactor)) |
| 1.3 | Implement `_score_move()` — distance + barrier + edge + trap scoring | P0 | Done | Returns float scores, highest score = best move |
| 1.4 | Implement Cop strategy — pursuit + barrier placement logic | P0 | Done | Considers `BARRIER` when `barriers_remaining > 0`, prioritizes capture |
| 1.5 | Implement Thief strategy — evasion + trap avoidance | P0 | Done | Maximizes distance, avoids dead ends |
| 1.6 | Implement `on_result()` — belief state update + stats | P1 | Done | Belief state updated, no crashes |
| 1.7 | Implement `save()` / `load()` — weight persistence | P2 | Done | Saves/loads config, `load` returns valid actor |
| 2.1 | Create `state_encoder.py` — relative position + edge + barrier → int | P0 | Done | Encode all 9×9 relative positions, verify uniqueness, `num_states()` correct (see [PLAN §ADR-002](PLAN.md#adr-002-relative-position-encoding-for-q-table)) |
| 2.2 | Create `qtable_actor.py` — `QTableActor(BaseActor)` skeleton | P0 | Done | Passes `isinstance(actor, BaseActor)`, Q-table initialized to zeros (see [PLAN §5.2 QTableActor API](PLAN.md#52-qtableactor)) |
| 2.3 | Implement epsilon-greedy `get_action()` | P0 | Done | Returns random action with prob ε, best Q-action otherwise |
| 2.4 | Implement Bellman update in `on_result()` | P0 | Done | Q-values change correctly after reward, verified with unit test |
| 2.5 | Implement epsilon decay + floor | P1 | Done | ε decays each sub-game, never below `epsilon_min` |
| 2.6 | Implement `save()` — write Q-table to `.npy` | P0 | Done | File created, shape matches `(num_states, num_actions)` |
| 2.7 | Implement `load()` — read `.npy`, set ε=0 | P0 | Done | Loaded actor plays deterministically (ε=0) |
| 4.1 | Belief state integration with RL backend | P2 | Done | QTableActor uses belief state when `opponent_pos` is `None` |
| 4.3 | Learning curve visualization | P2 | Not Started | Graph of win rate vs. training episodes |
| 7.1 | Correct RL, actor, peer, launcher, and model artifacts after Fable review | P0 | Done | See `docs/CODE_REVIEW_REMEDIATION.md` and `docs/QTABLE_RETRAINING_REPORT.md` |

---

## 🧪 Testing

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 0.4 | Create `tests/` directory structure | P1 | Not Started | `pytest` discovers tests |
| 1.8 | Unit tests for `heuristic_actor` | P0 | Not Started | ≥ 85% coverage, all actions ∈ `legal_moves` |
| 2.8 | Unit tests for `qtable_actor` + `state_encoder` | P0 | Not Started | ≥ 85% coverage, Bellman update verified mathematically |
| 3.1 | Integration Step 1 — import + construct test | P0 | Not Started | No import errors from submodule context (see [PLAN §4 Step 1](PLAN.md#step-1--config--factory-no-game)) |
| 3.2 | Integration Step 2 — heuristic on 2×2 | P0 | Not Started | Game log shows completion, no illegal actions (see [PLAN §4 Step 2](PLAN.md#step-2--heuristic-on-22-smoke-test)) |
| 3.3 | Integration Step 3 — heuristic on 5×5 (6 sub-games) | P0 | Not Started | Total score > 30 (see [PLAN §4 Step 3](PLAN.md#step-3--heuristic-on-55-full-game)) |
| 3.4 | Integration Step 4 — QTableActor cold start | P0 | Not Started | Game completes, `.npy` files created (see [PLAN §4 Step 4](PLAN.md#step-4--qtableactor-cold-start-no-training)) |
| 3.5 | Integration Step 5 — QTableActor trained vs heuristic | P1 | Not Started | RL actor wins ≥ 50% of sub-games (see [PLAN §4 Step 5](PLAN.md#step-5--qtableactor-trained-exploitation-mode)) |
| 3.7 | Full test suite — ≥ 85% coverage | P0 | Not Started | `pytest --cov=actor_t6` passes threshold |
| 4.2 | Simulated partial observability tests | P2 | Not Started | Tests with artificially hidden `opponent_pos` pass |

---

## Summary

| Category | Count | P0 Tasks |
|----------|-------|----------|
| **Infra** | 4 | 3 |
| **Program** | 16 | 10 |
| **Testing** | 10 | 7 |
| **Total** | **30** | **20** |

---

### Legend

| Symbol | Meaning |
|--------|---------|
| P0 | Critical — must complete for submission |
| P1 | High — important for quality |
| P2 | Medium — nice to have / bonus |

---

*Document Version: 1.0*
*Last Updated: 2026-06-25*
