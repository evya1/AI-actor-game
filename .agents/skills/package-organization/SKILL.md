---
name: package-organization
description: Organize Python project as a professional package with pyproject.toml, __init__.py exports, relative imports, and proper folder structure. Use when packaging Python code for distribution or reuse.
---

# Project as Package

Organizing code as a package is a fundamental principle of professional software development. Properly organized packages enable code reuse, clear dependency management, simple distribution, easy installation, and built-in testing.

## Package Definition File

Every package must include `pyproject.toml` (preferred) or `setup.py`. The file specifies:
- Name, version, description
- Author, license
- Dependencies with pinned versions

## __init__.py Files

`__init__.py` files must exist in the main package directory and every subdirectory:

- Use them to export public interfaces via `__all__`
- Define `__version__` in the main `__init__.py`

```python
# __init__.py
__version__ = "1.00"

__all__ = ["MyClass", "MyFunction"]
from .module import MyClass, MyFunction
```

## Relative Imports

All imports must use relative paths or package names, never absolute paths. File read/write also searches relative to the package path.

```python
# Correct
from . import constants
from ..sdk import SDK

# Wrong
import sys
sys.path.append("/absolute/path")
```

## Package Checklist

### 1. Package Definition File
- [ ] `pyproject.toml` exists
- [ ] Contains name, version, and dependencies
- [ ] Dependencies specified with versions

### 2. __init__.py File
- [ ] Exists in main package directory
- [ ] Exports public interfaces via `__all__`
- [ ] `__version__` defined

### 3. Folder Structure
- [ ] Source code in dedicated `src/` directory
- [ ] Tests in `tests/`
- [ ] Documentation in `docs/`

### 4. Relative Paths
- [ ] All imports are relative or package-based
- [ ] No absolute paths used
