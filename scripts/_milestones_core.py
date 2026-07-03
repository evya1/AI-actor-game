"""Pure domain logic for the milestone manifest sync tool.

Loads and validates ``config/milestones.json``, models live milestone state,
and computes the manifest-vs-live diff. No subprocess or network I/O — the
gh adapter lives in ``_milestones_gh`` and the CLI + verify/dry-run/apply
operations live in ``sync_milestones``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

SUPPORTED_VERSION = 1


class ManifestError(ValueError):
    """Raised when the manifest is malformed or contains invalid entries."""


@dataclass(frozen=True)
class ExpectedMilestone:
    title: str
    description: str


@dataclass(frozen=True)
class LiveMilestone:
    number: int
    title: str
    description: str
    due_on: str | None
    state: str


@dataclass(frozen=True)
class Manifest:
    version: int
    milestones: tuple[ExpectedMilestone, ...]


@dataclass
class Diff:
    matches: list[str] = field(default_factory=list)
    missing: list[ExpectedMilestone] = field(default_factory=list)
    extra: list[LiveMilestone] = field(default_factory=list)
    conflicts: list[tuple[ExpectedMilestone, LiveMilestone]] = field(default_factory=list)
    duplicates: list[str] = field(default_factory=list)
    bad_due_on: list[LiveMilestone] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not (
            self.missing or self.extra or self.conflicts or self.duplicates or self.bad_due_on
        )

    @property
    def has_blocking_conflict(self) -> bool:
        """True when ``apply`` must abort before any write."""
        return bool(self.extra or self.conflicts or self.duplicates or self.bad_due_on)


def load_manifest(path: Path) -> Manifest:
    assert isinstance(path, Path), "path must be a Path"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Manifest is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ManifestError("Manifest root must be a JSON object")
    version = raw.get("version")
    if version != SUPPORTED_VERSION:
        raise ManifestError(
            f"Unsupported manifest version: {version!r} (expected {SUPPORTED_VERSION})"
        )
    entries = raw.get("milestones")
    if not isinstance(entries, list) or not entries:
        raise ManifestError("manifest.milestones must be a non-empty list")
    parsed: list[ExpectedMilestone] = []
    seen: set[str] = set()
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ManifestError(f"milestones[{i}] must be an object")
        title = entry.get("title")
        desc = entry.get("description")
        if not isinstance(title, str) or not title.strip():
            raise ManifestError(f"milestones[{i}].title must be a non-empty string")
        if title in seen:
            raise ManifestError(f"Duplicate milestone title in manifest: {title!r}")
        if not isinstance(desc, str):
            raise ManifestError(f"milestones[{i}].description must be a string")
        if "due_on" in entry and entry["due_on"] is not None:
            raise ManifestError(f"milestones[{i}].due_on must be null (got {entry['due_on']!r})")
        seen.add(title)
        parsed.append(ExpectedMilestone(title=title, description=desc))
    return Manifest(version=version, milestones=tuple(parsed))


def compute_diff(manifest: Manifest, live: list[LiveMilestone]) -> Diff:
    diff = Diff()
    by_title: dict[str, LiveMilestone] = {}
    for lm in live:
        if lm.title in by_title:
            diff.duplicates.append(lm.title)
        else:
            by_title[lm.title] = lm
    expected: set[str] = set()
    for em in manifest.milestones:
        expected.add(em.title)
        lm = by_title.get(em.title)
        if lm is None:
            diff.missing.append(em)
        elif lm.due_on is not None:
            diff.bad_due_on.append(lm)
        elif lm.description != em.description:
            diff.conflicts.append((em, lm))
        else:
            diff.matches.append(em.title)
    diff.extra = [lm for lm in live if lm.title not in expected]
    return diff


def format_diff(diff: Diff) -> str:
    lines: list[str] = [f"matches: {len(diff.matches)}"]
    sections = (
        ("missing", [m.title for m in diff.missing]),
        ("unexpected extra", [f"{m.title} (#{m.number})" for m in diff.extra]),
        (
            "description conflicts",
            [f"{em.title} (#{lm.number})" for em, lm in diff.conflicts],
        ),
        ("duplicate live titles", list(diff.duplicates)),
        (
            "non-null due_on",
            [f"{m.title} (due_on={m.due_on})" for m in diff.bad_due_on],
        ),
    )
    for label, items in sections:
        if items:
            lines.append(f"{label} ({len(items)}):")
            lines.extend(f"  - {x}" for x in items)
    return "\n".join(lines)
