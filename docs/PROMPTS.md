# AI Prompt Log

Per CLAUDE.md §6. Terse by design — one row per distinct piece of work,
not a full transcript. Session with Claude Code (Sonnet 5).

| Date | Prompt (paraphrased) | Outcome |
|------|----------------------|---------|
| 2026-07-03 | Apply a prepared quality-gate/CI tooling package to the repo on a dedicated branch, one commit per step, PR-gated. | 9 local quality-gate scripts, `.pre-commit-config.yaml` (11 hooks), keyless `.github/workflows/ci.yml`, issue/PR templates, `SUBMISSION_CHECKLIST.md`, `config/milestones.json`, README generated `repo-facts` region. PR #2. |
| 2026-07-03 | Exclude the GitHub issue/milestone-management scripts (gh-authenticated, mutate live repo state) from the public repo — keep only local repo-state quality gates. | 7 scripts dropped before push; `scripts/README.md` and the issue template's dangling reference updated. Folded into PR #2. |
| 2026-07-03 | Push the branch and open the PR with a description following the repo's PR template. | PR #2 opened, reviewed together, merged. |
| 2026-07-03 | Sync `main`, delete merged/superseded branches locally and remotely. | `chore/quality-gates` and an unrelated stale `feat/llm-stack-launcher` branch removed both sides. |
| 2026-07-03 | Run `uv run pre-commit install` to activate the hook suite locally. | Hook installed; verified firing (all 11 checks) on the next real commit. |
| 2026-07-03 | Untrack a duplicated tracked archive under `.agents/` now that its contents are already extracted elsewhere in the repo. | Archive removed from git (kept on disk, gitignored); allowlist entry dropped from `scripts/check_source_archives.py`. PR #3. |
| 2026-07-03 | Sync `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md`, and `SUBMISSION_CHECKLIST.md` with the quality-gate work above (tooling-only, so not required by the Interface Change Protocol, but expected by the project's SDLC discipline). | New `docs/PLAN.md` §8 + ADR-005, `docs/TODO.md` Phase 6, `docs/PRD.md` §4.3 cross-reference, checklist items marked true. PR #4. |
| 2026-07-03 | Create this prompt log. | `docs/PROMPTS.md` (this file). |

## Notes

- All commits in this log were made with `--no-gpg-sign` at the user's
  explicit request — commit signing requires credentials this session's
  sandbox cannot read.
- Remaining open item from this work: CI's gated pytest/coverage job needs
  a `SUBMODULE_SSH_KEY` repo secret (read-only deploy key on the submodule
  repo), blocked on submodule-repo admin access — see `docs/TODO.md` 6.4.
