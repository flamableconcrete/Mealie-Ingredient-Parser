# Developer Standards

## Critical Coding Rules

1. **Always use type hints** - All functions, methods, and variables must have type annotations
2. **Reactive state updates** - Use reactive attributes for UI state, never manual updates
3. **Async/await required** - All API calls and I/O must be async
4. **Error handling mandatory** - All API calls must handle ClientError exceptions
5. **Test business logic** - All services and models must have unit tests
6. **CSS for styling** - No inline styles, use Textual CSS files
7. **Keyboard-first** - All UI interactions must work via keyboard
8. **Session persistence** - Use existing aiohttp session, never create new ones
9. **State serialization** - SessionState must be JSON-serializable
10. **Logging not print** - Use Python logging, never print statements

## Quick Reference

**Common Commands:**
```bash
# Development server
python main.py
uv run main.py

# Run tests
pytest
pytest tests/unit/
pytest -v --cov

# Type checking
mypy mealie_parser/

# Linting
ruff check --fix mealie_parser/
```

**Key Import Patterns:**
```python
from __future__ import annotations
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header

if TYPE_CHECKING:
    from mealie_parser.models.pattern import PatternGroup
```

**File Naming:**
- Screens: `pattern_group.py` → `PatternGroupScreen`
- Modals: `pattern_action.py` → `PatternActionModal`
- Services: `pattern_analyzer.py` → `PatternAnalyzer`
- Models: `pattern.py` → `PatternGroup`

**Project-Specific Patterns:**
- Use `app.session` for all API calls
- Mark patterns completed with `session_state.completed_pattern_ids.add()`
- Persist state with `StateManager.save_state()`
- Refresh caches after alias creation: `get_foods_full()`

---
