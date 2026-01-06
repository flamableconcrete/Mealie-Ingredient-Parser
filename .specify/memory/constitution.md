# Mealie Ingredient Parser Constitution

<!--
Sync Impact Report:
Version Change: 1.0.0 → 1.1.0
Modified Principles:
  - Testing Requirements: Changed from "encouraged but NOT mandatory" → "REQUIRED for all features"
Added Sections: None
Removed Sections: None
Templates Requiring Updates:
  ✅ spec-template.md - Verified compatible (no updates needed)
  ✅ plan-template.md - Verified compatible (no updates needed)
  ✅ tasks-template.md - Updated to mark tests as REQUIRED (previously OPTIONAL)
Follow-up TODOs: None
-->

## Core Principles

### I. TUI-First User Experience

Every feature MUST provide clear, responsive feedback in the Terminal User Interface. The application MUST display progress indicators for long-running operations, provide actionable error messages, and maintain session state to allow resuming interrupted workflows. Interactive elements MUST be intuitive and guide users through complex processes (pattern grouping, batch processing, alias creation).

**Rationale**: As a TUI application for processing potentially hundreds of ingredients, users need visibility into progress and the ability to resume sessions. Poor UX leads to confusion and lost work.

### II. Resilient API Integration

All Mealie API interactions MUST use retry logic with exponential backoff for transient errors. API errors MUST be classified as either `TransientAPIError` (retryable) or `PermanentAPIError` (immediate failure). Batch operations MUST continue processing remaining items when individual items fail. The application MUST maintain a persistent aiohttp session throughout its lifecycle.

**Rationale**: External API calls are inherently unreliable. The app must gracefully handle network issues, rate limits, and temporary server problems without losing user progress.

### III. Code Quality Standards (NON-NEGOTIABLE)

All Python code MUST be formatted with `uv run ruff format` before commit. Code MUST pass `uv run ruff check` linting. Maximum line length is 120 characters. NumPy-style docstrings are required for public functions. Type hints are encouraged but not strictly enforced. Maximum cyclomatic complexity is 10 per function.

**Rationale**: Consistent code quality ensures maintainability, especially for a project "vibe-coded by Claude Code." Automated tooling prevents style drift.

### IV. Pattern-Based Efficiency

The application MUST group similar unparsed ingredients into patterns during startup to minimize API calls and enable batch processing. Pattern analysis happens once per session. Users MUST be able to apply actions (create unit/food, add alias) to all ingredients matching a pattern in a single operation.

**Rationale**: Processing ingredients one-by-one is inefficient when many ingredients share the same missing unit or food. Pattern-based grouping is a core architectural principle.

### V. Session Persistence & State Management

The application MUST persist session state (processed patterns, created units/foods, skipped items) to allow resuming interrupted sessions. State MUST be saved after significant operations. Users MUST be prompted to resume previous sessions on startup. Session state MUST include enough context to recover from crashes or user exits.

**Rationale**: Processing hundreds of ingredients can take significant time. Users must be able to stop and resume without losing progress.

## Development Standards

### Testing Requirements (NON-NEGOTIABLE)

All features MUST include appropriate tests before being considered complete. Test coverage requirements:

- **Unit tests** in `tests/unit/` for isolated logic (pattern analysis, data models, utilities)
- **Integration tests** in `tests/integration/` for API interactions, screen workflows, and end-to-end user journeys
- Tests MUST be written BEFORE implementation (Test-Driven Development encouraged)
- All tests MUST pass before merging code
- Run tests with `uv run pytest`
- Use `pytest-asyncio` for async test support

**Rationale**: Testing is critical for a TUI application with complex state management, API interactions, and session persistence. Untested code leads to regressions and user data loss.

### Logging & Observability

Structured logging via Loguru is REQUIRED for:

- API calls (request/response, retries, errors)
- Session state changes (save/load/clear)
- Pattern analysis results
- Batch operation outcomes

Logs MUST be saved to `logs/mealie_parser_YYYYMMDD.log` with daily rotation.

### Dependency Management

- Add dependencies: `uv add <package>`
- Development dependencies: `uv add --dev <package>`
- Python 3.13+ REQUIRED
- Minimize external dependencies - prefer standard library when reasonable

## Architecture Constraints

### Screen-Based Navigation

The application follows Textual's screen-based architecture:

1. `LoadingScreen` → fetch data, analyze patterns
2. `ModeSelectionScreen` → user chooses batch or sequential mode
3. Pattern/batch screens → interactive ingredient processing

Screens communicate through shared app state and method calls. Avoid tight coupling between screens.

### Error Handling Hierarchy

Custom exceptions MUST follow this hierarchy:

- `TransientAPIError` → triggers retry with backoff
- `PermanentAPIError` → immediate failure, no retry
- Use `BatchOperationResult` class to track batch success/partial failure

### Configuration Management

Environment variables loaded from `.env`:

- `MEALIE_API_KEY`: Required - API authentication
- `MEALIE_URL`: Required - base URL ending with `/api`
- `BATCH_SIZE`: Optional - parallel processing limit (default: 10)
- `COLUMN_WIDTH_*`: Optional - TUI column width customization

Configuration MUST be validated at startup with clear error messages for missing required values.

## Governance

### Amendment Process

Constitution amendments require:

1. Documented rationale for the change
2. Version bump following semantic versioning:
   - MAJOR: Breaking governance changes, principle removals
   - MINOR: New principles or sections added
   - PATCH: Clarifications, typo fixes, non-semantic refinements
3. Update Sync Impact Report (HTML comment at top of file)
4. Verify dependent templates align with changes

### Compliance & Review

All code changes MUST align with constitution principles. Violations require explicit justification in:

- Pull request descriptions
- Code comments explaining necessity
- Complexity Tracking section in `plan.md` for feature planning

### Version Control

**Version**: 1.1.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-05
