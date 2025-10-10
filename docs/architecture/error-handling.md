# Error Handling

## Error Handling Layers

```
┌─────────────────────────────────────────────────┐
│                 Screen Layer                    │
│  - Catch exceptions from API layer              │
│  - Display user-friendly notifications          │
│  - Log context-specific errors                  │
│  - Decide whether to continue or abort          │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│                  API Layer                      │
│  - Try/catch around all HTTP operations         │
│  - Log technical details (request/response)     │
│  - Re-raise exceptions to screen layer          │
│  - raise_for_status() for HTTP errors           │
└───────────────────┬─────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              aiohttp / Network                  │
│  - ClientError for network issues               │
│  - asyncio.TimeoutError for timeouts            │
│  - HTTP status codes (4xx, 5xx)                 │
└─────────────────────────────────────────────────┘
```

## Error Handling Examples

### Screen-Level Error Handling

```python
# In RecipeListScreen.review_recipe()
try:
    details = await get_recipe_details(self.session, recipe["slug"])
    # ... process details
except Exception as e:
    logger.error(f"Error reviewing recipe '{recipe.get('name')}': {e}", exc_info=True)
    self.notify(f"Error reviewing recipe: {e}", severity="error", timeout=3)
    # Continue to next recipe (don't crash app)
```

### API-Level Error Handling

```python
# In api.py
async def create_unit(session, name, abbreviation="", description=""):
    try:
        async with session.post(f"{API_URL}/units", json=body) as r:
            r.raise_for_status()
            result = await r.json()
            logger.info(f"Created unit: {name}")
            return result
    except Exception as e:
        logger.error(f"Error creating unit '{name}': {e}", exc_info=True)
        raise  # Re-raise to screen layer
```

## Error Recovery Strategies

| Error Type | Recovery Strategy |
|-----------|------------------|
| Network timeout | API layer logs and re-raises → Screen displays notification → User retries |
| Recipe not found (404) | Log warning, skip recipe, continue with next |
| Duplicate unit (409) | Show error modal, ask user to choose different name |
| Parse failure | Log error, show ingredient as unparsed, allow skip |
| Session closed | App-level check in on_unmount, prevent further operations |

---
