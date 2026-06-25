---
name: project-setup
description: Set up professional project structure with mandatory documentation (README, PRD, PLAN, TODO), modular folder layout, and code quality standards. Use when starting a new project or organizing an existing codebase.
---

# Project Setup & Documentation

Set up a professional software project with proper structure and documentation.

## Mandatory Project Structure

Create the following directory layout:

```text
project-root/
├── src/                              # Source code
│   ├── <package>/
│   │   ├── __init__.py
│   │   ├── sdk/                      # SDK layer
│   │   │   └── sdk.py
│   │   ├── services/                 # Business logic
│   │   ├── shared/                   # Shared utilities
│   │   │   ├── gatekeeper.py         # API gatekeeper
│   │   │   ├── config.py             # Configuration manager
│   │   │   └── version.py            # Version tracking
│   │   └── constants.py
│   └── main.py
├── tests/                            # Unit and integration tests
│   ├── unit/
│   └── integration/
├── docs/                             # Documentation (MANDATORY)
│   ├── PRD.md                        # Product Requirements
│   ├── PLAN.md                       # Architecture & Planning
│   ├── TODO.md                       # Task tracking
│   └── PRD_<mechanism>.md            # Per-algorithm PRDs
├── config/                           # Configuration files
│   ├── setup.json
│   └── rate_limits.json
├── data/                             # Input data
├── results/                          # Experiment results
├── assets/                           # Images, graphs, resources
├── notebooks/                        # Analysis notebooks
├── README.md                         # MANDATORY
├── pyproject.toml                    # Build & dependencies
├── uv.lock                           # Locked dependencies
├── .env-example                      # Secret placeholders
└── .gitignore
```

## Mandatory Documents

### README.md (Root)
Must include:
- Installation instructions (system requirements, step-by-step, env vars, troubleshooting)
- Usage instructions (GUI, CLI, typical workflow)
- Examples and demos (code samples, screenshots, use case diagrams)
- Configuration guide (config files, parameters, their effects)
- Contribution guidelines (code standards and style)
- License and credits

### docs/PRD.md (Product Requirements Document)
Must include:
- Project overview and context, user problem description, market analysis, target audience
- Goals and success metrics, KPIs, acceptance criteria
- Functional and non-functional requirements, user stories, common workflows
- Constraints, dependencies, limitations, out-of-scope items
- Timeline and milestones with expected deliverables

### docs/PLAN.md (Architecture & Planning)
Must include:
- C4 Model diagrams (Context, Container, Component, Code)
- UML diagrams for complex processes, deployment diagrams
- Architectural Decision Records (ADRs) with rationale, trade-offs, alternatives
- API documentation and interfaces, data schemas and contracts

### docs/TODO.md (Task Tracking)
Must include:
- Detailed task list with priorities and status (Not Started / In Progress / Done)
- Phases with milestones
- Responsibility assignment per task
- Definition of Done per task

### Per-Algorithm PRDs
Create dedicated PRD for every algorithm, mechanism, or complex technical component:
- `docs/PRD_ml_algorithm.md`, `docs/PRD_authentication.md`, etc.
- Include: detailed description with theoretical background, specific requirements, expected I/O, performance metrics, constraints, alternatives considered, success criteria, test diagrams

## Mandatory Work Process

Follow this order before writing any code:
1. Create `docs/PRD.md` — get approval before continuing
2. Create `docs/PLAN.md` — architectural planning
3. Create `docs/TODO.md` — task list
4. Create per-algorithm PRDs for each central mechanism
5. Get approval for all documents before starting development
6. Start development — update `TODO.md` with progress
7. Save results, create visualizations, update `README.md`

## File Size Rule

- Maximum **150 lines of code** per file
- When a file exceeds the limit, split it — never compress code to fit
- Split strategies:
  - **Helper functions** — independent functions to separate file
  - **Mixin extraction** — when a class has multiple responsibilities
  - **50/50 split** — when there are two logic parts (read/write)
  - **Constants extraction** — `constants.py` to separate file
  - **Module extraction** — module definitions to separate file

## Code Quality Standards

- Comments explain the "why" not just the "what"
- Detailed docstrings for every function, class, and module
- Descriptive and precise variable and function names
- Short, focused functions following Single Responsibility Principle
- No code duplication (DRY principle)
- Consistent code style across the entire project
