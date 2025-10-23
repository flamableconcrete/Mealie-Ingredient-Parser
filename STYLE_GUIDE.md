# Python Style Guide for Mealie Ingredient Parser

This document defines the coding standards and best practices for this project. All code should adhere to these guidelines to ensure consistency, maintainability, and quality.

## Core Principles

1. **Follow PEP 8**: Python's official style guide forms the foundation of our coding standards
2. **Readability Counts**: Code is read more often than it is written
3. **Explicit is Better Than Implicit**: Clear, unambiguous code is preferred
4. **Consistency is Key**: Follow the existing patterns in the codebase

## Code Formatting

### Tool Configuration

This project uses **ruff** as the primary linter and formatter. Ruff is a fast, modern Python linter written in Rust that replaces multiple tools (black, isort, flake8, etc.).

### Automatic Formatting

All Python files should be formatted with ruff before committing:

```bash
# Format a single file
uv run ruff format file.py

# Format entire project
uv run ruff format .

# Check without making changes
uv run ruff check .
```

### Line Length

- **Maximum line length**: 120 characters
- **Rationale**: Provides sufficient space for modern code patterns while maintaining readability

### Imports

Imports are automatically organized by ruff with the following structure:

1. Standard library imports
2. Third-party imports
3. Local application imports

Each group is separated by a blank line and sorted alphabetically.

**Example:**
```python
# Standard library
import asyncio
from pathlib import Path

# Third-party
import aiohttp
from loguru import logger
from textual.app import App

# Local
from mealie_parser.api import get_recipes
from mealie_parser.models.pattern import Pattern
```

### Indentation

- Use **4 spaces** per indentation level
- Never mix tabs and spaces
- Continuation lines should align wrapped elements or use hanging indent

### Quotes

- Prefer **double quotes** (`"`) for strings
- Use single quotes (`'`) only when the string contains double quotes
- Triple-quoted strings use double quotes: `"""`

### Whitespace

- No trailing whitespace
- Blank line at end of file
- Two blank lines between top-level functions and classes
- One blank line between methods in a class
- No spaces around `=` in keyword arguments or default parameter values
- One space around operators: `x = y + 1`

## Naming Conventions

### General Rules

| Type | Convention | Example |
|------|------------|---------|
| Module | `snake_case` | `pattern_analyzer.py` |
| Class | `PascalCase` | `PatternAnalyzer` |
| Function | `snake_case` | `parse_ingredient()` |
| Method | `snake_case` | `get_recipe_data()` |
| Variable | `snake_case` | `recipe_count` |
| Constant | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private | `_leading_underscore` | `_internal_method()` |

### Specific Guidelines

**Functions and Methods:**
- Use verbs that describe the action: `get_recipes()`, `parse_ingredient()`, `validate_unit()`
- Boolean-returning functions should be prefixed with `is_`, `has_`, or `should_`: `is_recipe_unparsed()`, `has_ingredients()`

**Classes:**
- Use nouns that represent the concept: `RecipeListScreen`, `PatternAnalyzer`, `UnitActionModal`
- Avoid redundant suffixes like `Manager` or `Helper` unless they add clarity

**Variables:**
- Use descriptive names, avoid abbreviations unless universally understood
- Prefer `recipe_count` over `rc`, but `url` and `api` are acceptable
- Use plural names for collections: `recipes`, `units`, `ingredients`

**Constants:**
- Define at module level
- Use for configuration values, magic numbers, and fixed strings

## Type Hints

### General Usage

- **All function signatures** should include type hints for parameters and return values
- **Public APIs** must be fully typed
- Use `typing` module types for complex types

**Example:**
```python
from typing import Optional
from aiohttp import ClientSession

async def get_recipe(
    session: ClientSession,
    recipe_id: str,
    timeout: int = 30
) -> dict[str, Any]:
    """Fetch a recipe by ID from the API."""
    ...
```

### Type Hint Best Practices

- Use `list[T]`, `dict[K, V]`, `set[T]` instead of `List[T]`, `Dict[K, V]`, `Set[T]` (Python 3.9+ style)
- Use `Optional[T]` for values that can be `None`
- Use `Any` sparingly - try to be specific
- For complex types, consider using `TypedDict` or dataclasses
- Use `Callable` for function types
- Use `Protocol` for structural subtyping when appropriate

## Documentation

### Docstrings

All public modules, classes, and functions require docstrings. Use **NumPy-style docstrings**.

**Module Docstring:**
```python
"""Pattern analysis utilities for ingredient parsing.

This module provides functions to analyze ingredient parsing patterns
and identify recurring structures in unparsed ingredients.
"""
```

**Function Docstring:**
```python
def parse_ingredient(text: str, recipe_id: str) -> ParsedIngredient:
    """Parse an ingredient string into structured components.

    Parameters
    ----------
    text : str
        Raw ingredient text to parse
    recipe_id : str
        ID of the recipe containing this ingredient

    Returns
    -------
    ParsedIngredient
        ParsedIngredient object with extracted components

    Raises
    ------
    ValueError
        If text is empty or invalid
    APIError
        If API call fails
    """
```

**Class Docstring:**
```python
class PatternAnalyzer:
    """Analyzes ingredient patterns to identify common parsing issues.

    This class tracks patterns in unparsed ingredients and provides
    statistics on the most common parsing failures.

    Attributes
    ----------
    pattern_count : int
        Number of unique patterns found
    recipes_analyzed : int
        Total recipes processed
    """
```

**Method Docstring:**
```python
async def fetch_recipes(self, session: ClientSession, page: int = 1) -> list[dict]:
    """Fetch recipes from the API with pagination.

    Parameters
    ----------
    session : ClientSession
        Aiohttp session for making requests
    page : int, optional
        Page number to fetch, by default 1

    Returns
    -------
    list[dict]
        List of recipe dictionaries

    Notes
    -----
    This method automatically handles pagination and retries on transient errors.

    Examples
    --------
    >>> async with aiohttp.ClientSession() as session:
    ...     recipes = await fetch_recipes(session, page=1)
    ...     print(len(recipes))
    50
    """
```

### Comments

- Use comments to explain **why**, not **what**
- Prefer clear code over comments when possible
- Keep comments up-to-date with code changes
- Use `# TODO:` for future work, `# FIXME:` for known issues
- Avoid obvious comments: `x = x + 1  # Increment x` ❌

## Code Organization

### File Structure

```
mealie_parser/
├── __init__.py           # Package initialization
├── app.py                # Main application entry point
├── config.py             # Configuration management
├── constants/            # Constants organized by domain
├── api.py                # API layer (all HTTP calls)
├── models/               # Data models and types
│   ├── __init__.py
│   ├── pattern.py
│   └── session_state.py
├── screens/              # Textual screens
│   ├── __init__.py
│   ├── loading.py
│   └── recipe_list.py
├── modals/               # Modal dialogs
│   └── ...
├── services/             # Business logic layer
│   └── ...
└── utils.py              # Utility functions
```

### Module Organization

Within a module, organize code in this order:

1. Module docstring
2. Imports (standard library → third-party → local)
3. Constants
4. Exception classes
5. Type definitions (TypedDict, Protocol, etc.)
6. Functions
7. Classes

### Class Organization

Within a class, organize code in this order:

1. Class docstring
2. Class variables
3. `__init__` method
4. Special methods (`__str__`, `__repr__`, etc.)
5. Properties
6. Public methods
7. Private methods

## Best Practices

### Async/Await

- Use `async`/`await` for all I/O operations
- Prefer `asyncio.gather()` for concurrent operations
- Always close async resources (use `async with` context managers)
- Pass `ClientSession` as parameter rather than creating in functions

**Example:**
```python
async def fetch_multiple_recipes(
    session: ClientSession,
    recipe_ids: list[str]
) -> list[dict[str, Any]]:
    """Fetch multiple recipes concurrently."""
    tasks = [get_recipe(session, rid) for rid in recipe_ids]
    return await asyncio.gather(*tasks)
```

### Error Handling

- Use specific exception types, not bare `except:`
- Handle exceptions at the appropriate level
- Provide useful error messages
- Log errors with context using loguru

**Example:**
```python
try:
    recipe = await get_recipe(session, recipe_id)
except aiohttp.ClientError as e:
    logger.error(f"Failed to fetch recipe {recipe_id}: {e}")
    raise APIError(f"Recipe fetch failed: {recipe_id}") from e
```

### Textual-Specific Guidelines

- Screen classes should end with `Screen`: `LoadingScreen`, `RecipeListScreen`
- Modal classes should end with `Modal`: `UnitActionModal`, `CreateFoodModal`
- Use `push_screen_wait()` for modal dialogs that return values
- Use `push_screen()` for navigation to main screens
- Prefer reactive attributes for state that affects rendering
- Use `on_mount()` for initialization, not `__init__`

### Data Models

- Use Pydantic models or dataclasses for structured data
- Prefer immutable data structures when possible
- Use TypedDict for API response shapes

### Logging

- Use loguru for all logging
- Log levels:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages
  - `WARNING`: Warning messages for recoverable issues
  - `ERROR`: Error messages for failures
  - `CRITICAL`: Critical failures requiring immediate attention

**Example:**
```python
from loguru import logger

logger.info(f"Processing {len(recipes)} recipes")
logger.warning(f"Skipping invalid recipe: {recipe_id}")
logger.error(f"API request failed", exc_info=e)
```

### Testing

- Write tests for all public functions and methods
- Use pytest for testing
- Use pytest-asyncio for async tests
- Organize tests to mirror source structure
- Name test functions: `test_<function_name>_<scenario>()`

**Example:**
```python
import pytest

async def test_get_recipe_success(mock_session):
    """Test successful recipe fetching."""
    recipe = await get_recipe(mock_session, "test-id")
    assert recipe["id"] == "test-id"

async def test_get_recipe_not_found(mock_session):
    """Test handling of missing recipe."""
    with pytest.raises(APIError):
        await get_recipe(mock_session, "nonexistent")
```

## Anti-Patterns to Avoid

1. **Mutable default arguments**
   ```python
   # ❌ Bad
   def add_ingredient(recipe, ingredients=[]):
       ...

   # ✅ Good
   def add_ingredient(recipe, ingredients=None):
       if ingredients is None:
           ingredients = []
       ...
   ```

2. **Bare except clauses**
   ```python
   # ❌ Bad
   try:
       risky_operation()
   except:
       pass

   # ✅ Good
   try:
       risky_operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}")
   ```

3. **String concatenation in loops**
   ```python
   # ❌ Bad
   result = ""
   for item in items:
       result += str(item)

   # ✅ Good
   result = "".join(str(item) for item in items)
   ```

4. **Not using context managers**
   ```python
   # ❌ Bad
   file = open("data.txt")
   data = file.read()
   file.close()

   # ✅ Good
   with open("data.txt") as file:
       data = file.read()
   ```

## Pre-Commit Checklist

Before committing code, ensure:

- [ ] Code is formatted with `uv run ruff format`
- [ ] Linting passes: `uv run ruff check`
- [ ] All functions have type hints
- [ ] Public APIs have docstrings
- [ ] Tests pass: `uv run pytest`
- [ ] No debugging code (print statements, breakpoints) remains
- [ ] Imports are organized correctly
- [ ] No trailing whitespace

## Tools and Automation

### Ruff Configuration

Ruff is configured in `pyproject.toml` with project-specific rules.

**Disabled Rules:**

The following rules are intentionally disabled:

- **E501** (Line too long): Handled by the formatter
- **B008** (Function calls in argument defaults): Common pattern in FastAPI/Textual
- **PTH123** (Use `Path.open()` instead of `open()`): Standard `open()` is preferred for simplicity
- **SIM102** (Use single if statement): Multiple if statements can be clearer
- **SIM108** (Use ternary operator): Explicit if/else can be more readable

### Running Checks

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Type checking (if using mypy)
uv run mypy mealie_parser/
```

### CI/CD Integration

These checks should be automated in CI/CD pipelines:
- Ruff formatting verification
- Ruff linting
- Type checking
- Test suite execution

## References

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [NumPy Docstring Style Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Textual Documentation](https://textual.textualize.io/)

## Updates and Changes

This style guide is a living document. As the project evolves, these guidelines may be updated. All team members should review changes and provide feedback.

### Changelog

- **v1.1.0** (2025-10-22): Updated to NumPy-style docstrings and 120 character line length
- **v1.0.0** (2025-10-22): Initial style guide with Google-style docstrings and 100 character line length

---

**Last Updated:** 2025-10-22
**Version:** 1.1.0
