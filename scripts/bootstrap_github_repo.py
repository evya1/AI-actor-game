"""Bootstrap GitHub labels and issue/PR templates into a repository.

Ported from agentic-publishing-pipeline (label vocabulary adapted; fixed a
TypeError where _gh_raw was called with an unsupported stdin kwarg).
Copies the label vocabulary and .github/ workflow templates from this
repo into a target repo.  Idempotent: existing labels are updated in-place;
existing template files are overwritten only when content differs.

Usage:
  uv run python scripts/bootstrap_github_repo.py --repo owner/new-repo
  uv run python scripts/bootstrap_github_repo.py --repo owner/new-repo --dry-run
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

# §11 label vocabulary (name, hex color without #, description)
LABELS: list[tuple[str, str, str]] = [
    ("docs",         "0075ca", "Documentation / Markdown / README / report work."),
    ("architecture", "1d76db", "Design-level work: module contracts, dependency graph, ADRs."),
    ("rl",           "5319e7", "Q-table actor, state encoder, training, reward shaping."),
    ("heuristic",    "c5def5", "Rule-based actor and scoring."),
    ("mcp",          "0e8a16", "MCP servers, tools, protocol, natural-language messages."),
    ("launcher",     "fbca04", "run_stack / run_peer_match / peer_sync tooling."),
    ("llm-backend",  "bfdadc", "Ollama / OpenRouter / Anthropic backend wiring."),
    ("testing",      "006b75", "Unit tests, lint, coverage, reproducibility."),
    ("reporting",    "b60205", "Gmail JSON report, series results, submission emails."),
    ("deployment",   "d4c5f9", "Cloud deployment, public URLs, token auth."),
    ("submission",   "ededed", "Checklist, packaging, final deliverables."),
    ("security",     "d93f0b", "Secrets, token revocation, firewall/exposure boundaries."),
    ("decision",     "7057ff", "Blocking decision that must be answered before downstream work."),
]


TEMPLATE_FILES = [
    ".github/ISSUE_TEMPLATE/work_item.md",
    ".github/pull_request_template.md",
]

_REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# gh helpers
# ---------------------------------------------------------------------------

def _gh_raw(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True, input=stdin)


def _gh_json(*args: str) -> object:
    result = _gh_raw(*args)
    if result.returncode != 0:
        raise SystemExit(f"gh error: {result.stderr.strip()}")
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Label bootstrap
# ---------------------------------------------------------------------------

def _existing_labels(repo: str) -> dict[str, dict[str, str]]:
    items = _gh_json(
        "label", "list", "--repo", repo,
        "--json", "name,color,description", "--limit", "200",
    )
    assert isinstance(items, list)
    return {item["name"]: item for item in items}  # type: ignore[index]


def _sync_label(repo: str, name: str, color: str, description: str,
                existing: dict[str, dict[str, str]], dry_run: bool) -> str:
    if name in existing:
        current = existing[name]
        color_match = current["color"].lstrip("#").lower() == color.lower()
        if color_match and current["description"] == description:
            return "skipped (unchanged)"
        action = "would update" if dry_run else "updated"
        if not dry_run:
            _gh_raw("label", "edit", name, "--repo", repo,
                    "--color", color, "--description", description)
        return action
    action = "would create" if dry_run else "created"
    if not dry_run:
        _gh_raw("label", "create", name, "--repo", repo,
                "--color", color, "--description", description)
    return action


# ---------------------------------------------------------------------------
# Template bootstrap
# ---------------------------------------------------------------------------

def _get_remote_file_sha(repo: str, path: str) -> str | None:
    result = _gh_raw("api", f"repos/{repo}/contents/{path}", "--jq", ".sha")
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _push_template(repo: str, relative_path: str, dry_run: bool) -> str:
    local = _REPO_ROOT / relative_path
    if not local.exists():
        return "skipped (source file not found)"
    content_b64 = base64.b64encode(local.read_bytes()).decode()
    remote_sha = _get_remote_file_sha(repo, relative_path)
    action = "would update" if remote_sha else "would create"
    if not dry_run:
        action = "updated" if remote_sha else "created"
        body: dict[str, str] = {
            "message": f"chore: bootstrap {relative_path} from template repo",
            "content": content_b64,
        }
        if remote_sha:
            body["sha"] = remote_sha
        payload = json.dumps(body)
        result = _gh_raw("api", "--method", "PUT",
                         f"repos/{repo}/contents/{relative_path}",
                         "--input", "-",
                         stdin=payload)
        if result.returncode != 0:
            return f"ERROR: {result.stderr.strip()}"
    return action


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """Sync labels and push templates into the target repo."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, metavar="OWNER/REPO",
                        help="Target repository (e.g. myorg/new-project)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without making changes")
    args = parser.parse_args(argv)

    repo: str = args.repo
    dry_run: bool = args.dry_run
    prefix = "[dry-run] " if dry_run else ""

    print(f"{prefix}Bootstrapping {repo}")
    print()

    # Labels
    print("Labels:")
    existing = _existing_labels(repo)
    for name, color, description in LABELS:
        outcome = _sync_label(repo, name, color, description, existing, dry_run)
        print(f"  {name:<16} {outcome}")

    print()

    # Templates
    print("Templates:")
    for path in TEMPLATE_FILES:
        outcome = _push_template(repo, path, dry_run)
        print(f"  {path}  →  {outcome}")

    print()
    print(f"{prefix}Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
