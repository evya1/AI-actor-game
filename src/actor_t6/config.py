"""Actor configuration loader (PRD §3.6 FR-05, PLAN §6.1).

Loads ``config/actor_config.json`` and merges it over built-in defaults so a
missing file or partial config still yields a complete, valid configuration.
Defaults live here — not in the actors — so every consumer sees identical
fallback values and no hyperparameter is hard-coded inside strategy code.
"""

from __future__ import annotations

import json
from pathlib import Path

# Repo root = three levels up from this file (src/actor_t6/config.py).
_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = _REPO_ROOT / "config" / "actor_config.json"

# Built-in defaults mirror config/actor_config.json (PLAN §6.1). They are the
# single fallback source when the file is absent or a key is omitted.
DEFAULTS: dict[str, dict] = {
    "heuristic": {
        "distance_weight": 3.0,
        "barrier_weight": 2.0,
        "edge_weight": 1.5,
        "trap_penalty": 4.0,
        "cop_barrier_threshold": 3,
    },
    "rl": {
        "learning_rate": 0.1,
        "discount_factor": 0.9,
        "epsilon_start": 1.0,
        "epsilon_decay": 0.995,
        "epsilon_min": 0.05,
        "win_reward": 10.0,
        "lose_reward": -10.0,
        "step_cost": 0.1,
    },
}

# Required numeric keys per section, used by validate_schema.
_REQUIRED: dict[str, tuple[str, ...]] = {
    "heuristic": tuple(DEFAULTS["heuristic"]),
    "rl": tuple(DEFAULTS["rl"]),
}


def _merge(defaults: dict, override: dict) -> dict:
    """Return defaults deep-merged with override (override wins per key).

    Args:
        defaults: Base mapping providing fallback values.
        override: Mapping whose present keys replace defaults.

    Returns:
        A new merged dict; nested section dicts are merged one level deep.
    """
    merged = {section: dict(values) for section, values in defaults.items()}
    for section, values in override.items():
        if isinstance(values, dict) and isinstance(merged.get(section), dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged


def validate_schema(config: dict) -> None:
    """Validate a merged config: required keys present and numeric.

    Args:
        config: The merged configuration dict to validate.

    Raises:
        ValueError: If a required section/key is missing or a value is not a
            real number (bool is rejected — it is not a valid weight).
    """
    for section, keys in _REQUIRED.items():
        if section not in config or not isinstance(config[section], dict):
            raise ValueError(f"config: missing section '{section}'")
        for key in keys:
            if key not in config[section]:
                raise ValueError(f"config: missing key '{section}.{key}'")
            value = config[section][key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"config: '{section}.{key}' must be numeric")


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> dict:
    """Load actor config from JSON, merge over defaults, and validate.

    A missing file is not an error: the built-in defaults are returned. A file
    that exists but is malformed JSON raises, since that signals a real mistake.

    Args:
        path: Path to the JSON config file.

    Returns:
        A validated configuration dict with ``heuristic`` and ``rl`` sections.

    Raises:
        ValueError: If the file is invalid JSON or fails schema validation.
    """
    path = Path(path)
    if path.exists():
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise ValueError(f"config: invalid JSON in {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"config: top level of {path} must be an object")
    else:
        raw = {}
    merged = _merge(DEFAULTS, raw)
    validate_schema(merged)
    return merged
