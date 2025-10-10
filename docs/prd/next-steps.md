# Next Steps

## UX Expert Prompt

Review the User Interface Design Goals section and create detailed screen mockups for:
- Pattern Group Screen (table layout, keyboard shortcuts, status indicators)
- Batch Preview Screen (confirmation dialog with affected ingredients table)
- Mode toggle transitions between batch and sequential workflows

Focus on clear visual distinction between single-item and batch operations to prevent accidental mass changes. Ensure all interactions are keyboard-accessible with single-key shortcuts.

## Architect Prompt

Review this PRD and the existing codebase ([CLAUDE.md](../CLAUDE.md) provides architecture overview) to design the batch processing enhancement.

**Key Architectural Decisions Required:**
1. **Pattern matching algorithm** (Story 1.2): Evaluate fuzzy matching libraries (fuzzywuzzy, python-Levenshtein, NLTK) for performance and accuracy
2. **Data models** (Story 1.3): Design PatternGroup and BatchOperation class hierarchy with serialization support
3. **State management** (Story 3.4): Define JSON schema for progress persistence and screen state synchronization
4. **Async API strategy** (Story 1.4): Determine batch update approach (sequential with progress vs. concurrent with asyncio.gather)

**Architecture Deliverables:**
- Class diagrams for batch operation models
- Screen navigation flow (RecipeListScreen ↔ PatternGroupScreen ↔ BatchPreviewScreen)
- Error handling architecture (validation points, error propagation)
- State management patterns (screen ownership, data flow)

**Constraints:**
- Must maintain backward compatibility with existing API layer ([mealie_parser/api.py](../mealie_parser/api.py))
- Must follow existing Textual screen patterns ([mealie_parser/screens/](../mealie_parser/screens/))
- Must reuse existing modals (CreateUnitModal, CreateFoodModal, SelectFoodModal)

Reference the existing architecture in [CLAUDE.md](../CLAUDE.md) and existing codebase structure before designing new components.
