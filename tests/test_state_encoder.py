"""Unit tests for actor_t6.state_encoder (Phase 2)."""

from __future__ import annotations

import itertools

from actor_t6.state_encoder import StateEncoder
from tests.conftest import make_obs

GRID = (5, 5)


def test_num_states_formula():
    # (2*5-1)^2 relative offsets * 2 edge * 4 barrier buckets + 1 unknown.
    assert StateEncoder.num_states(GRID) == 9 * 9 * 2 * 4 + 1


def test_indices_within_bounds_for_all_positions():
    n = StateEncoder.num_states(GRID)
    cells = list(itertools.product(range(5), range(5)))
    for my_pos, opp in itertools.product(cells, cells):
        if my_pos == opp:
            continue
        idx = StateEncoder.encode(make_obs(my_pos=my_pos, opponent_pos=opp), GRID)
        assert 0 <= idx < n


def test_relative_encoding_is_translation_invariant():
    # Same offset (+1,+1) from different cells, same edge/barrier context.
    a = StateEncoder.encode(make_obs(my_pos=(1, 1), opponent_pos=(2, 2)), GRID)
    b = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=(3, 3)), GRID)
    assert a == b


def test_distinct_offsets_differ():
    a = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=(3, 3)), GRID)
    b = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=(1, 1)), GRID)
    assert a != b


def test_unknown_opponent_uses_reserved_index():
    idx = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=None), GRID)
    assert idx == StateEncoder.num_states(GRID) - 1


def test_edge_flag_changes_state():
    centre = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=(3, 3)), GRID)
    edge = StateEncoder.encode(make_obs(my_pos=(0, 2), opponent_pos=(1, 3)), GRID)
    assert centre != edge


def test_barrier_proximity_changes_state():
    clear = StateEncoder.encode(make_obs(my_pos=(2, 2), opponent_pos=(3, 3)), GRID)
    walled = StateEncoder.encode(
        make_obs(my_pos=(2, 2), opponent_pos=(3, 3), barriers=[(2, 3), (3, 2)]), GRID
    )
    assert clear != walled
