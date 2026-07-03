"""StateEncoder — maps an observation to a compact Q-table row index (ADR-002).

A tabular Q-learner needs a small, discrete state space. Encoding the *relative*
opponent offset (dx, dy) instead of absolute positions gives translational
invariance and shrinks the table from hundreds of position pairs to ~81 offsets.
Two cheap context features are appended — a near-edge flag and a bucketed count
of nearby barriers — and a single reserved index represents an unseen opponent.

Leaf module — depends on nothing inside actor_brains.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.state import ObservationState

# Barrier counts within Chebyshev distance 2 are bucketed into 0..3.
_BARRIER_BUCKETS = 4
_BARRIER_PROXIMITY = 2
_EDGE_STATES = 2


def _relative_span(grid: tuple[int, int]) -> tuple[int, int]:
    """Return the number of distinct dx and dy offset values for a grid.

    Args:
        grid: Grid (cols, rows).

    Returns:
        ``(2*cols - 1, 2*rows - 1)`` — offsets span ``-(n-1)..(n-1)``.
    """
    cols, rows = grid
    return (2 * cols - 1, 2 * rows - 1)


class StateEncoder:
    """Maps an ObservationState to an integer index in ``[0, num_states)``."""

    @staticmethod
    def num_states(grid_size: tuple[int, int]) -> int:
        """Return the total number of distinct encoded states.

        Args:
            grid_size: Grid (cols, rows).

        Returns:
            Count of relative-offset states times context features, plus one
            reserved index for an unobserved opponent.
        """
        span_x, span_y = _relative_span(grid_size)
        return span_x * span_y * _EDGE_STATES * _BARRIER_BUCKETS + 1

    @staticmethod
    def encode(obs: ObservationState, grid_size: tuple[int, int]) -> int:
        """Encode an observation into its Q-table row index.

        Args:
            obs: Current observation; ``opponent_pos`` may be ``None``.
            grid_size: Grid (cols, rows).

        Returns:
            An integer in ``[0, num_states(grid_size))``. The final index is
            reserved for the case where the opponent is not observed.
        """
        cols, rows = grid_size
        if obs.opponent_pos is None:
            return StateEncoder.num_states(grid_size) - 1
        span_y = _relative_span(grid_size)[1]
        my_col, my_row = obs.my_pos
        dx = obs.opponent_pos[0] - my_col + (cols - 1)
        dy = obs.opponent_pos[1] - my_row + (rows - 1)
        rel = dx * span_y + dy
        edge = int(my_col in (0, cols - 1) or my_row in (0, rows - 1))
        near = sum(
            1 for b in obs.barriers
            if max(abs(b[0] - my_col), abs(b[1] - my_row)) <= _BARRIER_PROXIMITY
        )
        bucket = min(near, _BARRIER_BUCKETS - 1)
        return (rel * _EDGE_STATES + edge) * _BARRIER_BUCKETS + bucket
