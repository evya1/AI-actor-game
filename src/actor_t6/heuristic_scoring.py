"""Pure scoring helpers for the heuristic actor.

Extracted from :mod:`actor_t6.heuristic_actor` to keep each file within the
150-line limit and to make the scoring logic independently testable. All
functions are stateless and operate on plain tuples, so they carry no game
state of their own.

Direction deltas are reused from the read-only submodule
(:data:`game.constants.DIRECTIONS`) rather than redefined here (DRY).
"""

from __future__ import annotations

from game.constants import BARRIER_ACTION, COP, DIRECTIONS

# Movement directions only (BARRIER does not displace the actor).
_MOVE_DELTAS = DIRECTIONS


def resolve_pos(pos: tuple[int, int], action: str) -> tuple[int, int]:
    """Return the cell the actor occupies after taking ``action``.

    Args:
        pos: Current (col, row).
        action: A direction key or ``BARRIER`` (which does not move the actor).

    Returns:
        The resulting (col, row); identical to ``pos`` for ``BARRIER``.
    """
    if action == BARRIER_ACTION:
        return pos
    dc, dr = _MOVE_DELTAS[action]
    return (pos[0] + dc, pos[1] + dr)


def chebyshev(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Return the Chebyshev (king-move) distance between two cells.

    Args:
        a: First cell (col, row).
        b: Second cell (col, row).

    Returns:
        ``max(|dx|, |dy|)`` — the minimum number of 8-directional steps.
    """
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def edge_proximity(pos: tuple[int, int], grid: tuple[int, int]) -> float:
    """Return how close ``pos`` sits to the board edge (0 centre … 1 edge).

    Args:
        pos: Cell (col, row).
        grid: Grid (cols, rows).

    Returns:
        ``1 / (1 + d)`` where ``d`` is the Chebyshev distance to the nearest
        wall — near 1.0 on an edge/corner, smaller toward the centre.
    """
    cols, rows = grid
    dist_to_wall = min(pos[0], cols - 1 - pos[0], pos[1], rows - 1 - pos[1])
    return 1.0 / (1.0 + max(dist_to_wall, 0))


def openness(pos: tuple[int, int], barriers: set[tuple[int, int]],
             grid: tuple[int, int]) -> int:
    """Return the count of free, on-board, non-barrier neighbours of ``pos``.

    A low value flags a near-trapped cell (few escape routes).

    Args:
        pos: Cell (col, row) to evaluate.
        barriers: Set of barrier cells.
        grid: Grid (cols, rows).

    Returns:
        Number of the 8 neighbouring cells that are on-board and barrier-free.
    """
    cols, rows = grid
    free = 0
    for dc, dr in _MOVE_DELTAS.values():
        nbr = (pos[0] + dc, pos[1] + dr)
        if 0 <= nbr[0] < cols and 0 <= nbr[1] < rows and nbr not in barriers:
            free += 1
    return free


def score_move(my_pos: tuple[int, int], action: str,
               target: tuple[int, int] | None, role: str,
               weights: dict, barriers: set[tuple[int, int]],
               grid: tuple[int, int]) -> float:
    """Score one candidate action from this actor's perspective.

    The cop minimises distance to the target (landing on it captures); the
    thief maximises distance and avoids edges, barriers, and low-openness
    cells. ``BARRIER`` keeps the cop in place but earns a cornering bonus when
    an adjacent target has few escape routes.

    Args:
        my_pos: Actor's current cell.
        action: Candidate action (direction or ``BARRIER``).
        target: Estimated opponent cell, or ``None`` if unknown.
        role: ``"cop"`` or ``"thief"``.
        weights: Heuristic weight mapping (see config ``heuristic`` section).
        barriers: Set of current barrier cells.
        grid: Grid (cols, rows).

    Returns:
        A float score; higher is better for this actor.
    """
    nxt = resolve_pos(my_pos, action)
    score = 0.0
    if target is not None:
        dist = chebyshev(nxt, target)
        sign = -1.0 if role == COP else 1.0
        score += sign * weights["distance_weight"] * dist
    if role != COP:
        adj_barriers = sum(1 for b in barriers if chebyshev(nxt, b) <= 1)
        score -= weights["barrier_weight"] * adj_barriers
        score -= weights["edge_weight"] * edge_proximity(nxt, grid)
    free = openness(nxt, barriers, grid)
    if free <= 2:
        penalty = weights["trap_penalty"] * (3 - free)
        score -= penalty if role != COP else 0.5 * penalty
    if action == BARRIER_ACTION and target is not None and chebyshev(my_pos, target) <= 1:
        score += weights["barrier_weight"] * (3 - openness(target, barriers, grid))
    return score
