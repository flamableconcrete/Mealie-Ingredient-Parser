# Tech Stack

## Technology Stack Table

| Category | Technology | Version | Purpose | Rationale |
|----------|-----------|---------|---------|-----------|
| Framework | Textual | >=6.2.1 | Terminal UI framework with reactive widgets and CSS styling | Modern TUI framework with component-based architecture, async support, and rich widget library. Enables complex terminal UIs with minimal code. |
| Language | Python | >=3.13 | Application runtime and business logic | Latest Python version with performance improvements and modern type hints. Required for Textual 6.x compatibility. |
| Async Runtime | asyncio | stdlib (3.13+) | Event loop and async coordination | Native Python async support. Powers Textual's reactive model and coordinates with aiohttp for API calls. |
| HTTP Client | aiohttp | >=3.13.0 | Async HTTP requests to Mealie API | Production-ready async HTTP client with session pooling, connection reuse, and timeout handling. Already integrated in existing codebase. |
| Configuration | python-dotenv | latest | Environment variable loading from .env files | Simple, secure configuration management. Keeps API keys out of code and supports multiple environments. |
| Dependency Mgmt | uv | latest | Fast Python package installer and resolver | Modern pip replacement with speed and reliability improvements. Already established in project. |
| Styling | Textual CSS | built-in | Component styling and theming | CSS-like syntax for terminal styling. Supports variables, selectors, and responsive rules. Maintains separation of concerns. |
| State Management | Reactive attributes | built-in (Textual) | Screen and widget state reactivity | Textual's reactive system automatically updates UI when state changes. No external state library needed for TUI scale. |
| Routing/Navigation | Screen stack | built-in (Textual) | Screen transitions and modal overlays | Textual's push_screen/pop_screen pattern manages navigation stack. Supports both full screens and modal overlays. |
| Component Library | Textual Widgets | built-in | DataTable, Modal, Button, Input, Label, etc. | Rich set of pre-built terminal widgets. Handles keyboard navigation, focus management, and accessibility. |
| Form Handling | Textual Input/Validation | built-in | User input in modals (CreateUnitModal, etc.) | Built-in Input widget with validation hooks. Sufficient for simple form workflows without external library. |
| Animation | Textual CSS Transitions | built-in | State transitions, progress indicators, spinners | CSS-like transitions for smooth visual feedback. Limited compared to web but adequate for terminal constraints. |
| Testing | pytest + pytest-asyncio | latest | Unit and integration testing | Standard Python testing stack. pytest-asyncio supports testing async Textual components. |
| Type Checking | mypy | latest | Static type analysis | Enforces type safety. Critical for large codebases with async code and complex data models. |
| Linting | ruff | latest | Fast Python linter and formatter | Modern linter replacing flake8/black. Catches common errors and enforces code style consistency. |
| Logging | Python logging | stdlib | Operation logging and debugging | Standard library logging with file handlers. Sufficient for single-user TUI application. |

## Rationale

This tech stack prioritizes **minimal external dependencies** while leveraging Textual's rich built-in capabilities.

**Trade-offs:**
- **No external state management library:** Textual's reactive system (similar to React hooks) handles TUI-scale state efficiently. For batch operations tracking, simple Python data classes + reactive attributes suffice.
- **No dedicated animation library:** Terminal animation capabilities are inherently limited by refresh rates and character-cell constraints. Textual's CSS transitions + programmatic widget updates provide adequate feedback.
- **No form validation library:** The form complexity is low (2-3 fields per modal). Textual's Input widget + custom validation functions are sufficient.

**Key Decisions:**
- **uv over pip:** Already established in project. Offers 10-100x faster dependency resolution.
- **No ORM/database layer:** Application is stateless - all persistence via Mealie API. State recovery uses simple JSON serialization.
- **pytest-asyncio:** Required for testing Textual's async event loop.

---
