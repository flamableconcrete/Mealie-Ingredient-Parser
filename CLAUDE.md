# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Terminal User Interface (TUI) application built with Textual that helps process unparsed recipe ingredients in Mealie instances. The app identifies recipes with unparsed ingredients, uses Mealie's NLP parser to process them, and provides an interactive interface for creating missing units/foods or adding aliases to existing ones.

## Development Commands

### Running the Application

```bash
uv run python main.py
```

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_pattern_analyzer.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code with ruff
uv run ruff format

# Format a specific file
uv run ruff format mealie_parser/api.py

# Lint code
uv run ruff check

# Auto-fix linting issues
uv run ruff check --fix

# Find dead code
uv run vulture
```

### Dependency Management

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Sync dependencies
uv sync
```

## Architecture Overview

### Application Structure

The application follows a screen-based architecture using Textual:

1. **Entry Point** (`main.py`): Initializes logging and launches the MealieParserApp
2. **Main App** (`mealie_parser/app.py`): Creates persistent aiohttp session and manages screen navigation
3. **Screen Flow**:
   - `LoadingScreen`: Fetches recipes, units, foods, and performs pattern analysis
   - `ModeSelectionScreen`: User chooses between batch mode or sequential mode
   - Pattern/batch screens handle the actual ingredient processing workflow

### Key Components

**API Layer** (`api.py`):

- All Mealie API interactions with retry logic and error handling
- Batch operations for updating multiple ingredients
- Functions are decorated with `@retry_with_backoff` for transient error recovery
- HTTP errors are classified as `TransientAPIError` or `PermanentAPIError`

**Session State** (`models/session_state.py`):

- Persists progress across application restarts
- Tracks processed/skipped patterns, created units/foods
- Managed by `SessionManager` which handles save/load/clear operations

**Pattern Analysis** (`services/pattern_analyzer.py`):

- Groups similar unparsed ingredients into patterns
- Extracts unit and food patterns from ingredient text
- Used to batch-process similar ingredients together

**Error Handling** (`error_handling.py`):

- Custom exception hierarchy: `TransientAPIError` (retryable) vs `PermanentAPIError`
- `BatchOperationResult` class for tracking batch operation success/failure
- Retry decorator with exponential backoff

**Screens** (`screens/`):

- Each screen represents a different view in the TUI workflow
- Screens communicate through app state and method calls
- Pattern-based screens allow bulk processing of similar ingredients

**Modals** (`modals/`):

- Reusable dialog components for user interaction
- Handle creation of units/foods, alias management, session resumption

### Data Flow

1. LoadingScreen fetches all recipes, units, and foods from Mealie API
2. Pattern analyzer groups unparsed ingredients by similarity
3. User selects mode (batch or sequential)
4. For each pattern group:
   - User creates missing unit/food or adds aliases
   - System updates all matching ingredients via batch API calls
5. Session state persists progress to allow resuming later

### Configuration

Environment variables are loaded from `.env`:

- `MEALIE_API_KEY`: Authentication token for Mealie API
- `MEALIE_URL`: Base URL for Mealie API (e.g., <https://mealie.example.com/api>)
- `BATCH_SIZE`: Number of items to process in parallel (default: 10)

## Code Style

- Python 3.13+ required
- Uses ruff for linting and formatting with 120 character line length
- NumPy-style docstrings
- Type hints encouraged but not strictly enforced
- Async/await for all API calls
- Loguru for structured logging (logs saved to `logs/mealie_parser_YYYYMMDD.log`)

## Important Notes

- Always run `uv run ruff format` on Python files after editing (per user's global CLAUDE.md)
- The app maintains a persistent aiohttp session throughout its lifecycle
- Pattern analysis happens once at startup to minimize API calls
- Batch operations continue processing even if individual items fail
- Session state allows resuming interrupted batch operations
