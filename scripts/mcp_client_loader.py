"""Lazy FastMCP client imports for scripts that must stay test-importable."""

from __future__ import annotations


def client_auth() -> tuple[object, object]:
    """Return FastMCP Client and BearerAuth classes."""
    from fastmcp import Client
    from fastmcp.client.auth.bearer import BearerAuth

    return Client, BearerAuth
