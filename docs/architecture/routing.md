# Routing

## Route Configuration

Textual uses a **screen stack model** rather than URL-based routing. Navigation is managed through `push_screen()`, `pop_screen()`, and `switch_screen()` methods.

```python
"""Screen navigation and routing configuration."""

from __future__ import annotations

from textual.app import App
from textual.screen import Screen


class MealieParserApp(App):
    """Main application with navigation configuration."""

    SCREENS = {
        "loading": LoadingScreen,
        "recipe_list": RecipeListScreen,
        "ingredient_review": IngredientReviewScreen,
        "pattern_group": PatternGroupScreen,
        "batch_preview": BatchPreviewScreen,
    }

    def on_mount(self) -> None:
        """Initialize app and start with loading screen."""
        self.push_screen("loading")

    async def navigate_to_batch_mode(self, patterns: list, session_state) -> None:
        """Navigate to batch mode (pattern group screen)."""
        await self.push_screen(PatternGroupScreen(patterns, session_state))

    async def show_batch_preview(
        self,
        operation_type: str,
        affected_ingredients: list,
        *,
        callback=None,
    ) -> None:
        """Show batch preview confirmation screen."""
        def handle_result(confirmed: bool) -> None:
            if callback:
                callback(confirmed)

        await self.push_screen(
            BatchPreviewScreen(operation_type, affected_ingredients),
            callback=handle_result,
        )

    def return_to_previous_screen(self) -> None:
        """Navigate back to previous screen (pop from stack)."""
        self.pop_screen()
```

## Navigation Patterns

**Screen stack model:** `push_screen()` adds to stack, `pop_screen()` removes. Maintains navigation history automatically.

**Callback-based modal flow:** Modals use `push_screen(modal, callback=handler)` pattern.

**Centralized navigation methods:** `navigate_to_batch_mode()`, `navigate_to_sequential_mode()` in App class.

**Route guards:** Validation happens in action methods before navigation (e.g., check patterns exist before entering batch mode).

**State preservation:** Previous screens remain in memory with state intact when pushing new screens.

---
