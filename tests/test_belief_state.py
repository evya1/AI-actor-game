"""Unit tests for actor_t6.belief_state (Phase 1)."""

from __future__ import annotations

from actor_t6.belief_state import BeliefState
from tests.conftest import make_obs


def test_initial_estimate_is_none():
    assert BeliefState().get_estimate() is None


def test_update_sets_estimate_from_visible_opponent():
    bs = BeliefState()
    bs.update(make_obs(round=1, opponent_pos=(3, 2)))
    assert bs.get_estimate() == (3, 2)


def test_estimate_retained_when_opponent_hidden():
    bs = BeliefState()
    bs.update(make_obs(round=1, opponent_pos=(3, 2)))
    bs.update(make_obs(round=2, opponent_pos=None))
    assert bs.get_estimate() == (3, 2)  # last sighting retained


def test_estimate_refreshes_on_new_sighting():
    bs = BeliefState()
    bs.update(make_obs(round=2, opponent_pos=(3, 2)))
    bs.update(make_obs(round=3, opponent_pos=(1, 1)))
    assert bs.get_estimate() == (1, 1)


def test_new_subgame_resets_estimate():
    bs = BeliefState()
    bs.update(make_obs(round=4, opponent_pos=(3, 2)))
    bs.update(make_obs(round=1, opponent_pos=None))  # new sub-game
    assert bs.get_estimate() is None


def test_explicit_reset():
    bs = BeliefState()
    bs.update(make_obs(opponent_pos=(2, 2)))
    bs.reset()
    assert bs.get_estimate() is None
