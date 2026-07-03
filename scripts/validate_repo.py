"""Repository validation — project-specific invariants for actor_t6.

Adapted from ai-orchestration-ex4-finding-bugs. Generic gates live in
dedicated scripts (check_line_cap, check_no_secrets, check_docs_present,
check_markdown_links, check_source_archives); this script owns only the
invariants unique to this project.

Run: uv run python scripts/validate_repo.py
Exits 1 if any violation is found. No submodule required.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CODE_DIRS = ("src", "scripts", "tests")

_PATH = re.compile(r'["\']/(home|Users)/[A-Za-z0-9_.-]{2,}/')

# Dependency-graph rule from CLAUDE.md: actors never import each other.
_ACTOR_ISOLATION = {
    "heuristic_actor.py": ("qtable_actor", "state_encoder"),
    "heuristic_scoring.py": ("qtable_actor", "state_encoder"),
    "qtable_actor.py": ("heuristic_actor", "heuristic_scoring"),
}

MODEL_ARTIFACTS = ("models/cop_qtable.npy", "models/thief_qtable.npy")

Violations = list[str]


def _py_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True, check=True, cwd=ROOT
    )
    return [
        ROOT / p for p in out.stdout.splitlines()
        if p.endswith(".py") and p.split("/", 1)[0] in CODE_DIRS
    ]


def check_personal_paths() -> Violations:
    """Check 1: no personal absolute paths (/home/..., /Users/...) in code."""
    return [
        f"PERSONAL_PATH: {p.relative_to(ROOT)}"
        for p in _py_files()
        if _PATH.search(p.read_text(encoding="utf-8"))
    ]


def check_actor_isolation() -> Violations:
    """Check 2: heuristic and qtable actors never import each other."""
    hits = []
    for name, banned in _ACTOR_ISOLATION.items():
        path = ROOT / "src" / "actor_t6" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for mod in banned:
            if re.search(rf"(?m)^\s*(from|import)\s+(actor_t6\.)?{mod}\b", text):
                hits.append(f"ACTOR_ISOLATION: {name} imports {mod}")
    return hits


def check_model_artifacts() -> Violations:
    """Check 3: trained Q-tables are tracked (deliberate project decision)."""
    return [f"MISSING_MODEL: {rel}" for rel in MODEL_ARTIFACTS if not (ROOT / rel).exists()]


def main() -> int:
    """Run all checks; print violations; exit 1 on any failure."""
    checks = [check_personal_paths, check_actor_isolation, check_model_artifacts]
    violations: Violations = []
    for check in checks:
        violations.extend(check())
    if violations:
        print(f"FAIL: {len(violations)} violation(s)")
        for v in violations:
            print(f"  {v}")
        return 1
    print(f"OK: all {len(checks)} project-specific checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
