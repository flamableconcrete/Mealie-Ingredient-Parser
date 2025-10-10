# Story 2.2: Implement Batch Unit Creation Workflow

**As a** user,
**I want** to create a unit once and apply it to all matching ingredients,
**so that** I don't have to repeatedly create the same unit across dozens of recipes.

## Acceptance Criteria

1. From PatternGroupScreen, selecting a unit pattern and pressing Enter opens action modal with options: Create New Unit, Skip Pattern
2. "Create New Unit" option opens existing `CreateUnitModal` (reuse from sequential workflow)
3. After unit creation, system displays `BatchPreviewScreen` showing table of all affected ingredients (recipe name, ingredient text, current status)
4. BatchPreviewScreen offers: Confirm (apply to all), Cancel (abort operation), Review Individual (fall back to sequential mode for this pattern)
5. Upon confirmation, system calls `update_ingredient_unit_batch()` from Epic 1, displays progress indicator during API calls
6. After completion, PatternGroupScreen updates pattern status to "Completed" and shows success message with count
