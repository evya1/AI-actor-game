"""Phase-order protection check.

Ported from agentic-publishing-pipeline; adapted to this repo's
convention. For phase/NN-* branches, verifies that Phase NN-1 is marked
complete in docs/TODO.md's Implementation Status section — read from the
*base* commit via git show when a SHA is given, so a PR cannot mark its
own predecessor complete and then pass on its own text.

This repo marks completion with a checkmark status line:
    - ✅ **Phase 2 — RL:** ...

Usage:
    python scripts/check_phase_order.py <branch-name> [<base-commit-sha>]

Opt-in: only meaningful if you adopt phase/N-* branch naming. Not wired
into pre-commit or CI by default.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent
_PHASE_BRANCH_RE = re.compile(r"^phase/0*(\d+)")
_COMPLETE_RE = re.compile(r"[✅✓]\s*\*\*Phase\s+(\d+)")


def _todo_text_from_base(base_sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{base_sha}:docs/TODO.md"],
        capture_output=True, text=True, cwd=_REPO,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git show {base_sha}:docs/TODO.md failed: {result.stderr.strip()}")
    return result.stdout


def _todo_text_from_working_tree() -> str:
    todo_path = _REPO / "docs" / "TODO.md"
    if not todo_path.exists():
        raise RuntimeError("docs/TODO.md not found.")
    return todo_path.read_text(encoding="utf-8")


def _completed_phases(todo_text: str) -> set[int]:
    return {int(m.group(1)) for m in _COMPLETE_RE.finditer(todo_text)}


def main(argv: list[str]) -> int:
    """Enforce that phase N-1 is complete before phase/N work proceeds."""
    if not argv:
        print("Usage: check_phase_order.py <branch-name> [<base-commit-sha>]")
        return 1

    branch = argv[0]
    base_sha = argv[1] if len(argv) > 1 else None

    m = _PHASE_BRANCH_RE.match(branch)
    if not m:
        print(f"OK: '{branch}' is not a phase/* branch — no order check needed.")
        return 0

    phase_num = int(m.group(1))
    if phase_num <= 1:
        print(f"OK: phase {phase_num} has no predecessor to verify.")
        return 0

    required = phase_num - 1
    try:
        if base_sha:
            todo_text = _todo_text_from_base(base_sha)
            source = f"base commit {base_sha[:12]}"
        else:
            todo_text = _todo_text_from_working_tree()
            source = "working tree"
    except RuntimeError as exc:
        print(f"FAIL: {exc}")
        return 1

    if required not in _completed_phases(todo_text):
        print(
            f"FAIL: branch is for Phase {phase_num} but Phase {required} "
            f"is not marked complete in docs/TODO.md ({source})."
        )
        return 1

    print(f"OK: Phase {required} complete on {source}; Phase {phase_num} may proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
