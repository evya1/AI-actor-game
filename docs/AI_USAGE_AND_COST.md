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

## Run 3 -- Final Release, Smoke Fix, and PR

| Field | Value |
|---|---|
| Start time | 2026-07-03, Asia/Jerusalem |
| Purpose | Final release verification, OpenRouter local end-to-end smoke, launcher-defect fix, README sample-run preview, PR/CI |
| Prompt reference | `docs/PROMPTS.md`, 2026-07-03 final-release/smoke/PR entry |
| Repository | `https://github.com/evya1/AI-actor-game` |
| Branch | `fix/correctness-and-integration-review` |
| Base head at start | `7d9ee22` |
| Final head | `30709f6` |
| Model | Opus 4.8, per user selection; exact provider model identifier not independently verified |
| Effort level | Low, per user selection |
| Execution environment | Claude Code |
| Commits added | 3 (`da71883` launcher fix + test, `2588d8d` docs, `30709f6` README sample run) |
| Pull request | [#8](https://github.com/evya1/AI-actor-game/pull/8), CI green, mergeable |
| Local smoke | OpenRouter, `deepseek/deepseek-v3.2`, seed 42 — exit 0 |
| Non-cached input tokens | 28,125 |
| Output tokens | 253,166 |
| Cache-creation input tokens | 800,673 |
| Cache-read input tokens | 26,683,975 |
| Reasoning tokens | Not separately reported in the usage records |
| Reported total (input + output) | 281,291 |

Source: summed per-message `message.usage` records from this session's local
Claude Code transcripts (`~/.claude/projects/-home-dev-pop-os-hw6-actors/`,
files `3810214b….jsonl` + `701a28fc….jsonl`), model `claude-opus-4-8`. The
figures are a snapshot captured mid-session and continue to grow while the
conversation is active; cache-read/cache-creation tokens are tracked separately
and are not added into the reported total.

Arithmetic note: `28,125 input + 253,166 output = 281,291 reported total`.

Cost status: Not calculated -- the local transcripts contain no `costUSD`
field, which indicates a subscription (plan-metered) session rather than
per-token API billing, so no per-session monetary cost is recorded. No dollar
value is estimated without a verified billing model and rates. If run under API
billing, apply the Cost Calculation Template below to these token counts.

## Run Comparison

| Metric | Run 1 | Run 2 | Run 3 (snapshot) |
|---|---:|---:|---:|
| Non-cached input | 211,910 | Not reported | 28,125 |
| Cached input | 14,971,648 | Not reported | 27,484,648 |
| Output | 47,354 | Not reported | 253,166 |
| Reasoning | 5,896 | Not reported | Not separately reported |
| Reported total | 259,264 | Not reported | 281,291 |

Run 3 cached input is `cache_creation (800,673) + cache_read (26,683,975)`.
No cost delta is calculated: Run 2 token metadata was unavailable, and Run 1/Run 3
were subscription (plan-metered) sessions with no per-token dollar cost recorded;
exact billing rates were not verified.

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
