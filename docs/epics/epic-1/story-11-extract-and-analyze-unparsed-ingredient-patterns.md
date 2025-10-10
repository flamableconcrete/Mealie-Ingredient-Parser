# Story 1.1: Extract and Analyze Unparsed Ingredient Patterns

**As a** system administrator,
**I want** the application to analyze all unparsed ingredients and identify unique unit/food patterns,
**so that** I can understand the scope of batch processing opportunities before building UI.

## Acceptance Criteria

1. System extracts all unparsed ingredients from loaded recipes and identifies those missing `unit.id` or `food.id`
2. System groups ingredients by unparsed unit text (case-insensitive, trimmed whitespace)
3. System groups ingredients by unparsed food text (case-insensitive, trimmed whitespace)
4. Grouping logic creates data structures containing: pattern text, list of affected ingredient IDs, list of affected recipe IDs
5. Pattern analysis runs during existing LoadingScreen data fetch phase without blocking UI
6. Unit tests validate grouping logic with edge cases: empty strings, special characters, Unicode, whitespace variations
