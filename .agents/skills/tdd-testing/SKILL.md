---
name: tdd-testing
description: Implement Test-Driven Development (TDD) with minimum 85% coverage, edge case handling, and automated test reporting. Use when writing tests or implementing new features.
---

# TDD & Quality Assurance

All development must follow Test-Driven Development: **RED → GREEN → REFACTOR**.

## TDD Process

1. **RED** — Write a failing test for the new functionality
2. **GREEN** — Write minimal code to make the test pass
3. **REFACTOR** — Improve code quality while keeping tests green

## Test Structure

```text
tests/
├── unit/
│   ├── test_<module>/      # Mirror src/ structure
│   └── test_<file>.py
└── integration/
    ├── test_<feature>.py
    └── conftest.py         # Shared fixtures
```

## Test Rules

1. Every new module must have a corresponding test file
2. Every public function/method must have at least one test
3. Tests cover both happy path and error cases
4. Tests are written before or alongside implementation, not as an afterthought
5. Use fixtures from `conftest.py` for shared test data
6. Mock external dependencies (database, files, API)
7. Test files also follow the 150-line rule
8. No tests depend on external services

## Coverage Requirements

- **Minimum 85% global coverage** — build fails if below threshold
- Required coverage types:
  - Statement coverage
  - Branch coverage
  - Path coverage for critical paths

### Coverage Configuration (`pyproject.toml`)

```toml
[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "*/tests/*", "src/**/gui/*"]

[tool.coverage.report]
fail_under = 85
```

## Edge Case Handling

Systematically identify and document edge cases:

- Identify boundary conditions
- Document each edge case with detailed description, input, and expected response
- Include screenshots of failures when relevant
- Implement defensive programming with input validation
- Clear error messages and detailed logging
- Graceful degradation on failure

## Expected Test Results

- Document expected results for every test
- Create automated test reports with pass/fail rates
- Save logs of successful and failed runs

## Implementation Checklist

- [ ] Tests written before or alongside code (TDD cycle)
- [ ] Every public function has at least one test
- [ ] Both happy path and error cases covered
- [ ] External dependencies mocked
- [ ] Coverage ≥ 85%
- [ ] Edge cases identified and documented
- [ ] Defensive programming with input validation
- [ ] Clear error messages and logging
- [ ] Graceful degradation on failure
- [ ] Automated test reports generated
