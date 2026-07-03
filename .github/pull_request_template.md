<!--
Adapted from agentic-publishing-pipeline. Mark items that do not apply
with `N/A` and a one-line reason. Do not delete checklist sections.
-->

## Summary

<!-- 1–3 sentences: what this PR changes and why. -->

## Linked issue

- Related issue: <!-- Refs #N (no closing keywords — close after evidence) -->
- Task ID: <!-- e.g. 3.2 from docs/TODO.md -->
- Milestone: <!-- from config/milestones.json -->
- Labels: <!-- must match the issue labels -->

## Interface Change Protocol (CLAUDE.md §0)

- [ ] No interface, signature, module, or dependency-graph change — **or**
      the change was approved, the partner notified, and
      `docs/INTERFACES.md` / `docs/PLAN.md` / `docs/TODO.md` updated here.

## Gates

- [ ] `uv run ruff check src tests scripts` — passing
- [ ] `uv run pytest --cov=actor_t6 --cov-fail-under=85` — passing (needs submodule)
- [ ] `uv run python scripts/check_line_cap.py src scripts tests --limit 150` — passing
- [ ] `uv run python scripts/validate_repo.py` — passing
- [ ] `uv run python scripts/check_no_secrets.py` — passing
- [ ] `uv run python scripts/check_docs_present.py` — passing
- [ ] `uv run python scripts/check_markdown_links.py` — passing
- [ ] `uv run python scripts/readme_sync.py check` — passing (rebuilt if facts changed)

## Changed artifacts

-

## Docs synchronization

- [ ] `docs/TODO.md` — synchronized / no change required
- [ ] `docs/PLAN.md` — synchronized / no change required
- [ ] `README.md` — synchronized / no change required
- [ ] `SUBMISSION_CHECKLIST.md` — synchronized / no change required

## Known limitations and follow-ups

-
