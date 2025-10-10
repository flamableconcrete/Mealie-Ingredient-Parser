# State Management

## Store Structure

The application uses **Textual's reactive system** combined with **Python data classes** for state management. No external state library required.

```plaintext
State Architecture:
├── App-Level State (MealieParserApp)
│   ├── session: aiohttp.ClientSession (persistent HTTP client)
│   ├── units_cache: list[Unit] (loaded in LoadingScreen)
│   ├── foods_cache: list[Food] (loaded in LoadingScreen)
│   └── recipes: list[Recipe] (loaded in LoadingScreen)
│
├── Screen-Level State (Each Screen manages its own reactive state)
│   ├── PatternGroupScreen
│   │   ├── patterns: list[PatternGroup] (passed via __init__)
│   │   ├── completed_count: reactive[int]
│   │   ├── skipped_count: reactive[int]
│   │   └── selected_pattern: reactive[PatternGroup | None]
│   │
│   ├── RecipeListScreen
│   │   ├── recipes: list[Recipe] (passed via __init__)
│   │   ├── stats: reactive[RecipeStats]
│   │   └── filter_mode: reactive[str]
│   │
│   └── IngredientReviewScreen
│       ├── ingredients: list[Ingredient]
│       ├── current_index: reactive[int]
│       └── stats: reactive[ReviewStats]
│
└── Persistent State (SessionState - disk serialization)
    ├── completed_pattern_ids: set[str]
    ├── skipped_pattern_ids: set[str]
    ├── processed_recipe_ids: set[str]
    ├── stats: ProcessingStats
    └── timestamp: datetime
```

## State Management Template

```python
"""State management using Textual reactive system and data classes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from textual.reactive import reactive


@dataclass
class ProcessingStats:
    """Statistics for batch processing session."""

    units_created: int = 0
    foods_created: int = 0
    aliases_added: int = 0
    ingredients_processed: int = 0
    patterns_completed: int = 0
    patterns_skipped: int = 0

    def to_dict(self) -> dict[str, int]:
        """Serialize stats to dictionary for JSON persistence."""
        return {
            "units_created": self.units_created,
            "foods_created": self.foods_created,
            "aliases_added": self.aliases_added,
            "ingredients_processed": self.ingredients_processed,
            "patterns_completed": self.patterns_completed,
            "patterns_skipped": self.patterns_skipped,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> ProcessingStats:
        """Deserialize stats from dictionary."""
        return cls(**data)


@dataclass
class SessionState:
    """Persistent session state for recovery after interruption."""

    completed_pattern_ids: set[str] = field(default_factory=set)
    skipped_pattern_ids: set[str] = field(default_factory=set)
    processed_recipe_ids: set[str] = field(default_factory=set)
    stats: ProcessingStats = field(default_factory=ProcessingStats)
    timestamp: datetime = field(default_factory=datetime.now)
    schema_version: str = "1.0"

    def to_dict(self) -> dict:
        """Serialize session state to dictionary for JSON persistence."""
        return {
            "schema_version": self.schema_version,
            "timestamp": self.timestamp.isoformat(),
            "completed_pattern_ids": list(self.completed_pattern_ids),
            "skipped_pattern_ids": list(self.skipped_pattern_ids),
            "processed_recipe_ids": list(self.processed_recipe_ids),
            "stats": self.stats.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> SessionState:
        """Deserialize session state from dictionary."""
        if data.get("schema_version") != "1.0":
            raise ValueError(f"Incompatible schema version: {data.get('schema_version')}")

        return cls(
            completed_pattern_ids=set(data["completed_pattern_ids"]),
            skipped_pattern_ids=set(data["skipped_pattern_ids"]),
            processed_recipe_ids=set(data["processed_recipe_ids"]),
            stats=ProcessingStats.from_dict(data["stats"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            schema_version=data["schema_version"],
        )


# Example: Using reactive state in a screen
class PatternGroupScreen(Screen[None]):
    """Pattern group screen with reactive state."""

    # Reactive attributes - auto-trigger UI updates on change
    completed_count: reactive[int] = reactive(0)
    skipped_count: reactive[int] = reactive(0)

    def watch_completed_count(self, old: int, new: int) -> None:
        """React to completed count changes - update status bar.

        Textual automatically calls this when completed_count changes.
        """
        self._update_status_bar()

    def watch_skipped_count(self, old: int, new: int) -> None:
        """React to skipped count changes - update status bar."""
        self._update_status_bar()

    def mark_pattern_completed(self, pattern_id: str) -> None:
        """Mark pattern as completed and persist state."""
        self.session_state.completed_pattern_ids.add(pattern_id)
        self.completed_count += 1  # Triggers watch_completed_count automatically

        # Persist to disk
        self.app.call_later(self._persist_state)
```

## State Management Patterns

**Three-tier state model:**
1. **App-level state:** Shared data (API caches, HTTP session) stored in `MealieParserApp`
2. **Screen-level state:** UI-specific reactive state managed locally in each screen
3. **Persistent state:** `SessionState` serialized to JSON for recovery

**Reactive watchers:** `watch_{attribute}()` methods auto-called on state changes, trigger UI updates without manual event dispatching.

---
