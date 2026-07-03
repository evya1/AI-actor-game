"""Verify GitHub workflow files declare minimal permissions.

Flags workflows that:
- are missing a top-level 'permissions' key (defaults to broad access)
- declare 'permissions: write-all'

Requires PyYAML (available after `uv sync --group dev`).
Exits 1 when violations are found.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml  # available after uv sync --group dev

_WORKFLOWS = Path(__file__).parent.parent / ".github" / "workflows"
_OVERBROAD = {"write-all", "write_all"}


def _check_file(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        issues.append(f"{path.name}: YAML parse error: {exc}")
        return issues

    if not isinstance(doc, dict):
        return issues

    perms = doc.get("permissions")
    if perms is None:
        issues.append(
            f"{path.name}: missing top-level 'permissions' key "
            "(defaults to broad repository access)"
        )
    elif isinstance(perms, str) and perms in _OVERBROAD:
        issues.append(f"{path.name}: 'permissions: {perms}' grants excessive access")

    return issues


def main() -> int:
    """Check every workflow file for a minimal permissions declaration."""
    if not _WORKFLOWS.exists():
        print("SKIP: .github/workflows/ not found.")
        return 0

    workflow_files = sorted(_WORKFLOWS.glob("*.yml"))
    if not workflow_files:
        print("OK: no workflow files found.")
        return 0

    issues: list[str] = []
    for path in workflow_files:
        issues.extend(_check_file(path))

    if issues:
        print("FAIL: workflow permission issues found:")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print(f"OK: all {len(workflow_files)} workflow files have minimal permissions declared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
