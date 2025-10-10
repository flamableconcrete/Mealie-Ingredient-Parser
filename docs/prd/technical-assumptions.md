# Technical Assumptions

## Repository Structure

**Monorepo** - Single repository containing all application code, configuration, and documentation.

## Service Architecture

**Monolith** - Single-process Python TUI application. The existing architecture uses:
- Textual framework for TUI rendering and event handling
- aiohttp for async HTTP client operations against Mealie API
- Single persistent session created at app startup and shared across screens
- No backend services required—application acts as a client to existing Mealie instance

**Rationale:** Enhancing existing TUI rather than building new services. Monolithic architecture fits the use case: terminal application with no concurrent users, no scalability requirements beyond single-user session performance.

## Testing Requirements

**Unit + Integration Testing** - The application should include:
- **Unit tests** for core logic: pattern matching algorithms, ingredient grouping, batch operation validation
- **Integration tests** for API layer: mocked Mealie API responses to validate request/response handling
- **Manual testing** as primary validation method for TUI workflows (Textual UI testing is complex; human review more practical for UX validation)

**Rationale:** Unit tests prevent regression in batch logic. Integration tests validate API contract compliance. Full E2E automation of TUI flows has poor ROI given Textual framework limitations and manual testing efficiency for UI workflows.

## Additional Technical Assumptions and Requests

- **Python >=3.13** - Continue using current Python version requirement (existing constraint in pyproject.toml)
- **uv for dependency management** - Maintain existing tooling for consistency
- **Textual >=6.2.1** - Leverage latest Textual features; existing codebase already on 6.x
- **aiohttp >=3.13.0** - Continue using async HTTP client; session persistence pattern already established
- **python-dotenv** - Maintain .env configuration pattern for MEALIE_API_KEY and MEALIE_URL
- **No database layer** - Application remains stateless; all data stored in Mealie instance via API
- **Environment variable configuration only** - No config files, CLI args, or interactive setup; simplifies deployment
- **Backward compatibility with existing API layer** - New batch operations must use existing `api.py` functions; refactor for efficiency if needed but maintain function signatures where possible
- **Screen-based architecture** - New batch screens follow existing Textual screen patterns (LoadingScreen → RecipeListScreen → etc.)
- **Modal-based sub-workflows** - Batch preview/confirmation uses Textual modals consistent with current CreateUnitModal, CreateFoodModal patterns
- **Deployment** - Standard Python package installation (uv sync) with .env configuration; no additional infrastructure required beyond existing Mealie instance

---
