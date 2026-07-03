# Product Requirements Document (PRD) — Cop & Thief Actors

## Version 1.4 | 2026-07-03

> **Change from v1.3:** §2.3 and §9 checkboxes were stale (unchecked despite
> being done) — synced with actual implementation status per `docs/TODO.md`.
>
> **Change from v1.2:** §1.1 links `docs/EX06_ASSIGNMENT.md`, the full
> assignment brief copied from the shared submodule.
>
> **Change from v1.1:** §4.3 references the new mechanical quality-gate
> enforcement (`docs/PLAN.md` §8).

---

## 1. Project Overview

### 1.1 Context

This project implements the **actor decision-making backends** for Exercise 6 (ex06) of the "AI Orchestration" course at the University of Haifa. Two autonomous agents — a **Cop** and a **Thief** — play a pursuit-evasion game on a 2D grid, communicating via MCP servers. The full assignment brief is transcribed in [`docs/EX06_ASSIGNMENT.md`](EX06_ASSIGNMENT.md); this PRD covers only our actor-specific scope.

The game engine, MCP infrastructure, actor wrapper, and LLM integration are provided by a read-only submodule (`agent-orchestration-course-t6-common`). Our scope is **only the actors** — the intelligence that decides each move.

### 1.2 What Already Exists (Submodule)

The submodule provides the following out of the box:

| Component | Description |
|-----------|-------------|
| `BaseActor` | Abstract interface — `get_action(obs)` + `on_result(obs, action, result)` ([`src/actor/base_actor.py`](agent-orchestration-course-t6-common/src/actor/base_actor.py)) |
| `LLMActorBackend` | LLM decides both action and NL message (via Gatekeeper) ([`src/actor/llm_actor.py`](agent-orchestration-course-t6-common/src/actor/llm_actor.py)) |
| `RandomActorBackend` | Uniform random selection from legal moves ([`src/actor/random_actor.py`](agent-orchestration-course-t6-common/src/actor/random_actor.py)) |
| `RLActorBackend` | **Stub only** — raises `NotImplementedError` ([`src/actor/rl_actor.py`](agent-orchestration-course-t6-common/src/actor/rl_actor.py)) |
| `ActorWrapper` | Bridges the agent and a swappable backend ([`src/actor/actor_wrapper.py`](agent-orchestration-course-t6-common/src/actor/actor_wrapper.py)) |
| `LLMMessageWrapper` | Any backend for action + LLM for NL message ([`src/actor/llm_message_wrapper.py`](agent-orchestration-course-t6-common/src/actor/llm_message_wrapper.py)) |
| MCP servers | FastMCP servers on ports 8001/8002 ([`src/game/wrappers/mcp_server.py`](agent-orchestration-course-t6-common/src/game/wrappers/mcp_server.py)) |
| `run_match.py` | Match orchestrator that starts both servers and drives turns ([`scripts/run_match.py`](agent-orchestration-course-t6-common/scripts/run_match.py)) |

### 1.3 What We Build

| Component | Description |
|-----------|-------------|
| **Heuristic actor** | Rule-based strategy (distance, barrier awareness, trap detection) |
| **RL actor (Q-learning)** | Tabular Q-learning with Bellman updates — replaces the RL stub |
| **State encoder** | Maps game state to Q-table indices |
| **Belief state tracker** | Estimates opponent position when `opponent_pos` is `None` |
| **Config loader** | Loads actor hyperparameters from config files |

We package our actors under `actor_brains` so the submodule server can load them via `ACTOR_CLASS=actor_brains.<module>.<Class>`. The server handles instantiation — we do not implement a factory.

### 1.4 Integration Model

Per the submodule README (§"Wiring Your Actor into the Server"), the server loads our actor through environment variables — **no code changes to the submodule**:

```
ACTOR_CLASS=actor_brains.qtable_actor.QTableActor
ACTOR_TABLE=models/cop_qtable.npy
```

The server:
1. Imports our class from `ACTOR_CLASS`
2. Optionally calls `cls.load(role, path)` if `ACTOR_TABLE` is set
3. Wraps our actor with `LLMMessageWrapper` (LLM generates NL messages)
4. Calls `get_action(obs)` each turn and `on_result(...)` after resolution

We make our package importable by placing it under `src/actor_brains/` and setting `PYTHONPATH` (or using `run_match.py --mode actor` which does this automatically).

### 1.5 Out of Scope

- Modifying `agent-orchestration-course-t6-common` in any way
- MCP servers, game engine, or email reporting
- Cloud deployment or GUI
- LLM backend (already provided by `LLMActorBackend`)

---

## 2. Goals and Success Metrics

### 2.1 Goals

| Goal | Description | Priority |
|------|-------------|----------|
| G1 | Implement a heuristic actor that plays both Cop and Thief | Critical |
| G2 | Implement a Q-learning actor with persistence | High |
| G3 | Handle partial observability via belief state | High |
| G4 | Achieve >50 combined points per game (6 sub-games) | Medium |
| G5 | Keep every file ≤ 150 lines | Medium |

### 2.2 Success Metrics

| Metric | Target |
|--------|--------|
| Heuristic Cop win rate | ≥ 50% capture on 5×5 |
| Heuristic Thief win rate | ≥ 50% survival on 5×5 |
| RL actor beats heuristic baseline | After training on 5×5 |
| Backend swap | Config/env-var only, zero code changes |
| Test coverage | ≥ 85% |

### 2.3 Acceptance Criteria

- [x] Our actor implements `BaseActor.get_action()` and `on_result()`
- [x] Always returns a value from `obs.legal_moves` (never illegal)
- [x] Heuristic backend works for both Cop and Thief roles
- [x] RL backend implements Q-learning with save/load persistence
- [x] Actor loadable via `ACTOR_CLASS` env var (submodule integration)
- [x] All hyperparameters externalized to config

---

## 3. Functional Requirements

### 3.1 The Submodule Interface (Read-Only Contract)

```python
# BaseActor — abstract class we must subclass
class BaseActor(ABC):
    @abstractmethod
    def get_action(self, obs: ObservationState) -> str:
        """Return one legal action from obs.legal_moves."""

    def on_result(self, obs: ObservationState, action: str, result: ActionResult) -> None:
        """Feedback after the action resolves (for learning agents)."""
```

**Input — `ObservationState`:**

| Field | Type | Description |
|-------|------|-------------|
| `actor` | `str` | `"cop"` or `"thief"` |
| `round` | `int` | Current round number |
| `my_pos` | `tuple[int, int]` | My position `(col, row)` |
| `opponent_pos` | `tuple[int, int] \| None` | Opponent position (None if out of view radius) |
| `barriers` | `list[tuple[int, int]]` | Active barrier positions |
| `legal_moves` | `list[str]` | Valid actions — **always return one of these** |
| `barriers_remaining` | `int \| None` | Barriers left for Cop (`None` for Thief) |

**Output — `ActionResult`:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Action succeeded |
| `error` | `str \| None` | Error message if failed |
| `game_over` | `bool` | Sub-game ended |
| `winner` | `str \| None` | `"cop"` or `"thief"` |
| `win_reason` | `str \| None` | `"capture"`, `"thief_survived"`, `"thief_trapped"`, `"cop_trapped"` |

**Action space:**

| Action | Description | Available To |
|--------|-------------|--------------|
| `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW` | Move one cell | Both |
| `BARRIER` | Place barrier on current cell | Cop only (max 5) |

> **Note on visibility:** The pinned submodule now filters Cop observations by
> `view_radius`; the Thief still sees the Cop. The belief-state tracker retains
> the last visible position until a later sighting, explicit reset, or canonical
> new-sub-game round regression.

### 3.2 FR-01: Actor Base (Cop + Thief)

**Description:** A single actor class that plays both roles. Role-specific behavior is selected at construction time via the `role` parameter.

**Shared requirements:**
- FR-01.1: Subclass `BaseActor` and implement `get_action(obs)` → legal action string
- FR-01.2: Implement `on_result(obs, action, result)` for learning/statistics
- FR-01.3: Handle `opponent_pos == None` via internal belief state
- FR-01.4: Implement `save(path)` and `load(cls, role, path, **kwargs)` matching the submodule's expected signature
- FR-01.5: Accept `role: str` from `load()` (submodule convention — see submodule `README.md` §"Wiring Your Actor"). Fallback: detect from `obs.actor` at runtime

**Cop-specific behavior:**
- Use `barriers_remaining` to decide when to place barriers vs. move
- Prioritize reducing distance to the Thief
- Use barriers to corner the Thief or block escape routes

**Thief-specific behavior:**
- Maximize distance from the Cop
- Avoid cells adjacent to barriers or board edges that create dead ends
- When Cop's position is unknown, assume worst-case proximity

### 3.3 FR-02: Heuristic Backend

**Description:** Rule-based strategy that requires no training. Fast, deterministic, and serves as a baseline for the RL actor.

**Requirements:**
- FR-02.1: Evaluate each legal move using a weighted scoring function
- FR-02.2: Scoring factors include: distance to opponent, barrier proximity, edge proximity, trap detection
- FR-02.3: Cop considers barrier placement as a candidate action when `barriers_remaining > 0`
- FR-02.4: All weights configurable via config file
- FR-02.5: `get_action()` returns the highest-scoring legal move

### 3.4 FR-03: RL Backend (Q-learning)

**Description:** Tabular Q-learning that replaces the submodule's `RLActorBackend` stub. Learns from game outcomes via `on_result()`.

**Requirements:**
- FR-03.1: Maintain a Q-table mapping `(state, action)` → expected reward
- FR-03.2: State encoding uses relative position to opponent (not absolute) to keep Q-table manageable on 5×5 grid
- FR-03.2a: Barrier layout encoded as binary mask or simplified proximity metric
- FR-03.3: Update Q-values via Bellman equation in `on_result()`
- FR-03.4: Epsilon-greedy policy with decay for exploration → exploitation transition
- FR-03.5: Persist Q-table to `.npy` via `save()` / `load()`
- FR-03.6: All hyperparameters (α, γ, ε) externalized to config

### 3.5 FR-04: Partial Observability (Belief State)

**Description:** When `opponent_pos` is `None`, maintain an internal estimate of where the opponent might be.

**Requirements:**
- FR-04.1: Track a belief state (point estimate or probability distribution)
- FR-04.2: Update belief when `opponent_pos` becomes known
- FR-04.3: Persist belief across rounds within a sub-game
- FR-04.4: Reset belief between sub-games (detected via `round == 1`)

> **Current status:** Visibility mechanism not yet implemented in the submodule. This component is designed for forward compatibility and can be tested with simulated partial observability. Consider deferring to a bonus phase if time is tight.

### 3.6 FR-05: Configuration

**Description:** All actor parameters externalized — no hard-coded values.

**Requirements:**
- FR-05.1: Actor type selected via `ACTOR_CLASS` env var (submodule convention)
- FR-05.2: RL hyperparameters in config (`learning_rate`, `discount_factor`, `epsilon`)
- FR-05.3: Heuristic weights in config (`distance_weight`, `barrier_weight`, `edge_weight`)
- FR-05.4: Game parameters (`max_moves`, `grid_size`, etc.) already in submodule's `config/setup.json`
- FR-05.5: Actor-specific config (heuristic weights, RL hyperparameters) in our own `config/actor_config.json`
- FR-05.6: `.env` file required for LLM wrapping (submodule's `LLMMessageWrapper` needs `OLLAMA_BASE_URL` or `ANTHROPIC_API_KEY`)

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Requirement | Target |
|-------------|--------|
| `get_action()` latency (heuristic) | < 10 ms |
| `get_action()` latency (RL) | < 1 ms |
| Memory (RL Q-table, 5×5) | < 1 MB |

### 4.2 Correctness

| Requirement | Implementation |
|-------------|----------------|
| Always legal action | Assert returned action ∈ `obs.legal_moves` |
| No crashes on `opponent_pos == None` | Explicit None handling |
| Barrier limit respected | Use `barriers_remaining` from observation |

### 4.3 Code Quality

| Requirement | Implementation |
|-------------|----------------|
| Max file size | 150 lines per file |
| Docstrings | Every public method and class |
| DRY | Shared belief-state and state-encoding utilities |
| Single responsibility | One file per backend, one file per utility |
| Mechanical enforcement | 11-hook pre-commit suite + keyless CI workflow — see [`docs/PLAN.md`](PLAN.md) §8 |

---

## 5. User Stories

### US-01: Run Heuristic Actor
**As a** developer, **I want to** run both Cop and Thief with the heuristic backend, **so that** I have a fast, deterministic baseline.

**Acceptance Criteria:**
- `ACTOR_CLASS=actor_brains.heuristic_actor.HeuristicActor`
- Cop pursues using distance minimization + barrier strategy
- Thief evades using distance maximization + trap avoidance
- No training or LLM calls required

### US-02: Train RL Actor
**As a** developer, **I want to** train a Q-learning actor over many games, **so that** it learns a better policy than the heuristic baseline.

**Acceptance Criteria:**
- `ACTOR_CLASS=actor_brains.qtable_actor.QTableActor`
- Q-table updates via `on_result()` using Bellman equation
- Epsilon-greedy policy with configurable decay
- Q-table saved to `models/cop_qtable.npy` and `models/thief_qtable.npy`

### US-03: Load Trained Actor
**As a** developer, **I want to** load a trained Q-table and play without exploration, **so that** I can evaluate the learned policy.

**Acceptance Criteria:**
- `ACTOR_TABLE=models/cop_qtable.npy` triggers `load()`
- Loaded actor uses ε=0 (pure exploitation)
- Server auto-wraps with `LLMMessageWrapper` for NL messages

### US-04: Run Match via Orchestrator
**As a** developer, **I want to** use `run_match.py --mode actor` to run a full game, **so that** I can validate the integration.

**Acceptance Criteria:**
- `run_match.py` starts both MCP servers as subprocesses
- PYTHONPATH automatically injected
- Both servers load our actor class
- Game completes and produces game log

### US-05: Handle Partial Observability
**As an** actor, **I want to** maintain a belief about the opponent's position when it's not directly observable, **so that** I can make informed decisions.

**Acceptance Criteria:**
- Belief state initialized at sub-game start
- Belief updated when `opponent_pos` is revealed
- Decisions account for uncertainty

---

## 6. Constraints

| Constraint | Description |
|------------|-------------|
| Submodule read-only | Cannot modify `agent-orchestration-course-t6-common` |
| Must subclass `BaseActor` | Our actors extend the submodule's abstract class |
| Legal actions only | `get_action()` must return a value from `obs.legal_moves` |
| Max 150 lines/file | Split logic when files grow |
| Python 3.12+ | Minimum runtime version |
| Config-driven | No hard-coded hyperparameters |
| Package name `actor_brains` | Required by submodule's `run_match.py` convention |

---

## 7. Dependencies

| Dependency | Source | Purpose |
|------------|--------|---------|
| `actor.base_actor.BaseActor` | Submodule | Abstract interface to implement |
| `game.state.ObservationState` | Submodule | Input dataclass |
| `game.state.ActionResult` | Submodule | Output dataclass |
| `game.constants` | Submodule | Directions, scoring defaults |
| `numpy` | External | Q-table operations (RL backend) |

---

## 8. Project Structure

```
actor-for-ex06/
├── src/
│   └── actor_brains/
│       ├── __init__.py
│       ├── heuristic_actor.py   # HeuristicActor(BaseActor)
│       ├── qtable_actor.py      # QTableActor(BaseActor)
│       ├── state_encoder.py     # State → Q-table index mapping
│       ├── belief_state.py      # Partial observability tracker
│       └── config.py            # Config loading + defaults
├── models/
│   ├── cop_qtable.npy           # Trained Cop weights
│   └── thief_qtable.npy         # Trained Thief weights
├── tests/
│   ├── test_heuristic.py
│   ├── test_qtable.py
│   └── test_belief_state.py
├── docs/
│   └── PRD.md                   # This document
├── agent-orchestration-course-t6-common/  # git submodule (read-only)
├── pyproject.toml
└── .env
```

---

## 9. Timeline

### Phase 1: Heuristic Baseline
- [x] HeuristicActor with role-based Cop/Thief logic
- [x] Scoring function (distance, barriers, edges, traps)
- [x] Config loading for heuristic weights
- [x] Validate via `run_match.py --mode actor` on 2×2 grid

### Phase 2: RL Backend
- [x] QTableActor with state encoder
- [x] Bellman update in `on_result()`
- [x] Epsilon-greedy policy with decay
- [x] `save()` / `load()` for Q-table persistence
- [x] Training loop on 5×5 grid — learning-curve **visualization** is still open, tracked as `docs/TODO.md` 4.3

### Phase 3: Integration & Validation
- [x] Tests (≥ 85% coverage) — 100% on our modules
- [x] Ruff lint — zero violations
- [x] All 5 integration steps pass (see [PLAN §4](PLAN.md#4-integration-testing-steps)) — verified offline against the real engine
- [ ] Final validation on 5×5 grid (6 sub-games) via `run_match.py --mode actor` with a live LLM backend — the one open item in `docs/TODO.md` Phase 3

### Phase 4: Polish (Optional / Bonus)
> Visibility mechanism not yet implemented in submodule. Deferred until submodule adds it.
- [ ] Belief state tracker
- [ ] Integration with heuristic and RL backends
- [ ] Simulated partial observability tests
- [ ] Documentation and docstrings

---

## 10. Scoring Reference

| Outcome | Cop Score | Thief Score |
|---------|-----------|-------------|
| Cop captures Thief | 20 | 5 |
| Thief survives | 5 | 10 |
| Thief trapped (no legal moves) | 20 | 5 |
| Cop trapped (no legal moves) | 5 | 10 |

A game consists of **6 sub-games**. Maximum combined score: **90**. Minimum: **30**.

**Target:** > 50 combined points per game.

---

*Document Version: 1.4*
*Last Updated: 2026-07-03*
