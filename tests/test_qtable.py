"""Unit tests for actor_t6.qtable_actor (Phase 2)."""

from __future__ import annotations

import numpy as np

from actor_t6.qtable_actor import ACTIONS, QTableActor
from actor_t6.state_encoder import StateEncoder
from tests.conftest import make_obs, make_result

GRID = (5, 5)


def test_qtable_shape_matches_state_action_space():
    actor = QTableActor(role="cop", grid_size=GRID)
    assert actor.q_table.shape == (StateEncoder.num_states(GRID), len(ACTIONS))
    assert np.all(actor.q_table == 0)


def test_epsilon_one_explores_legally():
    actor = QTableActor(role="thief", grid_size=GRID, epsilon_start=1.0)
    obs = make_obs(actor="thief", legal_moves=["N", "E", "S"])
    for _ in range(20):
        assert actor.get_action(obs) in obs.legal_moves


def test_greedy_picks_highest_q_action():
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0)
    obs = make_obs(actor="cop", my_pos=(2, 2), opponent_pos=(4, 4),
                   legal_moves=["N", "SE", "W"])
    state = StateEncoder.encode(obs, GRID)
    actor.q_table[state, ACTIONS.index("SE")] = 5.0
    assert actor.get_action(obs) == "SE"


def test_terminal_bellman_update_moves_toward_reward():
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=0.5, win_reward=10.0)
    obs = make_obs(actor="cop", my_pos=(3, 3), opponent_pos=(4, 4),
                   legal_moves=["SE", "N"])
    chosen = actor.get_action(obs)
    state = StateEncoder.encode(obs, GRID)
    actor.on_result(obs, chosen, make_result(game_over=True, winner="cop"))
    # Q(s,a) += 0.5 * (10 - 0) = 5.0
    assert actor.q_table[state, ACTIONS.index(chosen)] == 5.0


def test_loss_update_is_negative():
    actor = QTableActor(role="thief", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=0.5, lose_reward=-10.0)
    obs = make_obs(actor="thief", my_pos=(3, 3), opponent_pos=(4, 4),
                   legal_moves=["SE", "N"])
    chosen = actor.get_action(obs)
    state = StateEncoder.encode(obs, GRID)
    actor.on_result(obs, chosen, make_result(game_over=True, winner="cop"))
    assert actor.q_table[state, ACTIONS.index(chosen)] == -5.0


def test_non_terminal_then_bootstrap_update():
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=1.0, discount_factor=0.9, step_cost=1.0)
    obs1 = make_obs(actor="cop", round=1, my_pos=(0, 0), opponent_pos=(4, 4),
                    legal_moves=["SE", "E"])
    a1 = actor.get_action(obs1)
    s1 = StateEncoder.encode(obs1, GRID)
    actor.on_result(obs1, a1, make_result(game_over=False))  # pending reward -1
    obs2 = make_obs(actor="cop", round=2, my_pos=(1, 1), opponent_pos=(4, 4),
                    legal_moves=["SE", "E"])
    s2 = StateEncoder.encode(obs2, GRID)
    actor.q_table[s2] = 2.0  # so max Q(s') = 2.0
    actor.get_action(obs2)   # triggers bootstrap of the (s1,a1) transition
    # Q(s1,a1) += 1.0 * (-1 + 0.9*2.0 - 0) = 0.8
    assert abs(actor.q_table[s1, ACTIONS.index(a1)] - 0.8) < 1e-9


def test_epsilon_decays_on_game_over():
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=1.0,
                        epsilon_decay=0.5, epsilon_min=0.05)
    obs = make_obs(actor="cop", legal_moves=["N", "E"])
    actor.get_action(obs)
    actor.on_result(obs, "N", make_result(game_over=True, winner="cop"))
    assert actor.epsilon == 0.5


def test_on_result_without_action_is_noop():
    actor = QTableActor(role="cop", grid_size=GRID)
    actor.on_result(make_obs(), "N", make_result(game_over=True, winner="cop"))
    assert np.all(actor.q_table == 0)


def test_save_and_load_roundtrip_sets_epsilon_zero(tmp_path):
    actor = QTableActor(role="cop", grid_size=GRID)
    obs = make_obs(actor="cop", legal_moves=["N", "E"])
    actor.get_action(obs)
    actor.on_result(obs, "N", make_result(game_over=True, winner="cop"))
    path = tmp_path / "cop_qtable.npy"
    actor.save(path)
    loaded = QTableActor.load("cop", path, grid_size=GRID)
    assert loaded.epsilon == 0.0
    assert np.array_equal(loaded.q_table, actor.q_table)


def test_load_missing_file_cold_start(tmp_path):
    actor = QTableActor.load("thief", tmp_path / "missing.npy", grid_size=GRID)
    assert actor.epsilon == 0.0
    assert np.all(actor.q_table == 0)
    assert actor._role == "thief"


def test_load_appends_npy_suffix_when_missing(tmp_path):
    actor = QTableActor(role="cop", grid_size=GRID)
    actor.q_table[0, 0] = 7.0
    actor.save(tmp_path / "cop_qtable.npy")
    # Pass a suffix-less path; load() should append .npy and find the file.
    loaded = QTableActor.load("cop", tmp_path / "cop_qtable", grid_size=GRID)
    assert loaded.q_table[0, 0] == 7.0


def test_load_ignores_shape_mismatched_table(tmp_path):
    path = tmp_path / "wrong.npy"
    np.save(str(path), np.ones((3, 3)))  # shape != (num_states, num_actions)
    loaded = QTableActor.load("cop", path, grid_size=GRID)
    assert loaded.q_table.shape == (StateEncoder.num_states(GRID), len(ACTIONS))
    assert np.all(loaded.q_table == 0)
