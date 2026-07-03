#!/usr/bin/env python3
"""Verify or create GitHub milestones from ``config/milestones.json``.

Default is read-only verification. ``apply`` requires ``--confirm`` and
only creates milestones that are missing — it never deletes, modifies a
description, or changes open/closed state. Any structural conflict
aborts ``apply`` before any write; correct state is an idempotent no-op.
See ``scripts/README.md`` for operator instructions.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Protocol, TextIO

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _milestones_core import (  # noqa: E402
    LiveMilestone,
    Manifest,
    ManifestError,
    compute_diff,
    format_diff,
    load_manifest,
)
from _milestones_gh import GhClient, GhError, resolve_repo  # noqa: E402
from _milestones_output import format_accepted_preapply_diff  # noqa: E402

EXIT_OK = 0
EXIT_DIVERGED = 1
EXIT_MANIFEST_INVALID = 2
EXIT_GH_ERROR = 3
EXIT_CONFIRM_REQUIRED = 4
EXIT_APPLY_ABORTED = 5

DEFAULT_MANIFEST = "config/milestones.json"


class MilestoneClient(Protocol):
    """Minimal milestone API used by verify/dry-run/apply."""

    def list_milestones(self) -> list[LiveMilestone]:
        """Return all live milestones."""
        ...

    def create_milestone(self, title: str, description: str) -> LiveMilestone:
        """Create a milestone and return it."""
        ...


def verify(manifest: Manifest, client: MilestoneClient, *, out: TextIO, err: TextIO) -> int:
    """Read-only comparison of manifest vs live state."""
    diff = compute_diff(manifest, client.list_milestones())
    print(format_diff(diff), file=out)
    if diff.is_clean:
        print("Live state matches the manifest.", file=out)
        return EXIT_OK
    print("Live state diverges from the manifest.", file=err)
    return EXIT_DIVERGED


def dry_run(manifest: Manifest, client: MilestoneClient, *, out: TextIO, err: TextIO) -> int:
    """Show what apply would create without writing."""
    diff = compute_diff(manifest, client.list_milestones())
    print(format_diff(diff), file=out)
    for em in diff.missing:
        print(f"Would create: {em.title}", file=out)
    if diff.is_clean:
        print("No actions required.", file=out)
        return EXIT_OK
    return EXIT_DIVERGED


def apply(
    manifest: Manifest,
    client: MilestoneClient,
    *,
    confirm: bool,
    out: TextIO,
    err: TextIO,
) -> int:
    """Create only the missing milestones; abort on any conflict."""
    if not confirm:
        print("apply requires --confirm", file=err)
        return EXIT_CONFIRM_REQUIRED
    diff = compute_diff(manifest, client.list_milestones())
    if diff.has_blocking_conflict:
        print("Aborting apply: conflicts detected. No writes performed.", file=err)
        print(format_diff(diff), file=err)
        return EXIT_APPLY_ABORTED
    print(format_accepted_preapply_diff(diff), file=out)
    if not diff.missing:
        print("State already matches manifest. Zero writes performed.", file=out)
        return EXIT_OK
    for em in diff.missing:
        client.create_milestone(em.title, em.description)
        print(f"Created milestone: {em.title}", file=out)
    after = compute_diff(manifest, client.list_milestones())
    if not after.is_clean:
        print("Post-apply verification failed.", file=err)
        print(format_diff(after), file=err)
        return EXIT_DIVERGED
    print("Post-apply verification passed.", file=out)
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    """CLI definition."""
    parser = argparse.ArgumentParser(
        description="Verify or create GitHub milestones from a JSON manifest.",
    )
    parser.add_argument("command", choices=["verify", "dry-run", "apply"])
    parser.add_argument(
        "--repo",
        help="Explicit OWNER/NAME. Default resolves the current repository via gh.",
    )
    parser.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help=f"Path to the milestone manifest (default: {DEFAULT_MANIFEST}).",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required for `apply` to perform any write.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = build_parser().parse_args(argv)
    try:
        manifest = load_manifest(Path(args.manifest))
    except (ManifestError, FileNotFoundError, OSError) as exc:
        print(f"Manifest invalid: {exc}", file=sys.stderr)
        return EXIT_MANIFEST_INVALID
    try:
        repo = args.repo or resolve_repo()
    except GhError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_GH_ERROR
    print(f"Repository: {repo}")
    client = GhClient(repo)
    try:
        if args.command == "verify":
            return verify(manifest, client, out=sys.stdout, err=sys.stderr)
        if args.command == "dry-run":
            return dry_run(manifest, client, out=sys.stdout, err=sys.stderr)
        return apply(manifest, client, confirm=args.confirm, out=sys.stdout, err=sys.stderr)
    except GhError as exc:
        print(f"gh error: {exc}", file=sys.stderr)
        return EXIT_GH_ERROR


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
