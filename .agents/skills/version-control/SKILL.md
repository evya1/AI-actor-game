---
name: version-control
description: Manage global versioning (starting at 1.00), Git workflows with meaningful commits and branches, prompt engineering log, and uv package management. Use when setting up versioning, managing dependencies, or documenting AI-assisted development.
---

# Version Control & Package Management (uv)

## Global Version Tracking

Code and all config files must include explicit version tracking. Version starts at `1.00` and increments on significant changes.

| Item | Location | Initial Value |
|------|----------|---------------|
| Code version | `src/<pkg>/shared/version.py` | 1.00 |
| Config version | `"version"` key in JSON | 1.00 |
| Rate limit version | `"rate_limits.version"` | 1.00 |

The application must validate config version compatibility at startup.

## Git Best Practices

- Maintain clear commit history with meaningful messages
- Use branches for new feature development
- Code reviews via Pull Requests
- Tagging for major versions

## Prompt Engineering Log

Document the AI-assisted development process:

- List of all prompts used to build the project
- Context and purpose description
- Examples of outputs received
- Improvements made
- Best practices that became standard

## Package Manager — uv (MANDATORY)

All projects must use `uv` as the package and virtual environment manager. Never use `pip`, `python -m pip install`, `venv`, or `virtualenv`.

| Task | Correct (uv) | Forbidden |
|------|-------------|-----------|
| Install dependencies | `uv sync` | `pip install` |
| Add dependency | `uv add <pkg>` | `pip install <pkg>` |
| Run script | `uv run python script.py` | `python script.py` |
| Run tests | `uv run pytest tests/` | `python -m pytest` |
| Lock dependencies | `uv lock` | `pip freeze` |

### Requirements

- `pyproject.toml` is the single source of truth for dependencies (no `requirements.txt`)
- `uv.lock` must exist and be under version control
- No direct calls to `pip` or `python -m` in code, scripts, CI/CD, or documentation
- All tools executed via `uv run`

## Implementation Checklist

- [ ] Version `1.00` defined in `version.py` and config files
- [ ] Config version validation at startup
- [ ] Clear Git commit history with meaningful messages
- [ ] Feature branches for new development
- [ ] Pull Requests for code reviews
- [ ] Tags for major versions
- [ ] Prompt engineering log documented
- [ ] `pyproject.toml` as single dependency source
- [ ] `uv.lock` exists and is versioned
- [ ] All commands use `uv run` (no `pip` or `python -m`)
