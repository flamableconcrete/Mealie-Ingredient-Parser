# Batch Integration Points

## Overview

Batch mode enhancements integrate with existing architecture through:

1. **New screen entry point** from ModeSelectionScreen
2. **Reuse of existing modals** (CreateUnitModal, CreateFoodModal, SelectFoodModal)
3. **New batch-specific screens** (PatternGroupScreen, BatchPreviewScreen)
4. **Extension of API layer** with batch update functions
5. **Preservation of sequential mode** (no changes to RecipeListScreen or IngredientReviewScreen)

## Integration Architecture

```
                  ┌──────────────────┐
                  │ ModeSelection    │
                  │ Screen           │
                  └────┬────────┬────┘
                       │        │
          ┌────────────┘        └────────────┐
          │                                  │
          ▼ (Sequential)                    ▼ (Batch)
┌──────────────────┐              ┌──────────────────────┐
│ RecipeListScreen │              │ PatternGroupScreen   │ ◄─ NEW
│ (EXISTING)       │              │ (NEW)                │
│                  │              │                      │
│ No changes       │              │ - Display pattern    │
│ required         │              │   groups             │
│                  │              │ - Batch actions      │
└─────────┬────────┘              └──────┬───────────────┘
          │                              │
          ▼                              ▼
┌──────────────────────┐       ┌──────────────────────┐
│ IngredientReview     │       │ BatchPreviewScreen   │ ◄─ NEW
│ Screen               │       │ (NEW)                │
│ (EXISTING)           │       │                      │
│                      │       │ - Show affected      │
│ Reuses existing      │       │   ingredients        │
│ modals:              │       │ - Confirm batch      │
│ - UnitActionModal    │◄──────┼─ Reuses existing     │
│ - CreateUnitModal    │       │   modals             │
│ - FoodActionModal    │       │                      │
│ - CreateFoodModal    │       └──────────────────────┘
│ - SelectFoodModal    │
└──────────────────────┘
```

## Integration Point 1: Mode Selection

**Screen:** `ModeSelectionScreen` (existing)

**Enhancement:** Add batch mode entry option

**Impact:** Minimal - add button/binding for batch mode

## Integration Point 2: Batch Screen Flow

**New Screens:**
- `PatternGroupScreen` - Display unique unit/food patterns
- `BatchPreviewScreen` - Confirm batch operations

**Integration:** Coexist with existing RecipeListScreen (no modifications)

## Integration Point 3: Modal Reuse

**Strategy:** Batch workflows **reuse existing modals**

**Example:**
```python
# In PatternGroupScreen (NEW)
async def create_unit_batch(self, pattern):
    """Create unit and apply to all matching ingredients."""

    # REUSE existing CreateUnitModal
    unit_data = await self.app.push_screen_wait(
        CreateUnitModal(pattern.unit_text)
    )

    # NEW: Batch preview screen
    confirmed = await self.app.push_screen_wait(
        BatchPreviewScreen(
            operation_type="create_unit",
            affected_ingredients=pattern.ingredients
        )
    )

    if confirmed:
        # NEW: Batch API call
        result = await update_ingredient_unit_batch(
            self.session,
            unit_data["id"],
            pattern.ingredient_ids
        )
```

## Integration Point 4: State Sharing

**Challenge:** PatternGroupScreen and RecipeListScreen need to share processed recipe state.

**Solution:** Pass state through screen constructors (existing pattern)

```python
# In PatternGroupScreen (NEW)
def __init__(self, patterns, unparsed_recipes, session, units, foods):
    super().__init__()
    self.patterns = patterns              # NEW batch-specific data
    self.unparsed_recipes = unparsed_recipes  # SHARED with RecipeListScreen
    self.session = session                # SHARED
    self.known_units = units              # SHARED
    self.known_foods = foods              # SHARED
```

---
