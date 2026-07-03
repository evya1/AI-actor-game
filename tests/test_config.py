"""Unit tests for actor_brains.config (Phase 0)."""

from __future__ import annotations

import json

import pytest

from actor_brains import config


def test_load_defaults_when_file_missing(tmp_path):
    cfg = config.load_config(tmp_path / "nope.json")
    assert cfg == config.DEFAULTS
    assert cfg["rl"]["learning_rate"] == 0.1


def test_load_real_config_file_validates():
    cfg = config.load_config(config.DEFAULT_CONFIG_PATH)
    assert cfg["heuristic"]["distance_weight"] == 3.0
    assert cfg["rl"]["epsilon_min"] == 0.05


def test_partial_override_merges_over_defaults(tmp_path):
    path = tmp_path / "actor_config.json"
    path.write_text(json.dumps({"rl": {"learning_rate": 0.5}}))
    cfg = config.load_config(path)
    assert cfg["rl"]["learning_rate"] == 0.5  # overridden
    assert cfg["rl"]["discount_factor"] == 0.9  # default retained
    assert cfg["heuristic"]["distance_weight"] == 3.0  # untouched section


def test_invalid_json_raises(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json")
    with pytest.raises(ValueError, match="invalid JSON"):
        config.load_config(path)


def test_non_object_top_level_raises(tmp_path):
    path = tmp_path / "list.json"
    path.write_text("[1, 2, 3]")
    with pytest.raises(ValueError, match="must be an object"):
        config.load_config(path)


def test_validate_schema_rejects_missing_key():
    bad = {"heuristic": {"distance_weight": 1.0}, "rl": config.DEFAULTS["rl"]}
    with pytest.raises(ValueError, match="missing key"):
        config.validate_schema(bad)


def test_validate_schema_rejects_missing_section():
    with pytest.raises(ValueError, match="missing section 'rl'"):
        config.validate_schema({"heuristic": config.DEFAULTS["heuristic"]})


def test_validate_schema_rejects_non_numeric():
    bad = {
        "heuristic": {**config.DEFAULTS["heuristic"], "distance_weight": "high"},
        "rl": config.DEFAULTS["rl"],
    }
    with pytest.raises(ValueError, match="must be numeric"):
        config.validate_schema(bad)


def test_validate_schema_rejects_bool():
    bad = {
        "heuristic": {**config.DEFAULTS["heuristic"], "cop_barrier_threshold": True},
        "rl": config.DEFAULTS["rl"],
    }
    with pytest.raises(ValueError, match="must be numeric"):
        config.validate_schema(bad)
