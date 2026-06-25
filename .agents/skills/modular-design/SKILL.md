---
name: modular-design
description: Design modular building blocks with well-defined interfaces, single responsibility, input/output validation, and testability. Use when designing new components or refactoring existing code.
---

# Modular Design & Building Blocks

Building blocks design is a modular approach where each component is an independent unit with a well-defined interface.

## Building Block Structure

Every building block is defined by:

### Input Data
- Data types, valid ranges
- External dependencies
- Comprehensive validation

### Output Data
- Data types, format
- Behavior in edge cases

### Setup Data
- Parameters with defaults
- Configuration
- Initialization

## Design Principles

- **Single Responsibility** — Each block is responsible for one task
- **Separation of Concerns** — Each block deals with one domain
- **Reusability** — Independent building blocks not dependent on specific code
- **Testability** — Every block testable in isolation

## Building Block Example

```python
class DataProcessor:
    """
    Input: raw_data (List[Dict]),
           filter_criteria (Dict)
    Output: processed_data (List[Dict])
    Setup: processing_mode ('fast'/'accurate'),
           batch_size (int, default: 100)
    """
    def __init__(self, processing_mode='fast', batch_size=100):
        self.processing_mode = processing_mode
        self.batch_size = batch_size
        self._validate_config()

    def process(self, raw_data, filter_criteria):
        self._validate_input(raw_data, filter_criteria)
        return self._do_processing(raw_data, filter_criteria)

    def _validate_config(self):
        if self.processing_mode not in ['fast', 'accurate']:
            raise ValueError("Invalid mode")
        if self.batch_size < 0:
            raise ValueError("Batch size must be > 0")

    def _validate_input(self, data, criteria):
        if not isinstance(data, list):
            raise TypeError("data must be list")
        if not isinstance(criteria, dict):
            raise TypeError("criteria must be dict")
```

## Implementation Checklist

- [ ] Each component has well-defined input, output, and setup
- [ ] Single responsibility per component
- [ ] Separation of concerns enforced
- [ ] Components are reusable and independent
- [ ] Each component is independently testable
- [ ] Input validation implemented
- [ ] Clear docstrings documenting I/O contract
