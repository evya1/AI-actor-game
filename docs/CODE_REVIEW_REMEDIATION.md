# Code Review Remediation

Date: 2026-07-03

This report maps the reviewed correctness claims to local verification,
implementation, regression tests, validation, and commits.

| Finding | Status | Root cause | Fix | Regression evidence | Commit |
|---|---|---|---|---|---|
| Terminal feedback only reached final mover | Fixed | `scripts/selfplay.py` called `on_result()` only for the acting brain. | Track unresolved actor transitions and deliver terminal result once to each. | `tests/test_selfplay_feedback.py` | `cbcd666` |
| Bellman target used illegal actions | Fixed | `_bellman_bootstrap()` used full Q row max. | Pass next legal moves into bootstrap and mask target columns. | `tests/test_qtable_bootstrap.py` | `cbcd666` |
| Cop capture lost to trap/barrier scoring | Fixed | Capture was scored as ordinary distance-zero movement. | Legal Cop movement onto the target returns terminal-dominant score. | `tests/test_heuristic_capture.py` | `f227600` |
| Belief reset erased round 0 sightings at round 1 | Fixed | `BeliefState` reset on `round <= 1`. | Reset on canonical round regression; explicit reset remains available. | `tests/test_belief_state.py` | `f227600` |
| Peer proposals omitted canonical mechanics | Fixed | Peer client called `propose_match_tool` without `view_radius`/`max_moves`. | Lazy-load canonical `run_match` and call `_propose_match()` with both values. | `tests/test_run_peer_match.py` | `ee4893e` |
| Peer env-sensitive API key imported too early | Fixed | `run_match._API_KEY` was frozen before main repo `.env` loading. | Load env before lazy import and construct `BearerAuth` from effective env. | `tests/test_run_peer_match.py` | `ee4893e` |
| Peer forfeit tolerance diverged | Fixed | One local forfeit became immediate technical loss. | Track consecutive local forfeits and threshold at canonical max. | `tests/test_run_peer_match.py` | `ee4893e` |
| Opponent wait could miss fast move | Fixed locally | Baseline could be captured after opponent move. | Add log-position marker proving another record after local move. | `tests/test_peer_sync.py` | `ee4893e` |
| Torn terminal JSONL line crashed reader | Fixed | Newest nonblank line was parsed without `JSONDecodeError` handling. | Skip one torn trailing record, raise on persistent corruption. | `tests/test_peer_sync.py` | `ee4893e` |
| Adapter port/env not forwarded | Fixed | Adapter child inherited env without validated launcher values. | Pass `ADAPTER_HOST`, `ADAPTER_PORT`, and `OLLAMA_BASE_URL`. | `tests/test_launch_common.py` | `cd5366b` |
| Adapter readiness failure leaked child | Fixed | `start_adapter()` did not clean up after readiness exception. | Terminate/wait child on failure; forced kill fallback in `stop_process()`. | `tests/test_launch_lifecycle.py` | `cd5366b` |
| Launcher suppressed child failures | Fixed | `subprocess.run(..., check=False)` return codes were ignored. | Return child status from local/cross-team paths and `SystemExit(main())`. | `tests/test_run_stack.py` | `cd5366b` |
| Existing Q-tables invalid after RL fixes | Fixed | Artifacts were trained with bad terminal and bootstrap semantics. | Deterministic retrain with seed 42, 2000 episodes per role. | `docs/QTABLE_RETRAINING_REPORT.md` | `f5f3828` |

## Rejected After Verification

No advisory finding was rejected outright. One item was narrowed: the opponent
race has no exposed monotonic engine sequence in `ObservationState`, so the
local fix uses the append-only game-log position available to this repository.

## Validation Snapshot

Each code/model commit ran the repository pre-commit suite successfully. Final
full-suite validation is recorded in the final response for this branch.
