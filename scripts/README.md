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

## Quality gates (wired into pre-commit + CI, no submodule needed)

| Script | Origin | Purpose |
|--------|--------|---------|
| `check_line_cap.py` | pipeline, adapted (`--mode raw\|logical`) | Line cap: `src`+`tests` raw ≤150 (this repo's rule); `scripts` logical ≤150 (origin repo's convention — the gh tools below exceed 150 raw) |
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

## GitHub project tooling (opt-in, needs authenticated `gh` CLI)

| Script | Origin | Purpose |
|--------|--------|---------|
| `sync_milestones.py` (+ `_milestones_core/gh/output.py`) | pipeline, verbatim | Verify/create milestones from `config/milestones.json`. Read-only by default; `apply --confirm` creates only missing ones, never deletes or edits |
| `check_github_metadata.py` | pipeline, label vocab adapted | Validate open issues/PRs: assignee, labels from the vocabulary, milestone, no closing keywords, short SHAs |
| `bootstrap_github_repo.py` | pipeline, labels adapted + stdin bugfix | Push the label vocabulary and `.github/` templates into a new repo (e.g. the next course exercise). Idempotent; `--dry-run` supported |
| `check_phase_order.py` | pipeline, adapted to `✅ **Phase N` in `docs/TODO.md` | For `phase/N-*` branches: predecessor phase must be complete on the base commit. Only meaningful if you adopt that branch naming — not wired into gates |

```sh
uv run python scripts/sync_milestones.py verify
uv run python scripts/sync_milestones.py apply --confirm
uv run python scripts/check_github_metadata.py --issue 12
uv run python scripts/bootstrap_github_repo.py --repo evya1/next-exercise --dry-run
```

## Not ported from agentic-publishing-pipeline (deliberately)

`build_pdf.py`, `check_latex_structure.py`, `render_latex_project.py` — the
LaTeX build/inspection chain. They are hard-wired to that repo (one imports
the `agentic_publishing_pipeline` package; all assume `latex_project/` and
its PRD conventions). This project has no LaTeX deliverable; port them only
if the ex06 report moves from README to LaTeX.
