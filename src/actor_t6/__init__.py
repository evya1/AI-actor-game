"""actor_t6 — Cop & Thief decision backends for the HW6 MCP game.

This package supplies the team-specific actor "brains" loaded by the read-only
``agent-orchestration-course-t6-common`` submodule via the ``ACTOR_CLASS`` env
var. It exposes two interchangeable :class:`actor.base_actor.BaseActor`
strategies — :class:`~actor_t6.heuristic_actor.HeuristicActor` and
:class:`~actor_t6.qtable_actor.QTableActor` — plus shared utilities.
"""

from __future__ import annotations

from actor_t6.shared.version import __version__

__all__ = ["__version__"]
