---
name: sdk-architecture
description: Design SDK-based architecture with OOP principles. All business logic flows through a single SDK entry point. Use when designing system architecture or refactoring to eliminate code duplication.
---

# SDK Architecture & OOP Design

All business logic must be accessible through an SDK layer. The SDK is the single entry point for all consumers.

## SDK Architecture

```text
External Consumers (GUI / CLI / REST / Third Party)
        |
        v
+-------+-------+
|      SDK      | <-- Single entry point for ALL logic
+-------+-------+
        |
        v
+-------+-------+
|     Domain    | <-- Services, models, orchestrators
|    Services   |
+-------+-------+
        |
        v
+-------+-------+
| Infrastructure | <-- DB, file I/O, external APIs
+-------+-------+
```

## Requirements

- Every important business function must be accessible through the SDK class
- No business logic in CLI, GUI, or controllers — these layers delegate to SDK
- External consumers can import the SDK and execute all operations without accessing internal modules
- All logic flows through the SDK layer

## OOP Design — No Code Duplication

Plan code using OOP principles. Never duplicate code.

### Duplication Rules

| Situation | Action |
|-----------|--------|
| Same function body in 2+ files | Extract to shared module |
| Same try/except pattern in 3+ files | Create wrapper function |
| Identical logic in 3+ classes | Create base class or mixin |
| Logic passed with slight variations | Use Template Method pattern |

### Mixin Rules

- Each mixin provides exactly one concern
- Mixins must not override each other's methods
- Mixins must be independently testable

## Implementation Checklist

1. Create `src/<package>/sdk/sdk.py` as the central SDK class
2. All business functions are methods or delegates of the SDK
3. CLI/GUI layers only handle presentation, delegating to SDK
4. No direct imports of domain services by external consumers
5. Extract shared logic before duplicating
6. Use inheritance or mixins for shared behavior
7. Each class has a single responsibility
8. Each mixin handles one concern
