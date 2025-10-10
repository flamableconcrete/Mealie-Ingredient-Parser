# Architecture Patterns

## 1. Screen-Based Navigation

The application uses Textual's **screen stack pattern** for navigation:

- **Screen Stack:** Screens are pushed onto a stack and popped when dismissed
- **Modal Overlays:** Modals appear as overlays without replacing the underlying screen
- **State Preservation:** Previous screens remain in memory with state intact

```python
# Navigation pattern
self.app.push_screen(RecipeListScreen(...))  # Add to stack
self.app.pop_screen()                        # Remove from stack
await self.app.push_screen_wait(Modal())     # Wait for modal result
```

## 2. Persistent Session Pattern

The application maintains a **single aiohttp ClientSession** throughout its lifecycle:

- **Created:** In `MealieParserApp.on_mount()`
- **Shared:** Passed to all screens via constructor
- **Cleaned Up:** In `MealieParserApp.on_unmount()`

**Rationale:** Connection pooling, authentication header reuse, resource efficiency.

## 3. Reactive State Updates

Textual's **reactive system** automatically triggers UI updates when state changes:

```python
class RecipeListScreen(Screen):
    # Reactive attributes trigger UI updates
    units_created: reactive[int] = reactive(0)

    def watch_units_created(self, old: int, new: int) -> None:
        """Called automatically when units_created changes."""
        self.update_status_bar()
```

## 4. API Function Abstraction

All Mealie API interactions are **centralized in `api.py`**:

- **Single Responsibility:** Each function handles one API operation
- **Error Handling:** Try/catch with logging at the API layer
- **Session Injection:** Session passed as parameter (no global state)

---
