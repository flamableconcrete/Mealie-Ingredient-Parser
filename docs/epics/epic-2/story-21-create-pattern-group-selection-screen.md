# Story 2.1: Create Pattern Group Selection Screen

**As a** user with many unparsed ingredients,
**I want** a screen showing grouped patterns with counts and action options,
**so that** I can identify high-value batch operations to tackle first.

## Acceptance Criteria

1. New `PatternGroupScreen` displays table with columns: Pattern Text, Type (Unit/Food), Count, Status (Pending/Completed/Skipped)
2. Table shows both unit patterns and food patterns in separate sections or with clear visual distinction
3. Keyboard navigation: arrow keys to select pattern, Enter to open action menu, 's' to skip, 'q' to return to recipe list
4. Screen loads pattern data from Epic 1's analysis performed during LoadingScreen
5. Status bar shows total patterns, processed count, and skipped count
6. Screen integrates into existing app flow: accessible from RecipeListScreen via keyboard shortcut ('b' for batch mode)
