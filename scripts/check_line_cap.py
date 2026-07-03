"""Check Python source files against the project line cap.

Ported from agentic-publishing-pipeline; adapted with a --mode flag.

  raw     — every physical line counts (this repo's CLAUDE.md rule:
            "No file may exceed 150 lines"). Default.
  logical — non-blank, non-comment source lines only (the original
            pipeline semantics; more lenient).

Usage: uv run python scripts/check_line_cap.py src scripts tests --limit 150
"""

from __future__ import annotations

import argparse
import sys
import tokenize
from pathlib import Path

DEFAULT_LIMIT = 150


def raw_lines(path: Path) -> int:
    """Count physical lines."""
    return len(path.read_text(encoding="utf-8").splitlines())


def logical_lines(path: Path) -> int:
    """Count non-blank, non-comment logical source lines."""
    lines: set[int] = set()
    with path.open("rb") as handle:
        for token in tokenize.tokenize(handle.readline):
            if token.type in {
                tokenize.ENCODING, tokenize.ENDMARKER, tokenize.NEWLINE,
                tokenize.NL, tokenize.INDENT, tokenize.DEDENT, tokenize.COMMENT,
            }:
                continue
            lines.update(range(token.start[0], token.end[0] + 1))
    return len(lines)


def python_files(root: Path) -> list[Path]:
    """Collect .py files under a root, skipping __pycache__."""
    if root.is_file():
        return [root] if root.suffix == ".py" else []
    return sorted(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)


def check_roots(roots: list[Path], *, limit: int, mode: str) -> list[tuple[Path, int]]:
    """Return (path, count) for every file over the limit."""
    measure = raw_lines if mode == "raw" else logical_lines
    violations: list[tuple[Path, int]] = []
    for root in roots:
        for path in python_files(root):
            count = measure(path)
            if count > limit:
                violations.append((path, count))
    return violations


def build_parser() -> argparse.ArgumentParser:
    """CLI definition."""
    parser = argparse.ArgumentParser(description="Enforce the source line cap.")
    parser.add_argument("roots", nargs="*", type=Path, default=[Path("src")])
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--mode", choices=("raw", "logical"), default="raw")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the cap check over the given roots."""
    args = build_parser().parse_args(argv)
    violations = check_roots(args.roots, limit=args.limit, mode=args.mode)
    if not violations:
        print(f"Line cap passed: <= {args.limit} {args.mode} lines")
        return 0
    for path, count in violations:
        print(f"{path}: {count} {args.mode} lines > limit {args.limit}", file=sys.stderr)
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
