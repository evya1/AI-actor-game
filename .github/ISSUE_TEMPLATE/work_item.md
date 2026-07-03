---
name: Work item
about: A concrete, traceable backlog item that maps to docs/TODO.md and docs/PLAN.md.
title: "<task-id> — <short title matching docs/TODO.md wording>"
labels: []
assignees: []
---

<!--
Adapted from agentic-publishing-pipeline. If the work is not already in
docs/TODO.md / docs/PLAN.md / docs/PRD.md, update the appropriate
document first (or alongside this issue). Interface changes additionally
follow the Interface Change Protocol in CLAUDE.md §0.
-->

## Source

- **Task ID**: `<N.M>` (from docs/TODO.md)
- **TODO**: `docs/TODO.md` Phase <N>, "<TODO wording>"
- **PLAN**: `docs/PLAN.md` §<section> / ADR-<nnn> if applicable
- **PRD**: <e.g. FR-01.5; or "none">

## Milestone and labels

- **Milestone**: <from `config/milestones.json`>
- **Labels**: <from the vocabulary: `docs`, `architecture`, `rl`,
  `heuristic`, `mcp`, `launcher`, `llm-backend`, `testing`, `reporting`,
  `deployment`, `submission`, `security`, `decision`>

## Dependencies

- **Depends on**: <task ID / issue #, or "none">
- **Blocks**: <task ID / issue #, or "none">

## Description

<!-- Concrete scope: exact files, contracts, or behaviour this changes. -->

## Definition of done

-

## Acceptance criteria

- [ ]
- [ ]

## Interface-change gate (CLAUDE.md §0)

- [ ] This issue does NOT change any class interface, method signature,
      module list, or the dependency graph — **or** the change was
      explicitly approved and docs/INTERFACES.md + docs/PLAN.md +
      docs/TODO.md are updated in the same PR.
