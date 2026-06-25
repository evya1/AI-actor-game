---
name: code-review-config
description: Enforce zero Ruff lint violations, externalize all configuration values, manage secrets securely with .env files. Use when reviewing code, setting up configuration, or handling sensitive data.
---

# Code Review, Configuration & Security

## Linter — Zero Ruff Violations

Zero Ruff violations allowed. All code must pass `ruff check` without errors.

### Ruff Configuration (`pyproject.toml`)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "N", "I", "UP", "B", "C4", "SIM"]
ignore = ["E501"]
```

### Active Rule Categories

| Category | Description |
|----------|-------------|
| E | PEP 8 errors (indentation, spacing, style) |
| F | Pyflakes (undefined names, unused imports) |
| W | PEP 8 warnings |
| I | Import ordering |
| N | pep8-naming (naming conventions) |
| UP | pyupgrade (modernize to Python 3.10+) |
| B | flake8-bugbear (common bugs) |
| C4 | Comprehension usage |
| SIM | Expression simplification |

## No Hardcoded Values

All configuration values must come from config files, never from source code.

| Category | Wrong | Right |
|----------|-------|-------|
| API URLs | `"https://api.example.com"` | `cfg.get("api_url")` |
| Rate limits | `rate_limit = 10` | `cfg.get("rate_limit", 10)` |
| Timeouts | `timeout=60` | `cfg.get("timeout", 60)` |
| Secrets | `api_key = "abc123"` | `os.environ.get("API_KEY")` |

### Allowed Hardcoded Values

- Physical/mathematical constants
- Default parameter values
- Constants in `constants.py`
- `Enum` values

## Configuration Architecture

```text
config/
├── setup.json                # Main app config (versioned)
├── rate_limits.json          # API rate limits (versioned)
├── logging_config.json       # Logging configuration
├── .env                     # Secrets (git-ignored)
├── .env-example              # Secret placeholders (committed)
├── pyproject.toml            # Build, lint, test settings
└── src/<package>/constants.py # Immutable project constants
```

## Security & Secrets Management

- Never store API keys, passwords, or tokens in source code
- Use environment variables only: `os.environ.get("API_KEY")`
- `.gitignore` must include: `.env`, `*.key`, `*.pem`, `credentials.json`
- `.env-example` must exist with placeholder values
- In production — use secrets management tools
- Rotate keys periodically, monitor usage, restrict permissions to minimum

## Implementation Checklist

- [ ] `ruff check` passes with zero violations
- [ ] No hardcoded API URLs, rate limits, timeouts, or secrets
- [ ] Configuration loaded from separate JSON/env files
- [ ] `.env-example` exists with placeholder values
- [ ] `.gitignore` blocks sensitive files
- [ ] Secrets accessed via `os.environ.get()`
- [ ] Constants in `constants.py` for immutable values
