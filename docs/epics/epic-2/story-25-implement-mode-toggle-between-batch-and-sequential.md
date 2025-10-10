# Story 2.5: Implement Mode Toggle Between Batch and Sequential

**As a** user,
**I want** to switch between batch mode and sequential mode without losing progress,
**so that** I can use the best workflow for different situations.

## Acceptance Criteria

1. From RecipeListScreen, pressing 'b' enters batch mode (PatternGroupScreen)
2. From PatternGroupScreen, pressing 'q' returns to RecipeListScreen with all progress preserved
3. From PatternGroupScreen action modal, "Review Individual" option enters sequential mode for selected pattern: shows IngredientReviewScreen for first ingredient in pattern group
4. Sequential mode processes ingredients normally; after completing all ingredients in pattern, returns to PatternGroupScreen with pattern marked completed
5. Mode transitions preserve all state: processed recipes, created units/foods, skipped patterns
6. Help footer displays available mode toggle shortcuts on relevant screens

---
