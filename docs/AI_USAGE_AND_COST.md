# AI Usage and Cost Record

## Scope

This document records AI-assisted engineering usage for correctness remediation,
release verification, model validation, documentation, and Git/submission
preparation in `https://github.com/evya1/AI-actor-game`.

Token counts are reported execution metadata. Token counts do not by themselves
establish monetary cost. Cached input is tracked separately. No monetary value
should be inferred without a verified billing model.

## Run 1 -- Correctness Remediation

| Field | Value |
|---|---|
| Purpose | Correctness-first remediation of RL, actor, peer, launcher, tests, models, and documentation |
| Prompt reference | `docs/PROMPTS.md`, 2026-07-03 correctness-remediation entry |
| Repository | `https://github.com/evya1/AI-actor-game` |
| Branch | `fix/correctness-and-integration-review` |
| Original base | `af1c2442fdb3e0ebc8872c7c728d3f72d871a48e` |
| Reported resulting head | `35f3a54` |
| Model | Sonnet 5, per prompt log; exact provider model identifier not independently verified |
| Effort | Not independently verified |
| Execution environment | Claude Code |

| Category | Tokens |
|---|---:|
| Non-cached input | 211,910 |
| Cached input | 14,971,648 |
| Output | 47,354 |
| Reasoning | 5,896 |
| Reported non-cached total | 259,264 |

Arithmetic note: `211,910 input + 47,354 output = 259,264 reported total`.

Cost status: Not calculated -- exact billing model and applicable rates were not
verified.

Outcomes: six remediation commits corrected terminal RL feedback,
legal-action Bellman targets, capture and belief semantics, peer protocol and
synchronization, launcher lifecycle and exit propagation, deterministic Q-table
artifacts, and remediation documentation. Evidence is recorded in
`docs/CODE_REVIEW_REMEDIATION.md`, `docs/QTABLE_RETRAINING_REPORT.md`, and
`models/qtable_manifest.json`.

Limitations: cached input is not included in the reported `total`. Reasoning
tokens may already be included in provider output-token accounting.

## Run 2 -- Release and Submission Verification

| Field | Value |
|---|---|
| Start time | 2026-07-03, Asia/Jerusalem |
| Completion time | Not reported by the execution environment |
| Model | Sonnet with low coordinator effort, requested by user; exact provider model identifier not independently verified |
| Effort level | Low coordinator effort requested; focused agents used for read-only audits |
| Branch | `fix/correctness-and-integration-review` |
| Base | `af1c2442fdb3e0ebc8872c7c728d3f72d871a48e` |
| Final head | Not reported by the execution environment at document creation time |
| Prompt reference | `docs/PROMPTS.md`, 2026-07-03 release-verification entry |
| Input tokens | Not reported by the execution environment |
| Cached-input tokens | Not reported by the execution environment |
| Output tokens | Not reported by the execution environment |
| Reasoning tokens | Not reported by the execution environment |
| Reported total | Not reported by the execution environment |
| Duration | Not reported by the execution environment |
| Focused agents | 3 |
| Commits added | Not reported by the execution environment at document creation time |
| Tests executed | Recorded in final release report and Git history |
| Final result | Not reported by the execution environment at document creation time |

Unavailable usage values are intentionally not estimated from transcript length.

## Run Comparison

| Metric | Run 1 | Run 2 |
|---|---:|---:|
| Non-cached input | 211,910 | Not reported |
| Cached input | 14,971,648 | Not reported |
| Output | 47,354 | Not reported |
| Reasoning | 5,896 | Not reported |
| Reported total | 259,264 | Not reported |

No cost or efficiency delta is calculated because Run 2 token metadata and exact
billing rates were not verified.

## Efficiency Observations

This release workflow used three narrow, non-overlapping focused agents:
release/diff audit, runtime smoke-test design, and submission/history/evidence
audit. The coordinator read repository instructions once, used targeted
`git diff`, `git show`, `rg`, and validation commands, and avoided rerunning
the original broad architecture review.

Recommended future improvements:

- read repository instructions once and share constraints with agents;
- avoid repeated full-file reads;
- use narrow agents with non-overlapping scopes;
- run focused tests before full validation;
- avoid regenerating unchanged documentation;
- prevent duplicate architecture reviews;
- reuse deterministic reports and repository manifests;
- do not reopen already verified design decisions.

These are process recommendations, not measured token savings.

## Cost Calculation Template

```text
ordinary_input_cost =
    non_cached_input_tokens / 1_000_000 x ordinary_input_rate

cached_input_cost =
    cached_input_tokens / 1_000_000 x cached_input_rate

output_cost =
    output_tokens / 1_000_000 x output_rate

estimated_total_cost =
    ordinary_input_cost + cached_input_cost + output_cost
```

Reasoning-token treatment: verify whether reasoning tokens are already included
in output-token billing before adding a separate reasoning component.

## Provenance

Source of Run 1 token figures: user-provided Claude execution summary.

Exact reported line:

```text
Token usage: total=259,264 input=211,910
(+ 14,971,648 cached) output=47,354
(reasoning 5,896)
```

Date recorded: 2026-07-03.

Repository commit that introduced this documentation: see the follow-up release
documentation commit in Git history.

Independent-verification status: No -- preserved from the execution summary
supplied by the user.
