# Story 2.3: Implement Batch Food Creation and Alias Workflows

**As a** user,
**I want** to create a food once or add an alias to existing food and apply it to all matching ingredients,
**so that** I efficiently handle food patterns without repetition.

## Acceptance Criteria

1. From PatternGroupScreen, selecting a food pattern and pressing Enter opens action modal with options: Create New Food, Add Alias to Existing Food, Skip Pattern
2. "Create New Food" opens existing `CreateFoodModal`, then shows `BatchPreviewScreen` for confirmation, then executes batch food update
3. "Add Alias to Existing Food" opens existing `SelectFoodModal` (searchable table of foods), then shows `BatchPreviewScreen`, then creates alias via API and executes batch food update
4. Both workflows follow same preview-confirm-execute pattern as Story 2.2
5. BatchPreviewScreen clearly indicates whether operation is "creating new food" or "adding alias to [Food Name]"
6. After completion, system refreshes food cache (call `get_foods_full()`) before processing next pattern to ensure alias is available
