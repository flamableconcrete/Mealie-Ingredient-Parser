# Component Standards

## Component Template

Basic Textual screen component template with modern Python type hints:

```python
"""Pattern Group Screen - Batch mode ingredient pattern display and selection."""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header
from textual.reactive import reactive

if TYPE_CHECKING:
    from mealie_parser.models.pattern import PatternGroup


class PatternGroupScreen(Screen[None]):
    """Display grouped ingredient patterns for batch processing.

    Attributes:
        patterns: List of PatternGroup objects to display
        completed_count: Number of completed patterns (reactive)
        skipped_count: Number of skipped patterns (reactive)
    """

    CSS_PATH = "styles/screens.tcss"
    BINDINGS = [
        ("enter", "select_pattern", "Process Pattern"),
        ("s", "skip_pattern", "Skip Pattern"),
        ("u", "unskip_pattern", "Un-skip Pattern"),
        ("d", "show_dashboard", "Dashboard"),
        ("q", "quit_batch_mode", "Back to Recipes"),
    ]

    # Reactive attributes - automatically trigger UI updates
    completed_count: reactive[int] = reactive(0)
    skipped_count: reactive[int] = reactive(0)

    def __init__(
        self,
        patterns: list[PatternGroup],
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize the pattern group screen.

        Args:
            patterns: List of PatternGroup objects to display
            name: Name of the screen (optional)
            id: Unique identifier (optional)
            classes: CSS classes (optional)
        """
        super().__init__(name=name, id=id, classes=classes)
        self.patterns = patterns

    def compose(self) -> ComposeResult:
        """Compose the screen layout with widgets.

        Yields:
            Header, DataTable, Footer widgets
        """
        yield Header(show_clock=True)
        yield DataTable(id="pattern-table", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize screen state when mounted."""
        table = self.query_one("#pattern-table", DataTable)

        # Configure table columns
        table.add_columns("Pattern Text", "Type", "Count", "Status")
        table.cursor_type = "row"
        table.focus()

        # Populate table with pattern data
        self._populate_table()

    def _populate_table(self) -> None:
        """Populate DataTable with pattern groups."""
        table = self.query_one("#pattern-table", DataTable)

        for pattern in self.patterns:
            table.add_row(
                pattern.pattern_text,
                pattern.type,
                str(len(pattern.ingredient_ids)),
                pattern.status,
                key=pattern.id,
            )

    def action_select_pattern(self) -> None:
        """Handle Enter key - open pattern action modal."""
        table = self.query_one("#pattern-table", DataTable)

        if table.cursor_row is None:
            return

        # Get selected pattern from cursor position
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        pattern = self._get_pattern_by_id(str(row_key.value))

        if pattern:
            # Push PatternActionModal and await result
            self.app.push_screen("pattern_action_modal", callback=self._handle_action_result)

    def action_skip_pattern(self) -> None:
        """Handle 's' key - mark pattern as skipped."""
        self.skipped_count += 1

    def action_unskip_pattern(self) -> None:
        """Handle 'u' key - revert skipped pattern to pending."""
        self.skipped_count -= 1

    def action_show_dashboard(self) -> None:
        """Handle 'd' key - display progress dashboard modal."""
        self.app.push_screen("progress_dashboard_modal")

    def action_quit_batch_mode(self) -> None:
        """Handle 'q' key - return to recipe list screen."""
        self.app.pop_screen()

    def _get_pattern_by_id(self, pattern_id: str) -> PatternGroup | None:
        """Retrieve pattern by ID."""
        return next((p for p in self.patterns if p.id == pattern_id), None)

    def _handle_action_result(self, result: dict | None) -> None:
        """Handle callback from PatternActionModal."""
        if result:
            # Process the selected action
            pass
```

## Naming Conventions

**Files and Modules:**
- Screen files: `{purpose}_screen.py` → `pattern_group.py`, `batch_preview.py`
- Modal files: `{purpose}_modal.py` → `pattern_action.py`, `progress_dashboard.py`
- Widget files: `{component_name}.py` → `status_badge.py`, `progress_bar.py`
- Service files: `{service_name}.py` → `pattern_analyzer.py`, `batch_processor.py`
- Model files: `{entity_name}.py` → `pattern.py`, `batch_operation.py`

**Classes:**
- Screens: `{Purpose}Screen` → `PatternGroupScreen`, `BatchPreviewScreen`
- Modals: `{Purpose}Modal` → `PatternActionModal`, `ProgressDashboardModal`
- Widgets: `{ComponentName}` → `StatusBadge`, `ProgressBar`
- Services: `{ServiceName}` → `PatternAnalyzer`, `BatchProcessor`
- Data Models: `{EntityName}` → `PatternGroup`, `BatchOperation`

**Methods and Functions:**
- Public methods: `snake_case` → `populate_table()`, `get_pattern_by_id()`
- Private methods: `_snake_case` → `_populate_table()`, `_handle_action_result()`
- Action handlers: `action_{name}` → `action_select_pattern()`, `action_skip_pattern()`
- Event handlers: `on_{event}` → `on_mount()`, `on_button_pressed()`

**Variables:**
- Local variables: `snake_case` → `pattern_id`, `completed_count`
- Constants: `UPPER_SNAKE_CASE` → `MAX_PATTERNS`, `DEFAULT_TIMEOUT`
- Reactive attributes: `snake_case: reactive[Type] = reactive(default)`
- Widget IDs: `kebab-case` strings → `"pattern-table"`, `"status-badge"`

**Type Hints:**
- Use `from __future__ import annotations` for forward references
- Use `TYPE_CHECKING` block for import-only type hints
- Prefer `list[T]` over `List[T]` (Python 3.13 native generics)
- Use `| None` instead of `Optional[T]` (PEP 604 union syntax)

---
