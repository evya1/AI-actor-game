# scripts/

Operator and quality-gate scripts. Everything runs through `uv run` so it
executes inside the project's resolved environment.

## Game / training (existing)

| Script | Purpose | Needs submodule |
|--------|---------|-----------------|
| `selfplay.py` | Drive the submodule `Game` engine directly (tests + trainer) | yes |
| `train_qtable.py` | Offline Q-learning trainer → `models/{cop,thief}_qtable.npy` | yes |
| `run_stack.py` | One-command full-stack launcher (`local` / `cross-team`) | yes |
| `run_peer_match.py` | Cross-team half-orchestrator | yes |
| `peer_sync.py`, `launch_common.py` | Launcher plumbing | yes |
| `openrouter_adapter.py` | Ollama-compatible shim → OpenRouter | no |

Model provenance for corrected Q-tables is recorded in
`models/qtable_manifest.json`; before/after evaluation is in
`docs/QTABLE_RETRAINING_REPORT.md`.

### Local end-to-end smoke test

For a full local smoke without a local Ollama daemon, use the OpenRouter backend.
`run_stack.py` boots the stdlib `openrouter_adapter.py` and points the
Gatekeeper at it, so no `ollama serve` is needed. Configure via environment
variables (never commit keys or `.env`):

```sh
export OPENROUTER_API_KEY='...'
export LLM_MODEL='deepseek/deepseek-v3.2'   # or another cheap OpenRouter model
uv run python scripts/run_stack.py --backend openrouter local --mode actor --seed 42
```

Bound a quick series with `--max-rounds` / `--num-games` (forwarded to
`run_match.py`), e.g. `... --seed 42 --max-rounds 8 --num-games 2`. A clean run
exits 0, completes the actor sub-games, and shuts the adapter and both MCP
servers down. Without `OPENROUTER_API_KEY`/`ANTHROPIC_API_KEY`, `auto`
backend-selection falls back to Ollama at `localhost:11434`.

## Quality gates (wired into pre-commit + CI, no submodule needed)

| Script | Origin | Purpose |
|--------|--------|---------|
| `check_line_cap.py` | pipeline, adapted (`--mode raw\|logical`) | Line cap: `src`+`tests` raw ≤150 (this repo's rule); `scripts` logical ≤150 (origin repo's convention) |
| `validate_repo.py` | ex4, adapted | Project-only invariants: personal paths, actor-isolation rule, model artifacts tracked |
| `check_no_secrets.py` | pipeline, cwd fix + `credentials.json`/`token.json` banned | Secret scan over all tracked files |
| `check_docs_present.py` | pipeline, list adapted | Required docs/config exist |
| `check_markdown_links.py` | pipeline, submodule-aware | Local links in tracked `.md` resolve |
| `check_source_archives.py` | pipeline, allowlist added | No tracked archives (allowlists `.agents/ai-orchestration-skills.zip` — consider untracking it) |
| `check_planning_ids.py` | pipeline, adapted to `N.M` task IDs | No duplicate task-ID rows in `docs/TODO.md` |
| `check_workflow_permissions.py` | pipeline, verbatim (needs `pyyaml`) | Every workflow declares minimal `permissions` |
| `readme_sync.py` | new, per the README-automation plan | Regenerates the `repo-facts` region in README between GENERATED markers; `build` / `check` |

Run the whole suite exactly as CI does:

```sh
uv run ruff check src tests scripts
uv run python scripts/check_line_cap.py src tests --limit 150 --mode raw
uv run python scripts/check_line_cap.py scripts --limit 150 --mode logical
uv run python scripts/validate_repo.py
uv run python scripts/check_no_secrets.py
uv run python scripts/check_docs_present.py
uv run python scripts/check_markdown_links.py
uv run python scripts/check_source_archives.py
uv run python scripts/check_planning_ids.py
uv run python scripts/check_workflow_permissions.py
uv run python scripts/readme_sync.py check
```

## Not ported (deliberately)

`sync_milestones.py`, `check_github_metadata.py`, `bootstrap_github_repo.py`,
`check_phase_order.py` (+ their `_milestones_*.py` helpers) — the opt-in,
`gh`-authenticated GitHub issue/milestone-management tooling from the source
package. None of it is wired into pre-commit or CI. Deliberately not
committed to this public-facing repo to avoid exposing live-repo-mutating
tooling; `config/milestones.json` (the declarative manifest they would have
read) is kept as plain data.

`build_pdf.py`, `check_latex_structure.py`, `render_latex_project.py` — the
LaTeX build/inspection chain. They are hard-wired to that repo (one imports
the `agentic_publishing_pipeline` package; all assume `latex_project/` and
its PRD conventions). This project has no LaTeX deliverable; port them only
if the ex06 report moves from README to LaTeX.

`build_pdf.py`, `check_latex_structure.py`, `render_latex_project.py` — the
LaTeX build/inspection chain. They are hard-wired to that repo (one imports
the `agentic_publishing_pipeline` package; all assume `latex_project/` and
its PRD conventions). This project has no LaTeX deliverable; port them only
if the ex06 report moves from README to LaTeX.
