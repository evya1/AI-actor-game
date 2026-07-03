"""Verify that archive files are not tracked in git.

Ported from agentic-publishing-pipeline. Downloaded archives (tar, gz,
zip, etc.) must never be committed. Exits 1 when any non-allowlisted
archive file is found in the git index.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent

_ARCHIVE_SUFFIXES = (
    ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2",
    ".tar.xz", ".zip", ".gz", ".bz2", ".xz",
)

# Deliberately tracked archives. NOTE: .agents/ai-orchestration-skills.zip
# duplicates the extracted .agents/skills/ tree — consider untracking the
# zip and removing this entry.
_ALLOWED = {
    ".agents/ai-orchestration-skills.zip",
}


def _tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
        cwd=_REPO,
    )
    return result.stdout.splitlines()


def main() -> int:
    """Fail when any tracked archive is not on the explicit allowlist."""
    archives = [
        f for f in _tracked_files()
        if any(f.endswith(s) for s in _ARCHIVE_SUFFIXES) and f not in _ALLOWED
    ]

    if archives:
        print("FAIL: archive files are tracked in git:")
        for path in archives:
            print(f"  {path}")
        return 1

    print("OK: no unexpected archives tracked in git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
