# SUBMISSION_CHECKLIST — Exercise 6 (Cop & Thief via MCP)

Mapped from the assignment spec (ex06 PDF, v1.0, Dr. Yoram Segal). Each row
should point at concrete evidence in this repo or the submodule before
submission. Rows marked **(submodule)** are provided by
`agent-orchestration-course-t6-common` — verify they exist there, don't
reimplement here.

## Game mechanics & configuration

- [ ] Grid size, `max_moves` (25), `num_games` (6), `max_barriers` (5), and all
      four scoring values live in a config file — **zero hardcoding**
      (assignment §10). Evidence: `config/actor_config.json` + submodule config. (submodule for game params)
- [ ] Generic architecture: grid size changeable via config only. (submodule)
- [ ] Barrier rules: cop-only, placed on own square, max 5, blocks thief. (submodule)
- [ ] Sanity-check ladder run and documented: 2×1 → 2×3/3×3 → 4×3/4×4 → 5×5
      (assignment §4.5). Evidence: logs/section in README.

## Orchestration & MCP

- [ ] Two independent MCP servers (cop, thief), natural-language messages only —
      no raw coordinates in the protocol. (submodule)
- [ ] LLM lives in the client/orchestrator, MCP server exposes tools only
      (assignment §5.2). Documented in `docs/LLM_BACKENDS.md`.
- [ ] Fully autonomous series of 6 sub-games, no human in the loop.
- [ ] Cloud deployment of both MCP servers with public URLs; token-based auth
      with revoke. Evidence: URLs in the internal game report JSON.
- [ ] Technical-loss rule honored: aborted sub-games rerun until 6 clean ones.

## Reporting (assignment §9)

- [ ] Automated Gmail API email to `rmisegal+uoh26b@gmail.com` after 6 sub-games,
      body is **JSON only** (internal game report schema: `group_name`,
      `students`, `github_repo`, `cop_mcp_url`, `thief_mcp_url`, `timezone`,
      `sub_games`, `totals`).
- [ ] OAuth client (Desktop) + test user + `credentials.json`/`token.json` flow
      per the Google API guide; secrets NOT committed (`validate_repo.py` gate).
- [ ] Bonus (optional, +10): cross-team series with role swap after 3 sub-games,
      both teams email identical reports, `mutual_agreement: true`.

## README as scientific report (assignment §11)

- [ ] Formal Dec-POMDP model: the tuple ⟨n, S, {Ai}, P, R, {Ωi}, O, γ⟩ defined
      with the concrete state/action/observation spaces of this game.
- [ ] Orchestration-challenge analysis: free natural language without a fixed
      protocol, linguistic ambiguity, mutual-understanding techniques.
- [ ] Visualizations: learning curves (Q-table training), CLI logs proving
      MCP communication, GUI screenshots of live agent/barrier movement.
- [ ] Honest results (already partially in README: cop-dominant 5×5 analysis,
      RL cop vs heuristic numbers, 50% series win rate).

## Repo quality gates (this repo)

- [x] `uv run ruff check src tests scripts` → 0 violations.
- [x] `uv run pytest --cov=actor_t6 --cov-fail-under=85` → green (needs submodule).
- [x] `uv run python scripts/validate_repo.py` → OK.
- [x] `uv run python scripts/check_markdown_links.py` → OK.
- [x] `uv run python scripts/readme_sync.py check` → OK.
- [x] 11-hook pre-commit suite wired and installed (`.pre-commit-config.yaml`,
      `uv run pre-commit install`); verified firing on a real commit
      (PR [#3](https://github.com/evya1/AI-actor-game/pull/3)).
- [x] CI keyless gates green on `main` (ruff, line-cap, validate-repo,
      no-secrets, docs-present, markdown-links, source-archives,
      planning-IDs, workflow-permissions).
- [ ] CI's gated pytest/coverage job green — blocked on the `SUBMODULE_SSH_KEY`
      repo secret (needs a read-only deploy key on the submodule repo;
      see `docs/TODO.md` task 6.4).
- [ ] CI green on the submission commit (re-check at submission time).
- [ ] AI-usage disclosure present (`docs/PROMPTS.md` / AI usage section) —
      **`docs/PROMPTS.md` does not exist yet**; CLAUDE.md §6 requires a
      prompt log — still to be created before submission.
