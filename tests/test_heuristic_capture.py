"""Capture-priority regressions for the heuristic Cop."""

from __future__ import annotations

from actor_t6 import heuristic_scoring as scoring
from actor_t6.heuristic_actor import HeuristicActor
from tests.conftest import make_obs


def test_cop_capture_dominates_trap_penalty_and_barrier_bonus():
    actor = HeuristicActor(role="cop")
    obs = make_obs(
        actor="cop", my_pos=(1, 0), opponent_pos=(0, 0),
        barriers=[(0, 1), (1, 1)], legal_moves=["W", "E", "SE", "BARRIER"],
        barriers_remaining=5,
    )
    assert actor.get_action(obs) == "W"


def test_extreme_weights_cannot_outweigh_cop_capture():
    actor = HeuristicActor(
        role="cop",
        weights={
            "distance_weight": 0.01,
            "barrier_weight": 10_000.0,
            "edge_weight": 1.0,
            "trap_penalty": 10_000.0,
            "cop_barrier_threshold": 3,
        },
        grid_size=(3, 3),
    )
    obs = make_obs(
        actor="cop", my_pos=(1, 0), opponent_pos=(0, 0),
        barriers=[(0, 1), (1, 1)], legal_moves=["W", "BARRIER"],
        barriers_remaining=5,
    )
    assert actor.get_action(obs) == "W"


def test_non_capture_moves_keep_relative_distance_scoring():
    weights = {"distance_weight": 3.0, "barrier_weight": 2.0, "edge_weight": 1.5,
               "trap_penalty": 4.0, "cop_barrier_threshold": 3}
    toward = scoring.score_move((0, 0), "SE", (4, 4), "cop", weights, set(), (5, 5))
    away = scoring.score_move((0, 0), "E", (4, 4), "cop", weights, set(), (5, 5))
    assert toward > away


def test_barrier_does_not_score_as_capture():
    score = scoring.score_move(
        (1, 0), "BARRIER", (1, 0), "cop",
        {"distance_weight": 3.0, "barrier_weight": 2.0, "edge_weight": 1.5,
         "trap_penalty": 4.0, "cop_barrier_threshold": 3},
        set(), (3, 3),
    )
    assert score != float("inf")
