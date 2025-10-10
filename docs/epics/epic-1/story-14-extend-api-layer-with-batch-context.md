# Story 1.4: Extend API Layer with Batch Context

**As a** developer,
**I want** API helper functions that support batch operations,
**so that** multiple ingredients can be updated efficiently after unit/food creation.

## Acceptance Criteria

1. Create `update_ingredient_unit_batch()` function accepting unit_id and list of ingredient_ids, calling Mealie API for each ingredient
2. Create `update_ingredient_food_batch()` function accepting food_id and list of ingredient_ids, calling Mealie API for each ingredient
3. Batch functions include error handling: collect failures, continue processing remaining ingredients, return success/failure summary
4. Functions reuse existing aiohttp session from app context
5. Functions log each API call for troubleshooting (ingredient ID, operation, result)
6. Integration tests with mocked API responses validate batch update logic and error recovery

---
