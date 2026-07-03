"""Check that no .env files or secrets patterns are tracked in git.

Ported from agentic-publishing-pipeline; one change: paths are resolved
against the repo root derived from this script's location, so the check
works regardless of the caller's working directory.

Scans tracked files for known secret patterns and reports findings.
Exits 1 when any issue is found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent

_BANNED_FILES = {
    ".env",
    "credentials.json",  # Google OAuth client secret (ex06 Gmail report)
    "token.json",        # Google OAuth user token
}

_SECRET_RE = re.compile(
    r'(?i)(api[_\-]?key|secret[_\-]?key|password|token|credential)\s*=\s*["\']?[A-Za-z0-9+/]{16,}',
)

_IGNORED_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".gz", ".tar", ".zip", ".npy"}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
        cwd=_REPO,
    )
    return [_REPO / p for p in result.stdout.splitlines() if p.strip()]


def main() -> int:
    """Scan tracked files for banned filenames and secret-looking assignments."""
    issues: list[str] = []

    for path in _tracked_files():
        if path.name in _BANNED_FILES:
            issues.append(f"Tracked secret file: {path.relative_to(_REPO)}")
            continue

        if path.suffix in _IGNORED_SUFFIXES or not path.exists():
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for lineno, line in enumerate(text.splitlines(), 1):
            if _SECRET_RE.search(line):
                issues.append(f"Possible secret at {path.relative_to(_REPO)}:{lineno}")

    if issues:
        print("FAIL: potential secrets or banned files found:")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print("OK: no tracked secrets or banned files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
