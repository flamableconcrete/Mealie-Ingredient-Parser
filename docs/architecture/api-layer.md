# API Layer

## API Function Categories

**File:** `mealie_parser/api.py`

### 1. Data Fetching (Read Operations)

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `get_all_recipes(session)` | `GET /recipes` | Fetch all recipes (paginated) |
| `get_recipe_details(session, slug)` | `GET /recipes/{slug}` | Get detailed recipe with ingredients |
| `get_units_full(session)` | `GET /units` | Fetch all units |
| `get_foods_full(session)` | `GET /foods` | Fetch all foods |

### 2. Entity Creation (Write Operations)

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `create_unit(session, name, abbreviation, description)` | `POST /units` | Create new unit |
| `create_food(session, name, description)` | `POST /foods` | Create new food |

### 3. Entity Updates (Modify Operations)

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `update_recipe(session, slug, recipe_data)` | `PUT /recipes/{slug}` | Update recipe with new ingredient data |
| `add_food_alias(session, food_id, alias)` | `PUT /foods/{food_id}` | Add alias to existing food |
| `add_unit_alias(session, unit_id, alias)` | `PUT /units/{unit_id}` | Add alias to existing unit |

### 4. Parsing (NLP Operations)

| Function | Endpoint | Purpose |
|----------|----------|---------|
| `parse_ingredients(session, ingredients)` | `POST /parser/ingredients` | Parse ingredient strings using Mealie NLP |

## API Error Handling Pattern

All API functions follow consistent error handling:

```python
async def create_unit(session, name, abbreviation="", description=""):
    """Create a new unit in Mealie."""
    body = {
        "name": name,
        "abbreviation": abbreviation or name[:3],
        "description": description,
        "fraction": True,
        "useAbbreviation": False,
    }
    try:
        async with session.post(f"{API_URL}/units", json=body) as r:
            r.raise_for_status()  # Raises for 4xx/5xx
            result = await r.json()
            logger.info(f"Created unit: {name}")
            return result
    except Exception as e:
        logger.error(f"Error creating unit '{name}': {e}", exc_info=True)
        logger.debug(f"Unit data: {body}")
        raise  # Re-raise for caller to handle
```

**Pattern:**
1. Try API call
2. `raise_for_status()` for HTTP errors
3. Log success with INFO level
4. Catch all exceptions, log with ERROR level
5. Re-raise for screen-level handling

## Batch API Extensions

**New Functions (Epic 1 Story 1.4):**
```python
async def update_ingredient_unit_batch(session, unit_id, ingredient_ids, recipe_id):
    """Update multiple ingredients with the same unit."""
    # Iterates over ingredient_ids
    # Calls existing update logic for each
    # Implements retry logic
    # Returns BatchUpdateResult
    pass

async def update_ingredient_food_batch(session, food_id, ingredient_ids, recipe_id):
    """Update multiple ingredients with the same food."""
    pass
```

**Pattern:** New batch functions **wrap existing API functions** rather than replace them.

---
