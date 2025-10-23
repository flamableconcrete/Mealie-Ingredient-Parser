# Coding Standards

## Python Version & Dependencies

- **Python Version**: >= 3.13
- **Dependency Management**: `uv` for dependency management and virtual environments
- **Package Manager**: Use `uv sync` to install dependencies, `uv run` to execute scripts

## Code Style & Formatting

### General Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use descriptive variable and function names (snake_case for functions/variables, PascalCase for classes)
- Maximum line length: 88 characters (Black default)
- Use double quotes `"` for strings consistently
- One import per line, grouped by: standard library, third-party, local imports

### Docstrings

- **Format**: Use **NumPy docstring format** for all docstrings
- Use triple double-quotes `"""` for all docstrings
- Module-level docstrings: Brief description of module purpose
- Function/method docstrings: Include sections for Parameters, Returns, Raises (if applicable), and Examples (if helpful)
- Class docstrings: Describe the class purpose, key attributes, and methods

**Module-level Example:**
```python
"""API functions for interacting with Mealie.

This module provides async functions for all Mealie REST API interactions,
including recipe fetching, ingredient parsing, and CRUD operations for
units, foods, and aliases.
"""
```

**Function Example (NumPy Style):**
```python
async def get_all_recipes(session):
    """Fetch all recipes from Mealie with pagination.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls.

    Returns
    -------
    list[dict]
        List of all recipe objects from the Mealie API.

    Raises
    ------
    aiohttp.ClientError
        If the API request fails or returns an error status.

    Examples
    --------
    >>> recipes = await get_all_recipes(session)
    >>> print(f"Found {len(recipes)} recipes")
    """
    ...
```

**Class Example (NumPy Style):**
```python
class MealieParserApp(App):
    """Main Textual app for Mealie ingredient parsing.

    This application manages a persistent aiohttp session and coordinates
    the screen flow for loading recipes, selecting unparsed recipes, and
    reviewing/parsing ingredients.

    Attributes
    ----------
    session : aiohttp.ClientSession or None
        Persistent HTTP session created on mount, closed on unmount.

    Methods
    -------
    on_mount()
        Initialize the aiohttp session and push the loading screen.
    on_unmount()
        Clean up the aiohttp session when the app exits.
    """
    ...
```

### Type Hints

- Use type hints for function parameters and return values where beneficial
- For async functions, use `async def` and appropriate return type hints
- For complex types, import from `typing` module

**Example:**
```python
from typing import List, Dict, Any

async def get_recipe_details(session: aiohttp.ClientSession, slug: str) -> Dict[str, Any]:
    """Fetch detailed information for a specific recipe."""
    ...
```

## Project Structure

### Module Organization

```
mealie_parser/
├── __init__.py           # Package initialization
├── app.py                # Main Textual application class
├── config.py             # Configuration and environment variables
├── api.py                # All API interactions with Mealie
├── utils.py              # Utility functions
├── logging_config.py     # Logging configuration
├── models/               # Data models
│   └── pattern.py
├── services/             # Business logic services
│   └── pattern_analyzer.py
├── screens/              # Textual screen components
│   ├── __init__.py
│   ├── loading.py
│   ├── mode_selection.py
│   ├── recipe_list.py
│   ├── ingredient_review.py
│   └── batch_units.py
└── modals/               # Modal dialog components
    ├── __init__.py
    ├── unit_modals.py
    └── food_modals.py
```

### File Naming

- Use `snake_case` for all Python file names
- Group related functionality in modules/packages
- Use `__init__.py` to expose public interfaces

## Async/Await Patterns

### Session Management

- Create a **single persistent** `aiohttp.ClientSession` in `MealieParserApp.on_mount()`
- Pass the session to all screens and API functions
- Close the session in `MealieParserApp.on_unmount()`
- Never create sessions inside API functions

**Example:**
```python
# ✅ CORRECT: Pass session as parameter
async def get_all_recipes(session):
    async with session.get(f"{API_URL}/recipes") as r:
        ...

# ❌ WRONG: Don't create sessions in functions
async def get_all_recipes():
    async with aiohttp.ClientSession() as session:  # Don't do this!
        ...
```

### API Call Patterns

- All API interactions go in `mealie_parser/api.py`
- Use `async with` for all HTTP requests
- Always call `r.raise_for_status()` after requests
- Handle errors with try/except blocks and proper logging

**Example:**
```python
async def get_recipe_details(session, slug):
    """Fetch detailed information for a specific recipe."""
    try:
        async with session.get(f"{API_URL}/recipes/{slug}") as r:
            r.raise_for_status()
            result = await r.json()
            logger.debug(f"Fetched details for recipe: {slug}")
            return result
    except Exception as e:
        logger.error(f"Error fetching recipe details for '{slug}': {e}", exc_info=True)
        raise
```

## Logging

### Logging Configuration

- Initialize logging using `mealie_parser.logging_config.setup_logging()`
- Use appropriate log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Include context in log messages (e.g., recipe slug, page number, item counts)

### Logger Usage

- Get logger at module level: `logger = logging.getLogger(__name__)`
- Log at appropriate levels:
  - `DEBUG`: Detailed diagnostic information
  - `INFO`: General informational messages (startup, shutdown, major events)
  - `WARNING`: Warning messages for unexpected but handled situations
  - `ERROR`: Error messages with `exc_info=True` for stack traces
  - `CRITICAL`: Critical errors that prevent app from continuing

**Example:**
```python
import logging

logger = logging.getLogger(__name__)

try:
    logger.info(f"Successfully fetched {len(recipes)} recipes")
    logger.debug(f"Fetched page {page} of recipes ({len(data['items'])} items)")
except Exception as e:
    logger.error(f"Error fetching recipes at page {page}: {e}", exc_info=True)
    raise
```

## Textual UI Components

### Screen Organization

- Each screen is a separate file in `mealie_parser/screens/`
- Screens should be self-contained and focused on a single responsibility
- Use `push_screen()` for navigation, `push_screen_wait()` for modal dialogs
- Clean up resources in screen lifecycle methods

### Modal Dialogs

- Modal components go in `mealie_parser/modals/`
- Group related modals by domain (e.g., `unit_modals.py`, `food_modals.py`)
- Use descriptive class names (e.g., `UnitActionModal`, `CreateFoodModal`)

### CSS Styling

- Define CSS inline in the component class using the `CSS` class variable
- Use Textual's design tokens for consistency (e.g., `$surface`, `$primary`)

## Error Handling

### API Errors

- Always use try/except blocks for API calls
- Call `raise_for_status()` on all HTTP responses
- Log errors with `exc_info=True` for full stack traces
- Re-raise exceptions after logging to allow upstream handling

### User-Facing Errors

- Catch exceptions at the UI layer and display user-friendly messages
- Don't expose technical details to users in error messages
- Log full technical details for debugging

## Configuration & Environment

### Environment Variables

- Store configuration in `.env` file (not committed to git)
- Load using `python-dotenv`
- Access via `mealie_parser/config.py` module
- Required variables:
  - `MEALIE_API_KEY`: Bearer token for authentication
  - `MEALIE_URL`: Base URL for Mealie API

**Example:**
```python
# config.py
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("MEALIE_API_KEY")
API_URL = os.getenv("MEALIE_URL", "").rstrip("/")
headers = {"Authorization": f"Bearer {API_KEY}"}
```

## Testing

### Test Organization

```
tests/
├── __init__.py
└── unit/
    ├── __init__.py
    ├── test_pattern_model.py
    └── test_pattern_analyzer.py
```

### Test Naming

- Test files: `test_<module_name>.py`
- Test functions: `test_<functionality>()`
- Use descriptive test names that explain what is being tested

### Test Dependencies

- Use appropriate testing frameworks (e.g., pytest)
- Mock external dependencies (API calls, sessions)
- Test edge cases and error conditions

## Git Practices

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in present tense (e.g., "Add", "Fix", "Update", "Refactor")
- Keep first line under 72 characters
- Add details in body if needed

**Example:**
```
Add BMAD method documentation

- Include coding standards document
- Document async/await patterns
- Add logging guidelines
```

### Branch Management

- Main branch: `main`
- Create feature branches for new work
- Keep commits focused and atomic

## Dependencies

### Core Dependencies

- **aiohttp**: HTTP client for async API calls
- **python-dotenv**: Environment variable management
- **textual**: Terminal UI framework
- **rich**: Rich text formatting

### Adding Dependencies

- Add dependencies via `uv add <package>`
- Document new dependencies and their purpose
- Keep dependencies minimal and justified

## Code Review Checklist

Before submitting code for review, ensure:

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have docstrings
- [ ] Async/await patterns are used correctly
- [ ] API calls are in `api.py` and use the shared session
- [ ] Errors are logged with appropriate levels
- [ ] No sensitive data (API keys, passwords) in code
- [ ] Tests are written for new functionality
- [ ] Code is self-documenting with clear variable/function names
- [ ] Imports are organized (stdlib, third-party, local)
- [ ] No unused imports or variables

## Performance Considerations

### API Efficiency

- Batch API calls where possible
- Use pagination for large datasets
- Reuse the single session instance
- Set appropriate connection limits in connector

### UI Responsiveness

- Keep async operations in the background
- Update UI progressively during long operations
- Use Textual's reactive features for efficient updates

## Security

### API Keys

- Never commit API keys to git
- Use environment variables for all secrets
- Include `.env` in `.gitignore`

### Input Validation

- Validate user inputs before processing
- Sanitize data before sending to API
- Handle malformed API responses gracefully

---

## Quick Reference

### Running the App

```bash
# Install dependencies
uv sync

# Run application
python main.py
# or
uv run main.py
```

### Common Patterns

**API Call (NumPy Docstring Format):**
```python
async def fetch_data(session, endpoint):
    """Fetch data from API endpoint.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The persistent HTTP session for API calls.
    endpoint : str
        The API endpoint path (without base URL).

    Returns
    -------
    dict
        JSON response data from the API.

    Raises
    ------
    aiohttp.ClientError
        If the API request fails or returns an error status.
    """
    try:
        async with session.get(f"{API_URL}/{endpoint}") as r:
            r.raise_for_status()
            logger.debug(f"Fetched data from {endpoint}")
            return await r.json()
    except Exception as e:
        logger.error(f"Error fetching {endpoint}: {e}", exc_info=True)
        raise
```

**Screen Navigation:**
```python
# Push a new screen
self.app.push_screen(NextScreen())

# Push a modal and wait for result
result = await self.app.push_screen_wait(MyModal())
```

**Logging:**
```python
logger.info("Application started")
logger.debug(f"Processing recipe: {recipe_slug}")
logger.error(f"Failed to process: {e}", exc_info=True)
```
