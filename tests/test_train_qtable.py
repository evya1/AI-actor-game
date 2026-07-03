"""Tests for deterministic Q-table training setup."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import train_qtable  # noqa: E402


def test_train_reuses_seed_for_repeatable_tables():
    first = train_qtable.train(episodes=3, seed=123, grid=(3, 3))
    second = train_qtable.train(episodes=3, seed=123, grid=(3, 3))
    assert np.array_equal(first["cop"].q_table, second["cop"].q_table)
    assert np.array_equal(first["thief"].q_table, second["thief"].q_table)
