"""Output helpers for the milestone sync command."""

from __future__ import annotations

from _milestones_core import Diff


def format_accepted_preapply_diff(diff: Diff) -> str:
    lines: list[str] = ["Accepted pre-apply diff:"]
    lines.extend(_section("matching milestones", diff.matches))
    lines.extend(_section("missing milestones to create", [m.title for m in diff.missing]))
    lines.extend(_section("unexpected extras", [m.title for m in diff.extra]))
    lines.extend(_section("description conflicts", [em.title for em, _lm in diff.conflicts]))
    lines.extend(_section("duplicate live titles", diff.duplicates))
    lines.extend(_section("non-null due_on", [m.title for m in diff.bad_due_on]))
    return "\n".join(lines)


def _section(label: str, items: list[str]) -> list[str]:
    if not items:
        return [f"{label}: none"]
    return [f"{label} ({len(items)}):", *[f"  - {item}" for item in items]]
