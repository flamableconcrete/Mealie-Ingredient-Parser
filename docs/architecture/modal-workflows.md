# Modal Workflows

## Modal Architecture

Modals are **overlay dialogs** that:
- Appear on top of current screen
- Block interaction with underlying screen
- Return result to caller via callback or await pattern

## Existing Modals

**Location:** `mealie_parser/modals/`

### UnitActionModal

**File:** `unit_modals.py`

**Purpose:** Ask user what to do with unknown unit

**Options:**
- Create new unit → Opens CreateUnitModal
- Skip ingredient

### CreateUnitModal

**File:** `unit_modals.py`

**Purpose:** Collect unit details (name, abbreviation, description)

**Flow:**
1. User fills form fields
2. Validation (abbreviation required)
3. Call `create_unit()` API function
4. Return created unit ID to caller

### FoodActionModal

**File:** `food_modals.py`

**Purpose:** Ask user what to do with unknown food

**Options:**
- Create new food → Opens CreateFoodModal
- Add alias to existing food → Opens SelectFoodModal
- Skip ingredient

### CreateFoodModal

**File:** `food_modals.py`

**Purpose:** Collect food details (name, description)

**Flow:**
1. User fills form fields
2. Validation (name required)
3. Call `create_food()` API function
4. Return created food ID to caller

### SelectFoodModal

**File:** `food_modals.py`

**Purpose:** Searchable table to select existing food for alias

**Flow:**
1. Display DataTable of all foods
2. User searches/filters
3. User selects food
4. Call `add_food_alias()` API function
5. Return selected food ID to caller

## Modal Invocation Pattern

```python
# In IngredientReviewScreen
async def handle_missing_unit(self, unit_name):
    """Open modal workflow for missing unit."""
    result = await self.app.push_screen_wait(
        UnitActionModal(unit_name)
    )

    if result["action"] == "create":
        # User chose to create unit
        unit_data = await self.app.push_screen_wait(
            CreateUnitModal(unit_name)
        )

        # API call happens in modal
        self.stats["units_created"].append(unit_data["id"])

        # Refresh cache
        self.known_units = await get_units_full(self.session)
```

---
