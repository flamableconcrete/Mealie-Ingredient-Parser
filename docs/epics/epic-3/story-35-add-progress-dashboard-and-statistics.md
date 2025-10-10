# Story 3.5: Add Progress Dashboard and Statistics

**As a** user,
**I want** to see high-level statistics about my parsing progress,
**so that** I can understand how much work remains and track my efficiency.

## Acceptance Criteria

1. Status bar across all screens displays: Total Ingredients Parsed, Remaining Unparsed, Units Created, Foods Created, Aliases Added
2. Statistics update in real-time as batch operations complete
3. PatternGroupScreen shows additional stats: Pending Patterns, Completed Patterns, Skipped Patterns
4. RecipeListScreen shows: Total Recipes, Fully Parsed, Partially Parsed, Unparsed
5. Pressing 'i' (info) on PatternGroupScreen displays detailed modal: breakdown by operation type, average time per operation, estimated time remaining
6. Stats calculations use data from Epic 1's pattern analysis and track changes through Epic 2's workflows

---
