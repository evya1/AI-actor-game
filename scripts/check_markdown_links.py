"""Check that internal file-path links in tracked Markdown files resolve.

Ported from agentic-publishing-pipeline scripts/check_markdown_links.py.
Parses inline links [text](path) and reference definitions [ref]: path in
every tracked .md file and verifies that local paths (not http/https/mailto/
anchors) resolve to an existing file or directory. Anchors within local
paths (docs/PLAN.md#section) are checked for file existence only.

Run: uv run python scripts/check_markdown_links.py
Exits 1 when any broken local path is found.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).parent.parent

_INLINE_RE = re.compile(r"\[(?:[^\]]*)\]\(([^)\s]+)\)")
_REF_DEF_RE = re.compile(r"^\[(?:[^\]]+)\]:\s+(\S+)", re.MULTILINE)
_URL_PREFIXES = ("http://", "https://", "mailto:", "ftp://")
_SUBMODULE = "agent-orchestration-course-t6-common"


def _tracked_md_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "*.md", "**/*.md"],
        capture_output=True,
        text=True,
        check=True,
        cwd=_REPO,
    )
    return [_REPO / p for p in result.stdout.splitlines() if p.strip()]


def _is_external(path: str) -> bool:
    return any(path.startswith(p) for p in _URL_PREFIXES) or path.startswith("#")


def _resolve(md_file: Path, link: str) -> bool:
    target = link.split("#", 1)[0]
    if not target:
        return True
    if _SUBMODULE in target and not (_REPO / _SUBMODULE / "src").exists():
        return True  # submodule not initialized here — unverifiable, not broken
    candidate = (md_file.parent / target).resolve()
    if candidate.exists():
        return True
    return (_REPO / target).resolve().exists()


def main() -> int:
    """Scan tracked Markdown files; report and fail on broken local links."""
    broken: list[str] = []
    for md in _tracked_md_files():
        text = md.read_text(encoding="utf-8", errors="ignore")
        links = _INLINE_RE.findall(text) + _REF_DEF_RE.findall(text)
        for link in links:
            if _is_external(link):
                continue
            if not _resolve(md, link):
                broken.append(f"{md.relative_to(_REPO)} -> {link}")
    if broken:
        print(f"FAIL: {len(broken)} broken local link(s)")
        for item in broken:
            print(f"  {item}")
        return 1
    print("OK: all local Markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
