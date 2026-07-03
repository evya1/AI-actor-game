"""Regression tests for legal-action Bellman targets."""

from __future__ import annotations

from actor_brains.qtable_actor import ACTIONS, QTableActor
from actor_brains.state_encoder import StateEncoder
from tests.conftest import make_obs, make_result

GRID = (5, 5)


def _prime_pending(actor: QTableActor) -> tuple[int, str]:
    obs = make_obs(actor="cop", my_pos=(1, 1), opponent_pos=(4, 4), legal_moves=["E", "S"])
    action = actor.get_action(obs)
    state = StateEncoder.encode(obs, GRID)
    actor.on_result(obs, action, make_result(game_over=False))
    return state, action


def test_bootstrap_ignores_large_illegal_column() -> None:
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=1.0, discount_factor=1.0, step_cost=0.0)
    state, action = _prime_pending(actor)
    nxt = make_obs(actor="cop", round=2, my_pos=(2, 1), opponent_pos=(4, 4),
                   legal_moves=["S", "E"])
    next_state = StateEncoder.encode(nxt, GRID)
    actor.q_table[next_state, ACTIONS.index("N")] = 999.0
    actor.q_table[next_state, ACTIONS.index("S")] = 2.0
    actor.get_action(nxt)
    assert actor.q_table[state, ACTIONS.index(action)] == 2.0


def test_bootstrap_uses_best_legal_value_when_negative() -> None:
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=1.0, discount_factor=1.0, step_cost=0.0)
    state, action = _prime_pending(actor)
    nxt = make_obs(actor="cop", round=2, my_pos=(2, 1), opponent_pos=(4, 4),
                   legal_moves=["S", "E"])
    next_state = StateEncoder.encode(nxt, GRID)
    actor.q_table[next_state] = -100.0
    actor.q_table[next_state, ACTIONS.index("S")] = -5.0
    actor.q_table[next_state, ACTIONS.index("E")] = -7.0
    actor.get_action(nxt)
    assert actor.q_table[state, ACTIONS.index(action)] == -5.0


def test_cop_does_not_bootstrap_from_stay() -> None:
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=1.0, discount_factor=1.0, step_cost=0.0)
    state, action = _prime_pending(actor)
    nxt = make_obs(actor="cop", round=2, my_pos=(2, 1), opponent_pos=(4, 4),
                   legal_moves=["S", "E"])
    next_state = StateEncoder.encode(nxt, GRID)
    actor.q_table[next_state, ACTIONS.index("STAY")] = 50.0
    actor.q_table[next_state, ACTIONS.index("E")] = 3.0
    actor.get_action(nxt)
    assert actor.q_table[state, ACTIONS.index(action)] == 3.0


def test_terminal_update_does_not_bootstrap() -> None:
    actor = QTableActor(role="cop", grid_size=GRID, epsilon_start=0.0,
                        learning_rate=1.0, discount_factor=1.0, win_reward=10.0)
    obs = make_obs(actor="cop", my_pos=(3, 3), opponent_pos=(4, 4), legal_moves=["SE"])
    action = actor.get_action(obs)
    state = StateEncoder.encode(obs, GRID)
    actor.on_result(obs, action, make_result(game_over=True, winner="cop"))
    nxt = make_obs(actor="cop", round=2, my_pos=(4, 4), opponent_pos=(4, 4),
                   legal_moves=["N"])
    actor.q_table[StateEncoder.encode(nxt, GRID), ACTIONS.index("N")] = 99.0
    actor.get_action(nxt)
    assert actor.q_table[state, ACTIONS.index(action)] == 10.0
