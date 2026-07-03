# AI Usage and Cost Record

## Scope

This document records AI-assisted engineering usage across the full project
lifecycle of `https://github.com/evya1/AI-actor-game` — initial build and
exploration, planning, the Fable code review, correctness remediation, model
validation, documentation, release verification, and Git/submission preparation
— across both Claude Code and Codex. The numbered Runs (1--3, F) call out the
key phases; the "Full Repository Accounting" tables below enumerate every
session per engine.

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
| Model | Codex `gpt-5.5` (verified from the session transcript token metadata). The prompt log's "Sonnet 5" reflected requested effort style, not the execution engine. |
| Effort | Not independently verified |
| Execution environment | Codex CLI (`codex-tui` 0.141.0), OpenAI provider |
| Session transcript | `~/.codex/sessions/2026/07/03/rollout-…019f28ca….jsonl` |

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
| Start time | 2026-07-03T16:52 UTC, Asia/Jerusalem |
| Model | Codex `gpt-5.5` (verified from the session transcript). The prompt requested "Sonnet with low coordinator effort," but the session executed on Codex `gpt-5.5`. |
| Effort level | Low coordinator effort requested; focused agents used for read-only audits |
| Branch | `fix/correctness-and-integration-review` |
| Base | `af1c2442fdb3e0ebc8872c7c728d3f72d871a48e` |
| Prompt reference | `docs/PROMPTS.md`, 2026-07-03 release-verification entry |
| Execution environment | Codex CLI, OpenAI provider |
| Session transcript | `~/.codex/sessions/2026/07/03/rollout-…019f28e5….jsonl` |
| Non-cached input tokens | 237,728 |
| Cached-input tokens | 5,013,632 |
| Output tokens | 28,330 |
| Reasoning tokens | 2,673 |
| Reported non-cached total | 266,058 |

Arithmetic note: `237,728 input + 28,330 output = 266,058 reported total`; the
transcript's cumulative `input_tokens` (5,251,360) includes the 5,013,632 cached
tokens, which are tracked separately and not added into the reported total.

Source: final cumulative `total_token_usage` record in the Codex rollout
transcript. Cost status: not calculated — the transcript records no monetary
cost (plan-metered Codex session); no dollar value is estimated without verified
rates.

## Run 3 -- Final Release, Smoke Fix, and PR

| Field | Value |
|---|---|
| Start time | 2026-07-03, Asia/Jerusalem |
| Purpose | Final release verification, OpenRouter local end-to-end smoke, launcher-defect fix, README sample-run preview, PR/CI |
| Prompt reference | `docs/PROMPTS.md`, 2026-07-03 final-release/smoke/PR entry |
| Repository | `https://github.com/evya1/AI-actor-game` |
| Branch | `fix/correctness-and-integration-review` |
| Base head at start | `7d9ee22` |
| Final head | `1cf9878` |
| Model | Opus 4.8, per user selection; exact provider model identifier not independently verified |
| Effort level | Low, per user selection |
| Execution environment | Claude Code |
| Commits added | 10 (`da71883` … `1cf9878`): launcher `OLLAMA_BASE_URL` fix, cost/usage accounting, professional README overhaul, and the `actor_t6 → actor_brains` package rename |
| Pull request | [#8](https://github.com/evya1/AI-actor-game/pull/8), CI green, mergeable |
| Local smoke | OpenRouter, `deepseek/deepseek-v3.2`, seed 42 — exit 0 |
| Non-cached input tokens | 72,814 |
| Output tokens | 634,833 |
| Cache-creation input tokens | 1,594,974 |
| Cache-read input tokens | 84,408,487 |
| Reasoning tokens | Not separately reported in the usage records |
| Reported total (input + output) | 707,647 |

Source: summed per-message `message.usage` records from this session's local
Claude Code transcripts (`~/.claude/projects/-home-dev-pop-os-hw6-actors/`,
files `3810214b….jsonl` + `701a28fc….jsonl`), model `claude-opus-4-8`. The
figures are a snapshot captured mid-session and continue to grow while the
conversation is active; cache-read/cache-creation tokens are tracked separately
and are not added into the reported total.

Arithmetic note: `72,814 input + 634,833 output = 707,647 reported total`.

Cost status: Not calculated -- the local transcripts contain no `costUSD`
field, which indicates a subscription (plan-metered) session rather than
per-token API billing, so no per-session monetary cost is recorded. No dollar
value is estimated without a verified billing model and rates. If run under API
billing, apply the Cost Calculation Template below to these token counts.

## Smoke-Test LLM Cost (OpenRouter, metered)

Unlike the plan-metered agent sessions above, the local smoke test's LLM calls
went through **OpenRouter** and carry real per-generation cost. Figures below
are computed directly from the OpenRouter generation export
(`app_name = "Cop & Thief actor_brains"`, model `deepseek/deepseek-v3.2`,
2026-07-03), covering both smoke runs that day.

| Metric | Value |
|---|---|
| Billed LLM calls (generations) | 199 |
| Total cost | **$0.008212** (~0.82 cents) |
| Average cost per call | **$0.0000413** (~0.004 cents) |
| Average tokens per call | 121 prompt / 18 completion |
| Provider cost spread (avg $/call) | Baidu $0.000019 → Google $0.000098 (~5×) |

OpenRouter routed calls across ~11 providers at different prices, so per-call
cost varies ~5×; the average above is the blended rate actually paid.

**Derived game economics.** Each round is **2 LLM calls** (one thief move
narration + one cop move narration). Using the blended $0.0000413/call:

| Unit | Calls | Estimated cost |
|---|---:|---:|
| 1 round | 2 | $0.000083 |
| 1 sub-game @ 8 rounds (smoke cap) | 16 | $0.00066 |
| 1 sub-game @ 25 moves (official cap) | 50 | $0.00206 |
| Full 6-sub-game series @ 8 rounds | 96 | $0.00396 |
| Full 6-sub-game series @ 25 moves | 300 | $0.01238 |

These are estimates from today's blended OpenRouter pricing for
`deepseek/deepseek-v3.2`; actual cost scales with rounds-per-sub-game (a capture
ends a sub-game early) and with which providers OpenRouter routes to. A full
official 6-sub-game series therefore costs roughly **1--1.5 US cents** of LLM
spend at this model. This is the only genuinely metered cost in this document;
the Claude and Codex agent sessions were plan-metered with no per-token charge.

## Run F -- Fable Code Review (Claude)

| Field | Value |
|---|---|
| Start time | 2026-07-03T14:54, Asia/Jerusalem |
| Purpose | Rigorous read-only `fluent-python-review` (high effort) of the actor code — the "Fable review" whose findings drove Run 1 remediation |
| Model | `claude-fable-5` (verified from the session transcript) |
| Execution environment | Claude Code |
| Session transcript | `~/.claude/projects/-home-dev-pop-os-hw6-actors/31e045cf….jsonl` |
| Non-cached input tokens | 52,313 |
| Cache-creation input tokens | 558,915 |
| Cache-read input tokens | 5,606,687 |
| Output tokens | 169,025 |
| Reasoning tokens | Not separately reported in the usage records |
| Reported total (input + output) | 221,338 |

Source: summed per-message `message.usage` records from the session transcript.
Cost status: not calculated — subscription (plan-metered) session with no
`costUSD` recorded.

## Codex Sessions -- Full Repository Accounting

All Codex work for this assignment ran on `2026-07-03` in `cwd`
`/home/dev-pop-os/hw6-actors`, model `gpt-5.5` (some spawned agents report
`codex-auto-review`). Runs 1 and 2 above are two of these sessions; the
remainder are review / auto-review / focused-agent sessions. Figures are the
final cumulative `total_token_usage` per rollout transcript. `input` includes
cached tokens; the last column is `total_tokens` (`input + output`).

| Session (rollout id) | Role | Input (incl. cached) | Cached | Output | Reasoning | Total |
|---|---|---:|---:|---:|---:|---:|
| `019f28ca` | Run 1 — correctness remediation | 15,183,558 | 14,971,648 | 47,354 | 5,896 | 15,230,912 |
| `019f28cc` | auto-review agent | 539,684 | 460,032 | 1,290 | 491 | 540,974 |
| `019f28cd-6291` | review agent | 235,105 | 160,384 | 3,818 | 125 | 238,923 |
| `019f28cd-7757` | review agent | 284,536 | 220,800 | 3,634 | 86 | 288,170 |
| `019f28cd-8a3b` | review agent | 142,380 | 95,616 | 2,803 | 307 | 145,183 |
| `019f28cd-9f11` | review agent | 279,606 | 231,808 | 4,446 | 481 | 284,052 |
| `019f28e5` | Run 2 — release/submission | 5,251,360 | 5,013,632 | 28,330 | 2,673 | 5,279,690 |
| `019f28f1-53f2` | review agent | 455,249 | 346,880 | 4,706 | 519 | 459,955 |
| `019f28f1-6612` | review agent | 246,705 | 201,344 | 2,968 | 258 | 249,673 |
| `019f28f1-8099` | review agent | 616,782 | 529,536 | 4,875 | 598 | 621,657 |
| `019f28f2-71b6` | auto-review agent | 39,950 | 26,368 | 206 | 170 | 40,156 |
| `019f28f2-f1cd` | auto-review agent | 102,741 | 74,112 | 386 | 243 | 103,127 |
| **Codex total (12 sessions)** | | **23,377,656** | **22,332,160** | **104,816** | **11,847** | **23,482,472** |

Non-cached input across all Codex sessions: `23,377,656 − 22,332,160 =
1,045,496`. Cost status: not calculated — Codex transcripts record no monetary
cost (plan-metered); no dollar value is estimated without verified rates.

## Claude Sessions -- Full Repository Accounting

Every Claude Code session recorded under this project
(`~/.claude/projects/-home-dev-pop-os-hw6-actors/*.jsonl`), summed from
per-message `message.usage`. This covers the whole project lifecycle: the
June 25--26 build/exploration, the 2026-07-03 planning, the Fable review
(Run F), and the Opus release session (Run 3). One empty session
(`2a45411b`, 0 tokens) is omitted. `Cached` = cache-creation + cache-read.

| Session | Date | Model | Phase / role | Input | Cached | Output | In+Out |
|---|---|---|---|---:|---:|---:|---:|
| `691d7362` | 06-25 | sonnet-4-6 | init | 6 | 39,128 | 316 | 322 |
| `4350d608` | 06-25 | sonnet-4-6 | init | 28 | 708,069 | 1,958 | 1,986 |
| `820cfef2` | 06-25 | opus-4-8 | build — repo/submodule study | 65,635 | 30,863,059 | 266,762 | 332,397 |
| `f03729ad` | 06-25 | opus-4-8 | build — repo/submodule study | 68,843 | 61,537,512 | 410,291 | 479,134 |
| `784b3692` | 06-25 | opus-4-8 | build — submodule/actors | 52,969 | 49,019,687 | 452,831 | 505,800 |
| `23f8df19` | 06-26 | opus-4-8 | build — launcher common-dir | 13,177 | 8,094,165 | 118,599 | 131,776 |
| `c90fb7b4` | 06-26 | opus-4-8 | build (interrupted) | 29,344 | 8,869,668 | 279,341 | 308,685 |
| `17696d69` | 07-03 | sonnet-5 | planning / quality-gates | 56,871 | 74,991,333 | 264,045 | 320,916 |
| `31e045cf` | 07-03 | fable-5 | **Run F** — Fable review | 52,313 | 6,165,602 | 169,025 | 221,338 |
| `3810214b` | 07-03 | opus-4-8 | **Run 3** — release/smoke/PR | 11,657 | 6,793,421 | 81,096 | 92,753 |
| `701a28fc` | 07-03 | opus-4-8 | **Run 3** — release/smoke/PR (cont.) | 61,157 | 79,210,040 | 553,737 | 614,894 |
| **Claude total (11 sessions)** | | | | **412,000** | **326,291,684** | **2,598,001** | **3,010,001** |

Run 3 spans two transcripts and is a live snapshot that keeps growing while the
session is active. The build sessions (June + the 07-03 planning session) were
outside the original remediation/release scope and are included here for a
complete project-wide picture.

## Project-Wide Token Total (Claude + Codex)

| Engine | Sessions | Non-cached input | Output | Non-cached in+out |
|---|---:|---:|---:|---:|
| Claude (this project) | 11 | 412,000 | 2,598,001 | 3,010,001 |
| Codex (this project) | 12 | 1,045,496 | 104,816 | 1,150,312 |
| **Combined** | **23** | **1,457,496** | **2,702,817** | **4,160,313** |

Cached-input tokens are large and tracked separately per engine (Claude
326,291,684; Codex 22,332,160) and are not added into the non-cached in+out
total. Cost status: not calculated — no Claude or Codex transcript records a
`costUSD` field; all sessions were subscription/plan-metered. No dollar value is
estimated without verified rates.

## Run Comparison

| Metric | Run 1 (Codex) | Run 2 (Codex) | Run F (Fable) | Run 3 (Opus, snapshot) |
|---|---:|---:|---:|---:|
| Non-cached input | 211,910 | 237,728 | 52,313 | 72,814 |
| Cached input | 14,971,648 | 5,013,632 | 6,165,602 | 86,003,461 |
| Output | 47,354 | 28,330 | 169,025 | 634,833 |
| Reasoning | 5,896 | 2,673 | Not sep. reported | Not sep. reported |
| Reported total (in+out) | 259,264 | 266,058 | 221,338 | 707,647 |

Cached input aggregates cache-creation + cache-read where the source separates
them (Run F: `558,915 + 5,606,687`; Run 3: `1,594,974 + 84,408,487`). No monetary
cost delta is calculated: every session above was subscription/plan-metered
(Claude Max plan for Fable/Opus; Codex plan for Runs 1–2) with no per-token
dollar cost recorded in any transcript, and exact billing rates were not
verified.

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

## Illustrative List-Price Cost (hypothetical -- NOT billed)

**These figures were never charged.** All Claude and Codex agent sessions ran
under subscription/plan billing with no per-token cost (see above); the only
metered spend is the OpenRouter smoke test (**$0.008212**). The estimates below
answer a *what-if*: had the Claude sessions run under metered **Anthropic API
list pricing**, applying cache-read at 0.1x input and cache-write at 1.25x
input. They are for scale intuition only and are not a real invoice.

Rates used (per 1M tokens, list price): Opus 4.8 = $5 in / $25 out; Fable 5 =
$10 in / $50 out.

| Run | Model | Non-cached in | Cache-write | Cache-read | Output | Illustrative total |
|---|---|---:|---:|---:|---:|---:|
| Run 3 | Opus 4.8 | $0.36 | $9.97 | $42.20 | $15.87 | **~$68.41** |
| Run F | Fable 5 | $0.52 | $6.99 | $5.61 | $8.45 | **~$21.57** |
| **Claude runs combined** | | | | | | **~$89.98** |

Cache-read dominates Run 3 (84.4M cache-read tokens x 0.1 x $5/M = $42.20) --
the large context re-read each turn. **Runs 1-2 (Codex `gpt-5.5`) are omitted:**
they are OpenAI models and no verified published GPT-5.5 rate was available, so
computing a figure would be fabrication.

Actually-billed total across the whole project: **$0.008212** (OpenRouter only).

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

Independent-verification status: **Yes (updated 2026-07-03).** Runs 1, 2, F, and
all Codex sessions were reconciled against on-disk session transcripts:

- Codex: final cumulative `total_token_usage` in
  `~/.codex/sessions/2026/07/03/rollout-*.jsonl` (filtered to `cwd`
  `/home/dev-pop-os/hw6-actors`). Run 1 = `019f28ca`, Run 2 = `019f28e5`.
- Claude: summed per-message `message.usage` in
  `~/.claude/projects/-home-dev-pop-os-hw6-actors/*.jsonl`. Run F (Fable) =
  `31e045cf`; Run 3 (Opus) = `3810214b` + `701a28fc`.

The token figures agree with the previously user-supplied summaries. No
transcript records a monetary cost field (`costUSD`), consistent with
subscription/plan-metered sessions; monetary cost is therefore not calculated.
Run 3 remains a mid-session snapshot and will grow while active.
