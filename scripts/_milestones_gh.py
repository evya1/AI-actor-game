"""GitHub adapter for the milestone manifest sync tool.

Thin wrapper around the ``gh`` CLI for listing and creating milestones. Kept
separate from the domain logic in ``_milestones_core`` so tests can run
hermetically against a fake client without touching the network. Every
subprocess call uses an explicit argument list (never ``shell=True``), a
bounded timeout, and surfaces ``gh`` stderr in the raised error.
"""

from __future__ import annotations

import json
import subprocess

from _milestones_core import LiveMilestone

GH_TIMEOUT_SECONDS = 60


class GhError(RuntimeError):
    """Raised when a ``gh`` invocation fails or returns unparseable output."""


class GhClient:
    def __init__(self, repo: str, timeout: int = GH_TIMEOUT_SECONDS) -> None:
        assert isinstance(repo, str) and "/" in repo, "repo must look like OWNER/NAME"
        self.repo = repo
        self.timeout = timeout

    def list_milestones(self) -> list[LiveMilestone]:
        stdout = self._run(
            [
                "api",
                "--paginate",
                "--slurp",
                f"repos/{self.repo}/milestones?state=all&per_page=100",
            ]
        )
        try:
            data = _flatten_pages(json.loads(stdout))
        except json.JSONDecodeError as exc:
            raise GhError(f"gh returned unparseable JSON: {exc}") from exc
        if not isinstance(data, list):
            raise GhError(f"gh returned a non-list payload: {type(data).__name__}")
        return [_to_live(m) for m in data]

    def create_milestone(self, title: str, description: str) -> LiveMilestone:
        stdout = self._run(
            [
                "api",
                "--method",
                "POST",
                f"repos/{self.repo}/milestones",
                "-f",
                f"title={title}",
                "-f",
                f"description={description}",
            ]
        )
        try:
            return _to_live(json.loads(stdout))
        except json.JSONDecodeError as exc:
            raise GhError(f"gh returned unparseable JSON: {exc}") from exc

    def _run(self, args: list[str]) -> str:
        try:
            proc = subprocess.run(
                ["gh", *args],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise GhError("gh CLI not found on PATH") from exc
        except subprocess.TimeoutExpired as exc:
            raise GhError(f"gh timed out after {self.timeout}s") from exc
        if proc.returncode != 0:
            raise GhError(
                f"gh {' '.join(args)} failed (exit {proc.returncode}): {proc.stderr.strip()}"
            )
        return proc.stdout


def _to_live(payload: dict) -> LiveMilestone:
    return LiveMilestone(
        number=int(payload["number"]),
        title=str(payload["title"]),
        description=str(payload.get("description") or ""),
        due_on=payload.get("due_on"),
        state=str(payload.get("state", "open")),
    )


def _flatten_pages(payload: object) -> object:
    """Flatten ``gh api --paginate --slurp`` output while accepting one page."""
    if not isinstance(payload, list):
        return payload
    if not payload or isinstance(payload[0], dict):
        return payload
    milestones: list[dict] = []
    for i, page in enumerate(payload):
        if not isinstance(page, list):
            raise GhError(f"gh returned a non-list page at index {i}")
        milestones.extend(page)
    return milestones


def resolve_repo(timeout: int = GH_TIMEOUT_SECONDS) -> str:
    try:
        proc = subprocess.run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GhError("gh CLI not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise GhError(f"gh repo view timed out after {timeout}s") from exc
    if proc.returncode != 0:
        raise GhError(
            "Could not resolve current repository via gh. "
            "Pass --repo OWNER/NAME explicitly. "
            f"stderr: {proc.stderr.strip()}"
        )
    name = proc.stdout.strip()
    if not name or "/" not in name:
        raise GhError(f"gh returned an unexpected repository name: {name!r}")
    return name
