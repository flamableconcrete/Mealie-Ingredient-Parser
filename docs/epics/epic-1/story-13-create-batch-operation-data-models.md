# Story 1.3: Create Batch Operation Data Models

**As a** developer,
**I want** well-defined data models for batch operations,
**so that** UI and business logic can reliably interact with batch processing state.

## Acceptance Criteria

1. Define `PatternGroup` data class containing: pattern_text, ingredient_ids, recipe_ids, suggested_similar_patterns, operation_status (pending/processing/completed/skipped)
2. Define `BatchOperation` data class containing: operation_type (create_unit/create_food/add_alias), target_pattern, affected_ingredients, mealie_entity_id (unit/food ID after creation)
3. Data models support serialization for potential future state persistence
4. Models include validation logic: non-empty pattern_text, valid ingredient/recipe ID references
5. Type hints added for all data model fields
6. Unit tests validate data model creation, validation, and edge cases
