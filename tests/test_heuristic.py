"""Unit tests for actor_brains.heuristic_actor and heuristic_scoring (Phase 1)."""

from __future__ import annotations

from actor_brains import heuristic_scoring as scoring
from actor_brains.heuristic_actor import HeuristicActor
from tests.conftest import make_obs, make_result

# --- scoring helpers -------------------------------------------------------

def test_resolve_pos_moves_and_barrier_stays():
    assert scoring.resolve_pos((2, 2), "E") == (3, 2)
    assert scoring.resolve_pos((2, 2), "N") == (2, 1)
    assert scoring.resolve_pos((2, 2), "BARRIER") == (2, 2)


def test_resolve_pos_stay_keeps_position():
    # The submodule offers the thief a STAY action; it must not displace.
    assert scoring.resolve_pos((2, 2), "STAY") == (2, 2)


def test_thief_handles_stay_in_legal_moves():
    actor = HeuristicActor(role="thief")
    obs = make_obs(
        actor="thief", my_pos=(2, 2), opponent_pos=(0, 0),
        legal_moves=["N", "E", "S", "W", "STAY"],
    )
    assert actor.get_action(obs) in obs.legal_moves  # scores STAY without crashing


def test_chebyshev():
    assert scoring.chebyshev((0, 0), (3, 1)) == 3
    assert scoring.chebyshev((2, 2), (2, 2)) == 0


def test_edge_proximity_higher_at_edge():
    centre = scoring.edge_proximity((2, 2), (5, 5))
    corner = scoring.edge_proximity((0, 0), (5, 5))
    assert corner > centre


def test_openness_counts_free_neighbours():
    assert scoring.openness((2, 2), set(), (5, 5)) == 8
    assert scoring.openness((0, 0), set(), (5, 5)) == 3  # corner
    assert scoring.openness((2, 2), {(3, 2), (1, 1)}, (5, 5)) == 6


# --- actor behaviour -------------------------------------------------------

def test_cop_moves_toward_thief():
    actor = HeuristicActor(role="cop")
    obs = make_obs(actor="cop", my_pos=(0, 0), opponent_pos=(4, 4))
    # SE reduces Chebyshev distance to (4,4); cop should pick it.
    assert actor.get_action(obs) == "SE"


def test_thief_moves_away_from_cop():
    actor = HeuristicActor(role="thief")
    obs = make_obs(actor="thief", my_pos=(2, 2), opponent_pos=(1, 1))
    # Cop is adjacent to the NW; the thief must increase its distance away.
    chosen = actor.get_action(obs)
    new_pos = scoring.resolve_pos((2, 2), chosen)
    assert scoring.chebyshev(new_pos, (1, 1)) > scoring.chebyshev((2, 2), (1, 1))


def test_action_always_legal():
    actor = HeuristicActor(role="thief")
    obs = make_obs(actor="thief", my_pos=(0, 0), opponent_pos=(1, 1),
                   legal_moves=["E", "S", "SE"])
    assert actor.get_action(obs) in obs.legal_moves


def test_role_detected_from_obs_when_unset():
    actor = HeuristicActor(role=None)
    obs = make_obs(actor="cop", my_pos=(0, 0), opponent_pos=(4, 4))
    assert actor.get_action(obs) == "SE"  # behaves as cop


def test_handles_hidden_opponent_via_belief():
    actor = HeuristicActor(role="cop")
    actor.get_action(make_obs(actor="cop", my_pos=(0, 0), opponent_pos=(4, 4)))
    hidden = make_obs(actor="cop", round=2, my_pos=(1, 1), opponent_pos=None)
    assert actor.get_action(hidden) == "SE"  # pursues last sighting


def test_cop_considers_barrier_when_thief_cornered_adjacent():
    actor = HeuristicActor(role="cop")
    # Thief at (0,0) corner, cop adjacent at (1,1); BARRIER is a candidate.
    obs = make_obs(actor="cop", my_pos=(1, 1), opponent_pos=(0, 0),
                   legal_moves=["N", "E", "S", "BARRIER"], barriers_remaining=5)
    assert actor.get_action(obs) in obs.legal_moves


def test_on_result_updates_belief_no_crash():
    actor = HeuristicActor(role="cop")
    obs = make_obs(actor="cop", opponent_pos=(2, 2))
    actor.on_result(obs, "E", make_result(game_over=True, winner="cop"))


def test_save_and_load_roundtrip(tmp_path):
    actor = HeuristicActor(role="cop", weights={"distance_weight": 9.0,
                                                "barrier_weight": 1.0,
                                                "edge_weight": 1.0,
                                                "trap_penalty": 1.0,
                                                "cop_barrier_threshold": 3})
    path = tmp_path / "w.json"
    actor.save(path)
    loaded = HeuristicActor.load("cop", path)
    assert loaded._weights["distance_weight"] == 9.0


def test_load_missing_file_uses_defaults(tmp_path):
    actor = HeuristicActor.load("thief", tmp_path / "missing.json")
    assert actor._role == "thief"
    assert "distance_weight" in actor._weights


def test_load_invalid_role_falls_back_to_none(tmp_path):
    actor = HeuristicActor.load("spectator", tmp_path / "missing.json")
    assert actor._role is None
