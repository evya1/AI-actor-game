# Phase Length Analysis — Cop & Thief Actors

## Version 1.0 | 2026-06-25

> Derived from [TODO.md](TODO.md).

---

## Phases Ranked by Length

| Rank | Phase | Tasks | Count | % of Total |
|------|-------|-------|-------|------------|
| 1 | **Phase 1: Heuristic Baseline** | 1.1–1.8 | **8** | 26.7% |
| 1 | **Phase 2: RL Backend** | 2.1–2.8 | **8** | 26.7% |
| 3 | **Phase 3: Integration & Validation** | 3.1–3.7 | **7** | 23.3% |
| 4 | **Phase 0: Project Setup** | 0.1–0.4 | **4** | 13.3% |
| 4 | **Phase 4: Polish (Optional)** | 4.1–4.4 | **4** | 13.3% |

---

## Summary

| Tier | Phases | Total Tasks | Combined % |
|------|--------|-------------|------------|
| **Large** (8 tasks) | Phase 1, Phase 2 | 16 | 53.3% |
| **Medium** (7 tasks) | Phase 3 | 7 | 23.3% |
| **Small** (4 tasks) | Phase 0, Phase 4 | 8 | 26.7% |
| **Total** | All phases | **30** | **100%** |

---

## Implications

- **Phases 1 & 2** represent the bulk of implementation effort (53.3% of tasks). These are parallelizable in that Phase 2 depends on Phase 1's belief state and config infrastructure.
- **Phase 3** is validation-heavy and gates submission — every integration step must pass before delivery.
- **Phase 0** is a quick prerequisite (4 tasks) that unblocks all other phases.
- **Phase 4** is optional polish and can be deprioritized if time is constrained.

---

*Document Version: 1.0*
*Last Updated: 2026-06-25*
