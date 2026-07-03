"""Verify task IDs in docs/TODO.md are unique as task definitions.

Ported from agentic-publishing-pipeline (P<phase>-I<nn> convention);
adapted to this repo's convention: a task definition is a Markdown table
row whose first cell is a numeric ID like `0.1` or `3.12`. Only
docs/TODO.md is checked — TODO_ORIGINAL.md and TODO_CATEGORIZED.md are
historical copies and legitimately repeat IDs.

Exits 1 when any duplicate definition is found.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

# Matches the first cell of a table row: | 3.12 |
_DEF_ROW_RE = re.compile(r"^\|\s*(\d+\.\d+)\s*\|")


def main() -> int:
    """Count task-ID definitions in docs/TODO.md; fail on duplicates."""
    todo_path = Path(__file__).parent.parent / "docs" / "TODO.md"
    if not todo_path.exists():
        print(f"FAIL: {todo_path} not found.")
        return 1

    ids: list[str] = []
    for line in todo_path.read_text(encoding="utf-8").splitlines():
        m = _DEF_ROW_RE.match(line)
        if m:
            ids.append(m.group(1))

    counts = Counter(ids)
    duplicates = {k: v for k, v in counts.items() if v > 1}

    if duplicates:
        print("FAIL: duplicate task ID definitions in docs/TODO.md:")
        for tid, count in sorted(duplicates.items()):
            print(f"  {tid}: defined {count} times in table rows")
        return 1

    print(f"OK: {len(counts)} unique task ID definitions, no duplicates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
