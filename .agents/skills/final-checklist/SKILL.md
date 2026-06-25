---
name: final-checklist
description: Run comprehensive pre-submission checklist covering documentation, architecture, tests, configuration, research, visualization, costs, extensibility, and general requirements. Use before submitting or delivering a project.
---

# Final Checklist

Before project submission, run through this comprehensive checklist.

## 1. Structure & Documentation
- [ ] Comprehensive `README.md` at project root (user manual level)
- [ ] `docs/` folder with `PRD.md`, `PLAN.md`, `TODO.md`
- [ ] Dedicated PRD documents for each algorithm/mechanism
- [ ] Architecture documentation with clear diagrams
- [ ] Documented prompt engineering log

## 2. Architecture & Code
- [ ] SDK architecture — all business logic through SDK layer
- [ ] OOP design — no code duplication, use inheritance or mixins
- [ ] API Gatekeeper — all external calls through Gatekeeper
- [ ] Rate limits from configuration, queue management for overflow
- [ ] Files ≤ 150 lines of code
- [ ] Docstring comments on all functions, classes, modules
- [ ] Consistent code style, descriptive names

## 3. Tests & Quality
- [ ] TDD — tests written before/with code
- [ ] Test coverage ≥ 85%
- [ ] Zero Ruff violations
- [ ] Edge cases documented and error handling implemented
- [ ] Automated test reports generated

## 4. Configuration & Security
- [ ] Separate config files from code, under version control
- [ ] `.env-example` with placeholder values
- [ ] No API keys or secrets in code
- [ ] `.gitignore` updated
- [ ] `uv` used as sole package manager
- [ ] `pyproject.toml` and `uv.lock` exist

## 5. Research & Visualization
- [ ] Systematic experiments with parameter changes
- [ ] Documented sensitivity analysis
- [ ] Analysis notebook with graphs
- [ ] Quality graphs, screenshots, architecture diagrams
- [ ] Token cost analysis and optimization strategies

## 6. Extensibility & Standards
- [ ] Documented extension points
- [ ] Professional Python package organization
- [ ] Parallel processing with thread safety
- [ ] Building block design pattern
- [ ] Compliance with ISO/IEC 25010
- [ ] Organized Git history, license, attribution, deployment instructions

## Quick Reference — Mandatory Thresholds

| Check | Threshold | Rule |
|-------|-----------|------|
| Code Review | All logic through SDK | SDK Architecture |
| Code Review | Extract at 2+ copies | OOP / No Duplication |
| Code Review + Test | All calls through SDK | API Gatekeeper |
| Config Check | From config, not code | Rate Limits |
| Integration Test | Queue, not crash | Overflow Management |
| Version Module | Starts at 1.00 | Version Control |
| Work Process | Red-Green-Refactor | TDD |
| Auto Test | ≤ 150 lines | File Size |
| `ruff check` | 0 violations | Linter |
| `pytest-cov` | ≥ 85% | Test Coverage |
| Code Review | 0 in source code | Hardcoded Values |
| Auto Scan | `.env-example + 0` | Secrets |
| Auto Test | All through uv | Package Manager |
