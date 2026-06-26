# Task Tracking — Cop & Thief Actors

## Version 2.1 | 2026-06-25

> **Change from v1.0:** Tests distributed across phases. Each phase ends with unit tests for its modules, so nothing is tested all at once. Original grouped version preserved in [TODO_ORIGINAL.md](TODO_ORIGINAL.md).

## Implementation Status (v2.1)

- ✅ **Phase 0 — Setup:** `actor_t6` package, `config/actor_config.json`, `config.py` (defaults + schema validation), `shared/version.py` (1.00), `pyproject.toml` (numpy, ruff, pytest). Tests pass.
- ✅ **Phase 1 — Heuristic:** `belief_state.py`, `heuristic_actor.py` (+ `heuristic_scoring.py` extracted for the 150-line limit), role-aware Cop/Thief scoring, save/load tolerant of a missing file. Unit + integration tests pass on the real engine.
- ✅ **Phase 2 — RL:** `state_encoder.py` (relative encoding, ADR-002), `qtable_actor.py` (ε-greedy + Bellman + decay + save/load), `scripts/train_qtable.py` + `scripts/selfplay.py` (offline training harness). Trained tables saved to `models/`.
- 🚧 **Phase 3 — Integration/QA:** ruff = 0 violations; coverage = 100% (≥85% gate); all files ≤150 lines; integration Steps 1–5 verified offline (engine + submodule `actor_loader`). **Remaining:** full `run_match.py --mode actor` smoke needs an LLM for NL messages — choose a backend per [`docs/LLM_BACKENDS.md`](LLM_BACKENDS.md) (Ollama, or OpenRouter via `scripts/openrouter_adapter.py`).
- ✅ **Phase 5 — Launcher tooling:** `scripts/run_stack.py` (one-command `local` + `cross-team`), `run_peer_match.py` (cross-team half-orchestrator), `launch_common.py`, `peer_sync.py`. Documents why the bare MCP server makes no LLM calls (Gatekeeper lives in the client). 31 new unit tests; ruff-clean; all files ≤150 lines. See [`docs/INTERFACES.md`](INTERFACES.md) §4.

**Key implementation findings** (see also docs/PLAN.md §4, §6.1):
- Q-learning trains **offline** — the submodule match path loads a fresh actor each turn and never calls `on_result`.
- Actors accept an optional `role` kwarg (FR-01.5) so the loader's `actor_cls(role=role)` path works; both `load()`s tolerate a missing table.
- The 5×5 game is cop-dominant; the RL cop beats the heuristic baseline on capture speed, and the series sub-game win rate is 50%.

---

## Phase 0: Project Setup

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 0.1 | Create `src/actor_t6/` package with `__init__.py` | P0 | Not Started | Package importable via `PYTHONPATH=../src` (see [PLAN §3 Modules](docs/PLAN.md#3-independent-modules)) |
| 0.2 | Create `config/actor_config.json` with default weights | P0 | Not Started | JSON validates, all required keys present |
| 0.3 | Create `config.py` — config loader with schema validation | P0 | Not Started | Returns defaults for missing keys, raises on invalid types (see [PLAN §6.1 Config Schema](docs/PLAN.md#61-actor-config-configactor_configjson)) |
| 0.4 | Unit tests for `config` | P1 | Not Started | Test with invalid/missing keys, verify defaults (see [PLAN §3 Unit Test Strategy](docs/PLAN.md#3-independent-modules)) |

**Milestone:** Config loads correctly from JSON, invalid input raises errors.

---

## Phase 1: Heuristic Baseline

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 1.1 | Create `belief_state.py` — point estimate tracker | P0 | Not Started | Updates on known `opponent_pos`, resets on `round == 1`, testable in isolation (see [PLAN §5.4 BeliefState API](docs/PLAN.md#54-beliefstate)) |
| 1.2 | Unit tests for `belief_state` | P0 | Not Started | Feed synthetic `ObservationState`, assert estimate updates (see [PLAN §3 Unit Test Strategy](docs/PLAN.md#3-independent-modules)) |
| 1.3 | Create `heuristic_actor.py` — `HeuristicActor(BaseActor)` skeleton | P0 | Not Started | Passes `isinstance(actor, BaseActor)`, `get_action` raises `NotImplementedError` (see [PLAN §5.1 HeuristicActor API](docs/PLAN.md#51-heuristicactor)) |
| 1.4 | Implement `_score_move()` — distance + barrier + edge + trap scoring | P0 | Not Started | Returns float scores, highest score = best move |
| 1.5 | Implement Cop strategy — pursuit + barrier placement logic | P0 | Not Started | Considers `BARRIER` when `barriers_remaining > 0`, prioritizes capture |
| 1.6 | Implement Thief strategy — evasion + trap avoidance | P0 | Not Started | Maximizes distance, avoids dead ends |
| 1.7 | Implement `on_result()` — belief state update + stats | P1 | Not Started | Belief state updated, no crashes |
| 1.8 | Implement `save()` / `load()` — weight persistence | P2 | Not Started | Saves/loads config, `load` returns valid actor |
| 1.9 | Unit tests for `heuristic_actor` | P0 | Not Started | ≥ 85% coverage, all actions ∈ `legal_moves` (see [PLAN §3 Unit Test Strategy](docs/PLAN.md#3-independent-modules)) |

**Milestone:** Unit tests pass + Step 2 integration test passes (2×2 grid, game completes).

---

## Phase 2: RL Backend

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 2.1 | Create `state_encoder.py` — relative position + edge + barrier → int | P0 | Not Started | Encode all 9×9 relative positions, verify uniqueness, `num_states()` correct (see [PLAN §ADR-002](docs/PLAN.md#adr-002-relative-position-encoding-for-q-table)) |
| 2.2 | Unit tests for `state_encoder` | P0 | Not Started | Encode all grid positions, verify uniqueness and bounds (see [PLAN §3 Unit Test Strategy](docs/PLAN.md#3-independent-modules)) |
| 2.3 | Create `qtable_actor.py` — `QTableActor(BaseActor)` skeleton | P0 | Not Started | Passes `isinstance(actor, BaseActor)`, Q-table initialized to zeros (see [PLAN §5.2 QTableActor API](docs/PLAN.md#52-qtableactor)) |
| 2.4 | Implement epsilon-greedy `get_action()` | P0 | Not Started | Returns random action with prob ε, best Q-action otherwise |
| 2.5 | Implement Bellman update in `on_result()` | P0 | Not Started | Q-values change correctly after reward, verified with unit test |
| 2.6 | Implement epsilon decay + floor | P1 | Not Started | ε decays each sub-game, never below `epsilon_min` |
| 2.7 | Implement `save()` — write Q-table to `.npy` | P0 | Not Started | File created, shape matches `(num_states, num_actions)` |
| 2.8 | Implement `load()` — read `.npy`, set ε=0 | P0 | Not Started | Loaded actor plays deterministically (ε=0) |
| 2.9 | Unit tests for `qtable_actor` | P0 | Not Started | ≥ 85% coverage, Bellman update verified mathematically (see [PLAN §3 Unit Test Strategy](docs/PLAN.md#3-independent-modules)) |

**Milestone:** Unit tests pass + Step 4 integration test passes (5×5 grid, cold start, Q-table saved).

---

## Phase 3: Integration & Validation

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 3.1 | Integration Step 1 — import + construct test | P0 | Not Started | No import errors from submodule context (see [PLAN §4 Step 1](docs/PLAN.md#step-1--config--factory-no-game)) |
| 3.2 | Integration Step 2 — heuristic on 2×2 | P0 | Not Started | Game log shows completion, no illegal actions (see [PLAN §4 Step 2](docs/PLAN.md#step-2--heuristic-on-22-smoke-test)) |
| 3.3 | Integration Step 3 — heuristic on 5×5 (6 sub-games) | P0 | Not Started | Total score > 30 (see [PLAN §4 Step 3](docs/PLAN.md#step-3--heuristic-on-55-full-game)) |
| 3.4 | Integration Step 4 — QTableActor cold start | P0 | Not Started | Game completes, `.npy` files created (see [PLAN §4 Step 4](docs/PLAN.md#step-4--qtableactor-cold-start-no-training)) |
| 3.5 | Integration Step 5 — QTableActor trained vs heuristic | P1 | Not Started | RL actor wins ≥ 50% of sub-games (see [PLAN §4 Step 5](docs/PLAN.md#step-5--qtableactor-trained-exploitation-mode)) |
| 3.6 | Ruff lint — zero violations | P0 | Not Started | `ruff check src/` passes |
| 3.7 | Full test suite — ≥ 85% coverage | P0 | Not Started | `pytest --cov=actor_t6` passes threshold |

**Milestone:** All 5 integration steps pass. Ready for submission.

---

## Phase 4: Polish (Optional)

| # | Task | Priority | Status | DoD |
|---|------|----------|--------|-----|
| 4.1 | Belief state integration with RL backend | P2 | Not Started | QTableActor uses belief state when `opponent_pos` is `None` |
| 4.2 | Simulated partial observability tests | P2 | Not Started | Tests with artificially hidden `opponent_pos` pass |
| 4.3 | Learning curve visualization | P2 | Not Started | Graph of win rate vs. training episodes |
| 4.4 | README.md — scientific report | P1 | Not Started | DecPOMDP formalization, orchestration analysis, screenshots |

---

## Legend

| Symbol | Meaning |
|--------|---------|
| P0 | Critical — must complete for submission |
| P1 | High — important for quality |
| P2 | Medium — nice to have / bonus |

## Definition of Done (per task)

A task is **Done** when:
1. Code is written and follows the 150-line file limit
2. Unit tests pass (≥ 85% coverage for actor modules)
3. Ruff lint passes with zero violations
4. Docstrings present on all public methods
5. Integration step (if applicable) passes on target grid size

---

*Document Version: 2.0*
*Last Updated: 2026-06-25*
