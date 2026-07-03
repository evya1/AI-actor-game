"""Validate GitHub issue/PR metadata against this repo's label vocabulary and PR rules.

Usage:
  uv run python scripts/check_github_metadata.py              # all open issues + PRs
  uv run python scripts/check_github_metadata.py --issue 29
  uv run python scripts/check_github_metadata.py --pr 92
  uv run python scripts/check_github_metadata.py --milestone 7

Exit 0 = all checks pass.  Exit 1 = violations found (CI-safe).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

LABEL_VOCAB = {
    "docs", "architecture", "rl", "heuristic", "mcp", "launcher",
    "llm-backend", "testing", "reporting", "deployment", "submission",
    "security", "decision", "enhancement", "bug", "duplicate",
    "good first issue", "help wanted", "invalid", "question", "wontfix",
}
_CLOSING = re.compile(r"^(closes|fixes|resolves)\s+#", re.I | re.M)
_FULL_SHA = re.compile(r"\b[0-9a-f]{40}\b")
_DEP_PROSE = re.compile(r"(?:Depends on|Blocks):\s*(?!none\b)", re.I)


# ---------------------------------------------------------------------------
# gh helpers
# ---------------------------------------------------------------------------

def _gh(*args: str) -> object:
    result = subprocess.run(["gh", *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"gh error: {result.stderr.strip()}")
    return json.loads(result.stdout)


def _repo() -> str:
    info = _gh("repo", "view", "--json", "nameWithOwner")
    return info["nameWithOwner"]


# ---------------------------------------------------------------------------
# Issue checks
# ---------------------------------------------------------------------------

def check_issue(number: int) -> list[str]:
    """Return metadata violations for one issue."""
    data = _gh(
        "issue", "view", str(number),
        "--json", "assignees,labels,milestone,body,blockedBy,blocking",
    )
    violations: list[str] = []

    if not data["assignees"]:
        violations.append("no assignee set")

    labels = [lb["name"] for lb in data["labels"]]
    if not labels:
        violations.append("no labels set")
    else:
        unknown = set(labels) - LABEL_VOCAB
        if unknown:
            violations.append(
                f"unknown labels (not in LABEL_VOCAB): {sorted(unknown)}"
            )

    if not data["milestone"]:
        violations.append("no milestone set")

    body = data.get("body") or ""
    if _FULL_SHA.search(body):
        violations.append("body contains a full 40-char SHA — use the 7-char short form")

    if _DEP_PROSE.search(body) and not data["blockedBy"] and not data["blocking"]:
        violations.append(
            "Dependencies prose mentions Depends on/Blocks but no native "
            "blocked-by/blocking relationships are wired "
            "(run: gh issue edit <N> --add-blocked-by / --add-blocking)"
        )

    return violations


# ---------------------------------------------------------------------------
# PR checks
# ---------------------------------------------------------------------------

def check_pr(number: int) -> list[str]:
    """Return metadata violations for one PR."""
    data = _gh(
        "pr", "view", str(number),
        "--json", "assignees,labels,milestone,body",
    )
    violations: list[str] = []

    if not data["assignees"]:
        violations.append("no assignee set on PR")

    if not data["labels"]:
        violations.append("no labels set on PR")

    body = (data.get("body") or "").strip()
    first_line = body.splitlines()[0] if body else ""
    if _CLOSING.match(first_line):
        violations.append(
            f"PR body opens with a closing keyword ({first_line!r}); "
            "use 'Refs #N' — closing happens post-merge per §8.5"
        )

    if _FULL_SHA.search(body):
        violations.append("PR body contains a full 40-char SHA — use the 7-char short form")

    if not data["milestone"]:
        violations.append("no milestone set on PR")

    return violations


# ---------------------------------------------------------------------------
# Batch helpers
# ---------------------------------------------------------------------------

def _open_issue_numbers(milestone: int | None) -> list[int]:
    args = ["issue", "list", "--state", "open", "--json", "number", "--limit", "200"]
    if milestone is not None:
        args += ["--milestone", str(milestone)]
    return [item["number"] for item in _gh(*args)]


def _open_pr_numbers(milestone: int | None) -> list[int]:
    args = ["pr", "list", "--state", "open", "--json", "number", "--limit", "200"]
    if milestone is not None:
        args += ["--search", f"milestone:{milestone}"]
    return [item["number"] for item in _gh(*args)]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _report(kind: str, number: int, violations: list[str]) -> None:
    tag = f"{kind} #{number}"
    if violations:
        print(f"FAIL  {tag}")
        for v in violations:
            print(f"      - {v}")
    else:
        print(f"PASS  {tag}")


def main(argv: list[str] | None = None) -> int:
    """Validate metadata for the selected issues/PRs."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--issue", type=int, metavar="N", help="Check a single issue")
    group.add_argument("--pr", type=int, metavar="N", help="Check a single PR")
    group.add_argument("--milestone", type=int, metavar="N",
                       help="Check all open issues and PRs in a milestone")
    args = parser.parse_args(argv)

    failures = 0

    if args.issue:
        v = check_issue(args.issue)
        _report("issue", args.issue, v)
        failures += bool(v)

    elif args.pr:
        v = check_pr(args.pr)
        _report("PR", args.pr, v)
        failures += bool(v)

    else:
        milestone = args.milestone
        for n in _open_issue_numbers(milestone):
            v = check_issue(n)
            _report("issue", n, v)
            failures += bool(v)
        for n in _open_pr_numbers(milestone):
            v = check_pr(n)
            _report("PR", n, v)
            failures += bool(v)

    if failures:
        print(f"\n{failures} object(s) have metadata violations.")
    else:
        print("\nAll checks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
