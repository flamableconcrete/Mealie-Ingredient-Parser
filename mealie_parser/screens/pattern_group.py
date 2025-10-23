"""Pattern group screen for batch ingredient processing."""

import asyncio
from typing import Any

import aiohttp
from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    LoadingIndicator,
    Static,
    Switch,
    TabbedContent,
    TabPane,
)

from mealie_parser.api import get_foods_full, get_recipe_details, parse_ingredients
from mealie_parser.modals.data_management_modal import DataManagementModal
from mealie_parser.modals.parse_config_modal import ParseConfigModal
from mealie_parser.models.pattern import PatternGroup, PatternStatus
from mealie_parser.models.session_state import SessionState
from mealie_parser.services.parse_result_processor import (
    extract_parsed_food,
    extract_parsed_unit,
    get_matched_food_id,
    get_matched_unit_id,
)
from mealie_parser.services.table_manager import PatternTableManager
from mealie_parser.session_manager import SessionManager


class PatternGroupScreen(Screen):
    """
    Screen for displaying and processing pattern groups in batch mode.

    Shows tabs for unit patterns and food patterns with batch action capabilities.

    Attributes
    ----------
    unit_patterns : list[PatternGroup]
        List of unit patterns to process
    food_patterns : list[PatternGroup]
        List of food patterns to process
    unparsed_recipes : list[dict]
        List of unparsed recipes
    session : aiohttp.ClientSession
        Persistent HTTP session for API calls
    known_units : list[dict]
        List of known units from Mealie
    known_foods : list[dict]
        List of known foods from Mealie
    processed_count : int
        Number of patterns successfully processed
    skipped_count : int
        Number of patterns skipped by user
    """

    CSS = """
    PatternGroupScreen {
        layout: vertical;
    }

    #title-bar {
        height: 3;
        background: $primary;
        padding: 0 2;
        content-align: center middle;
    }

    #title {
        text-style: bold;
        color: $text;
        text-align: center;
        width: 100%;
    }

    #controls {
        height: auto;
        layout: horizontal;
        align: left middle;
        background: $panel;
        padding: 1 2;
    }

    #controls Button {
        margin: 0 1;
    }

    #back-button {
        min-width: 20;
    }

    #food-controls, #unit-controls {
        height: auto;
        background: $panel;
        padding: 0 1;
        align: center middle;
    }

    .controls-inner {
        width: auto;
        height: auto;
    }

    .controls-inner Button {
        margin: 0 1;
    }

    TabbedContent {
        height: 1fr;
    }

    DataTable {
        height: 1fr;
    }

    #status-bar {
        height: 3;
        background: $surface;
        padding: 0 1;
    }

    .skipped-row {
        color: $text-muted;
        opacity: 0.6;
        text-style: strike;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+t", "switch_tab", "Switch Tab"),
        ("enter", "select_pattern", "Select Pattern"),
        ("s", "skip_pattern", "Skip"),
        ("u", "undo_skip", "Undo Skip"),
        ("p", "start_parsing", "Start Parsing"),
    ]

    processed_count = reactive(0)
    skipped_count = reactive(0)
    parsing_started = reactive(False)  # Track if any parsing has occurred
    hide_matched_foods = reactive(False)  # Toggle to hide matched items in food tab
    hide_matched_units = reactive(False)  # Toggle to hide matched items in unit tab

    # Helper methods for common operations
    def get_current_tab_info(self) -> tuple[DataTable, bool, str]:
        """
        Get information about the currently active tab.

        Returns
        -------
        tuple[DataTable, bool, str]
            (table widget, is_unit_table, table_id)
        """
        tabbed_content = self.query_one(TabbedContent)
        current_tab = tabbed_content.active

        if current_tab == "units":
            table = self.query_one("#unit-table", DataTable)
            return table, True, "#unit-table"
        table = self.query_one("#food-table", DataTable)
        return table, False, "#food-table"

    def get_pattern_status(self, pattern: PatternGroup, is_unit: bool) -> PatternStatus:
        """
        Get the appropriate status for the pattern based on table type.

        Parameters
        ----------
        pattern : PatternGroup
            The pattern to check
        is_unit : bool
            True if checking unit status, False for food status

        Returns
        -------
        PatternStatus
            The current status for the appropriate field
        """
        return pattern.unit_status if is_unit else pattern.food_status

    def get_checkbox_value(self, status: PatternStatus) -> str:
        """
        Get checkbox display value based on pattern status.

        Parameters
        ----------
        status : PatternStatus
            The current pattern status

        Returns
        -------
        str
            Checkbox character to display ("☐", "☑", or "")
        """
        from mealie_parser.models import PatternStatus

        if status == PatternStatus.UNMATCHED:
            return "☐"
        if status == PatternStatus.QUEUED:
            return "☑"
        return ""

    def get_status_display(self, status: PatternStatus) -> str:
        """
        Get Rich-formatted status display string.

        Parameters
        ----------
        status : PatternStatus
            The pattern status

        Returns
        -------
        str
            Rich-formatted status string
        """
        status_map = {
            "pending": "",
            "parsing": "[cyan]parsing[/cyan]",
            "matched": "[green]✓ matched[/green]",
            "unmatched": "[yellow]⚠ unmatched[/yellow]",
            "queued": "[blue]📤 queued[/blue]",
            "ignore": "[orange1]skipped[/orange1]",
            "error": "[red]✗ error[/red]",
        }
        return status_map.get(status.value, status.value)

    def __init__(
        self,
        patterns: list[PatternGroup],
        unparsed_recipes: list[dict],
        session: aiohttp.ClientSession,
        known_units: list[dict],
        known_foods: list[dict],
    ):
        """
        Initialize pattern group screen.

        Parameters
        ----------
        patterns : list[PatternGroup]
            Unified list of patterns (shown in both tabs with different columns)
        unparsed_recipes : list[dict]
            List of unparsed recipes
        session : aiohttp.ClientSession
            Persistent HTTP session for API calls
        known_units : list[dict]
            List of known units from Mealie
        known_foods : list[dict]
            List of known foods from Mealie
        """
        super().__init__()
        self.patterns = patterns
        self.unparsed_recipes = unparsed_recipes
        self.session = session
        self.known_units = known_units
        self.known_foods = known_foods
        self.session_manager = SessionManager()

        # Initialize session state if not exists
        # Handle case when running outside of app context (e.g., tests)
        try:
            if hasattr(self.app, "session_state") and self.app.session_state:
                self.session_state = self.app.session_state
                logger.info(f"Resuming session: {self.session_state.summary}")
                self._restore_pattern_states()
            else:
                self.session_state = SessionState(mode="batch")
                logger.info("Created new session state")
        except Exception:
            # Running outside app context (e.g., in tests)
            self.session_state = SessionState(mode="batch")
            logger.debug("Created session state without app context")

        logger.info(f"Initialized PatternGroupScreen: {len(patterns)} patterns (shown in both tabs)")

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        with Container(id="title-bar"):
            yield Static("Batch Mode", id="title")
        with Horizontal(id="controls"):
            yield Button("← Back [escape]", id="back-button", variant="default")
            yield Button("Data Management", id="data-management", variant="default")
            yield Button("Start Parsing [p]", id="start-parsing", variant="primary")
        with TabbedContent(initial="foods"):
            with TabPane("Food Patterns", id="foods"), Vertical():
                with Container(id="food-controls"):
                    with Horizontal(classes="controls-inner"):
                        yield Button("Select All Unmatched", id="toggle-food", variant="primary")
                        yield Switch(value=False, id="hide-matched-food")
                        yield Static("Hide Matched", classes="switch-label")
                yield DataTable(id="food-table")
            with TabPane("Unit Patterns", id="units"), Vertical():
                with Container(id="unit-controls"):
                    with Horizontal(classes="controls-inner"):
                        yield Button("Select All Unmatched", id="toggle-unit", variant="primary")
                        yield Switch(value=False, id="hide-matched-unit")
                        yield Static("Hide Matched", classes="switch-label")
                yield DataTable(id="unit-table")
        yield LoadingIndicator()
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Initialize tables when screen mounts."""
        logger.info("PatternGroupScreen.on_mount: Starting")
        self.query_one(LoadingIndicator).display = True
        self.call_later(self._initialize_tables)
        logger.info("PatternGroupScreen.on_mount: Worker started")

    async def _initialize_tables(self) -> None:
        """Initialize tables in a worker to avoid blocking."""
        logger.info("PatternGroupScreen._initialize_tables: Starting table initialization")
        # Create table managers to handle all table state
        unit_column_config = [
            ("Pattern Text", 50),
            ("Status", 15),
            ("Parsed Unit", 20),
            ("Create", 8),
        ]
        self.unit_table_manager = PatternTableManager(
            patterns=self.patterns,
            table_id="#unit-table",
            is_unit_table=True,
            column_widths=unit_column_config,
        )
        food_column_config = [
            ("Pattern Text", 50),
            ("Status", 15),
            ("Parsed Food", 20),
            ("Create", 8),
        ]
        self.food_table_manager = PatternTableManager(
            patterns=self.patterns,
            table_id="#food-table",
            is_unit_table=False,
            column_widths=food_column_config,
        )

        # Setup unit patterns table using table manager
        unit_table = self.query_one("#unit-table", DataTable)
        self.unit_table_manager.initialize_table(
            unit_table,
            hide_matched=self.hide_matched_units,
        )

        # Store column keys for unit table - get them from the columns property
        columns = list(unit_table.columns.keys())
        self.unit_status_col = columns[1]
        self.unit_parsed_unit_col = columns[2]
        self.unit_create_col = columns[3]

        # Setup food patterns table using table manager
        food_table = self.query_one("#food-table", DataTable)
        self.food_table_manager.initialize_table(
            food_table,
            hide_matched=self.hide_matched_foods,
        )

        # Store column keys for food table - get them from the columns property
        columns = list(food_table.columns.keys())
        self.food_status_col = columns[1]
        self.food_parsed_food_col = columns[2]
        self.food_create_col = columns[3]

        # Update status bar
        self.update_status_bar()

        # Check if any patterns have been parsed (have status other than PENDING)
        from mealie_parser.models import PatternStatus

        any_parsed = any(
            p.unit_status != PatternStatus.PENDING or p.food_status != PatternStatus.PENDING for p in self.patterns
        )
        if any_parsed:
            self.parsing_started = True
            logger.info("Detected previously parsed patterns, setting parsing_started=True")
        self.query_one(LoadingIndicator).display = False
        logger.info("PatternGroupScreen._initialize_tables: Finished table initialization")

    def update_status_bar(self) -> None:
        """Update the status bar with current progress."""
        total = len(self.patterns)

        # Check if status bar widget exists (may not be mounted yet)
        try:
            status = self.query_one("#status-bar", Static)
            status.update(
                f"Processed: {self.processed_count}/{total} | Skipped: {self.skipped_count}\n"
                f"[Enter] Select  [Ctrl+T] Switch Tab  [Escape] Back"
            )
        except Exception:
            # Widget not mounted yet, skip update
            pass

    def watch_processed_count(self, old_value: int, new_value: int) -> None:
        """React to processed count changes."""
        logger.debug(f"Processed count updated: {old_value} -> {new_value}")
        self.update_status_bar()

    def watch_skipped_count(self, old_value: int, new_value: int) -> None:
        """React to skipped count changes."""
        logger.debug(f"Skipped count updated: {old_value} -> {new_value}")
        self.update_status_bar()

    def watch_parsing_started(self, old_value: bool, new_value: bool) -> None:
        """React to parsing_started changes - update button label."""
        try:
            start_btn = self.query_one("#start-parsing", Button)

            if new_value:
                # Change button to "Continue Parsing"
                start_btn.label = "Continue Parsing [p]"
            else:
                # Reset to "Start Parsing"
                start_btn.label = "Start Parsing [p]"
        except Exception:
            pass

    def watch_hide_matched_foods(self, old_value: bool, new_value: bool) -> None:
        """React to hide_matched_foods toggle - update food table."""
        if hasattr(self, "food_table_manager"):
            # Refresh food table with filter
            self.refresh_food_table()

    def watch_hide_matched_units(self, old_value: bool, new_value: bool) -> None:
        """React to hide_matched_units toggle - update unit table."""
        if hasattr(self, "unit_table_manager"):
            # Refresh unit table with filter
            self.refresh_unit_table()

    def _restore_pattern_states(self) -> None:
        """
        Restore pattern states from session.

        Marks patterns as completed/skipped based on session state.
        """
        if not self.session_state:
            return

        from mealie_parser.models import PatternStatus

        logger.info("Restoring pattern states from session")
        restored_processed = 0
        restored_skipped = 0

        # Restore patterns
        for pattern in self.patterns:
            if pattern.pattern_text in self.session_state.processed_patterns:
                # Mark both unit and food as matched (completed)
                pattern.transition_unit_to(PatternStatus.MATCHED)
                pattern.transition_food_to(PatternStatus.MATCHED)
                restored_processed += 1
            elif pattern.pattern_text in self.session_state.skipped_patterns:
                # Mark both unit and food as ignored (skipped)
                pattern.transition_unit_to(PatternStatus.IGNORE)
                pattern.transition_food_to(PatternStatus.IGNORE)
                restored_skipped += 1

        # Update counts
        self.processed_count = restored_processed
        self.skipped_count = restored_skipped

        logger.info(f"Restored {restored_processed} processed, {restored_skipped} skipped patterns")

    def _save_session_state(self) -> None:
        """
        Save current session state to disk.

        Persists progress for crash recovery.
        """
        try:
            self.session_state.update_timestamp()
            self.session_manager.save_session(self.session_state)
            logger.debug("Session state saved successfully")
        except Exception as e:
            logger.error(f"Failed to save session state: {e}", exc_info=True)
            # Don't interrupt workflow on save failure

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection from DataTable click or Enter key."""
        # This event is no longer used since we switched to cell cursor type
        # Cell selection is now handled in on_data_table_cell_selected
        pass

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle cell selection - check which column was clicked."""
        # Get the table and determine if it's unit or food
        table, is_unit, _ = self.get_current_tab_info()

        column_index = event.coordinate.column
        display_row_index = event.coordinate.row

        # Map display row index to original pattern index using table manager
        table_manager = self.unit_table_manager if is_unit else self.food_table_manager
        pattern_index = table_manager.get_pattern_index(display_row_index)

        if pattern_index is None:
            logger.warning(f"Could not map display row {display_row_index} to pattern index")
            return

        # Check which column was clicked
        if column_index == 3:  # Create column
            # Handle checkbox click
            self.run_worker(
                self._handle_create_checkbox_click(pattern_index, is_unit),
                exclusive=False,
            )
        elif column_index == 1 or column_index == 0:  # Status column
            # Check pattern status and open appropriate modal
            if pattern_index < len(self.patterns):
                pattern = self.patterns[pattern_index]
                from mealie_parser.models import PatternStatus

                current_status = pattern.unit_status if is_unit else pattern.food_status

                if current_status == PatternStatus.UNMATCHED:
                    # Open unmatched modal for this pattern
                    self.run_worker(
                        self._handle_unmatched_status_click(pattern, is_unit, pattern_index),
                        exclusive=False,
                    )
                elif current_status == PatternStatus.PENDING:
                    # Open parse modal for pending pattern
                    self.run_worker(
                        self._handle_pending_pattern_click(pattern, is_unit, pattern_index),
                        exclusive=False,
                    )
        # For all other columns, do nothing (don't open any modal)

    async def _handle_unmatched_status_click(self, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """Handle clicking the Status column for an UNMATCHED pattern."""
        # Delegate to existing handle_unmatched_pattern method
        await self.handle_unmatched_pattern(pattern, is_unit, row_index)

    def _update_unit_status_from_parse(self, pattern: PatternGroup, parsed_unit_name: str) -> None:
        """Update pattern unit status based on parsed unit.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to update
        parsed_unit_name : str
            Parsed unit name
        """
        from mealie_parser.models import PatternStatus
        from mealie_parser.services.parse_result_processor import check_unit_match

        if parsed_unit_name:
            pattern.parsed_unit = parsed_unit_name
            if check_unit_match(parsed_unit_name, self.known_units):
                if pattern.unit_status != PatternStatus.MATCHED:
                    pattern.transition_unit_to(PatternStatus.MATCHED)
                pattern.matched_unit_id = get_matched_unit_id(parsed_unit_name, self.known_units)
                logger.info(f"Pattern '{pattern.pattern_text}' matched unit: {parsed_unit_name}")
            else:
                if pattern.unit_status != PatternStatus.UNMATCHED:
                    pattern.transition_unit_to(PatternStatus.UNMATCHED)
                logger.info(f"Pattern '{pattern.pattern_text}' parsed but no unit match: {parsed_unit_name}")
        else:
            if pattern.unit_status != PatternStatus.UNMATCHED:
                pattern.transition_unit_to(PatternStatus.UNMATCHED)
            logger.info(f"Pattern '{pattern.pattern_text}' parsed but no unit match")

    def _update_food_status_from_parse(self, pattern: PatternGroup, parsed_food_name: str) -> None:
        """Update pattern food status based on parsed food.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to update
        parsed_food_name : str
            Parsed food name
        """
        from mealie_parser.models import PatternStatus
        from mealie_parser.services.parse_result_processor import check_food_match

        if parsed_food_name:
            pattern.parsed_food = parsed_food_name
            if check_food_match(parsed_food_name, self.known_foods):
                if pattern.food_status != PatternStatus.MATCHED:
                    pattern.transition_food_to(PatternStatus.MATCHED)
                pattern.matched_food_id = get_matched_food_id(parsed_food_name, self.known_foods)
                logger.info(f"Pattern '{pattern.pattern_text}' matched food: {parsed_food_name}")
            else:
                if pattern.food_status != PatternStatus.UNMATCHED:
                    pattern.transition_food_to(PatternStatus.UNMATCHED)
                logger.info(f"Pattern '{pattern.pattern_text}' parsed but no food match: {parsed_food_name}")
        else:
            if pattern.food_status != PatternStatus.UNMATCHED:
                pattern.transition_food_to(PatternStatus.UNMATCHED)
            logger.info(f"Pattern '{pattern.pattern_text}' parsed but no food match")

    async def _handle_pending_pattern_click(  # noqa: C901
        self, pattern: PatternGroup, is_unit: bool, row_index: int
    ) -> None:
        """Handle clicking a PENDING pattern to parse it.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to parse
        is_unit : bool
            True if from unit table, False if from food table
        row_index : int
            Row index in table
        """
        from mealie_parser.api import parse_ingredients
        from mealie_parser.modals.parse_config_modal import ParseConfigModal
        from mealie_parser.models import PatternStatus

        logger.info(f"Opening parse modal for pending pattern: {pattern.pattern_text}")

        # Show parse config modal in single-item mode
        config = await self.app.push_screen_wait(
            ParseConfigModal(parsing_started=False, single_item=True, item_name=pattern.pattern_text)
        )

        if config is None:
            logger.info("Parse cancelled for pending pattern")
            return

        method = config["method"]
        logger.info(f"Parsing pattern '{pattern.pattern_text}' with method {method}")

        # Update status to PARSING for both components
        if pattern.unit_status == PatternStatus.PENDING:
            pattern.transition_unit_to(PatternStatus.PARSING)
        if pattern.food_status == PatternStatus.PENDING:
            pattern.transition_food_to(PatternStatus.PARSING)
        self.refresh_both_tables()

        try:
            # Parse the pattern text
            result = await parse_ingredients(self.session, [pattern.pattern_text], parser=method)

            if result and len(result) > 0:
                parsed = result[0]
                ingredient = parsed.get("ingredient", {})

                # Extract BOTH unit and food from the parse result
                parsed_unit_name = extract_parsed_unit(ingredient)
                parsed_food_name = extract_parsed_food(ingredient)

                logger.info(
                    f"Parse result for '{pattern.pattern_text}': unit='{parsed_unit_name}', food='{parsed_food_name}'"
                )

                # Update unit and food components
                self._update_unit_status_from_parse(pattern, parsed_unit_name)
                self._update_food_status_from_parse(pattern, parsed_food_name)
            else:
                # Parse failed - set to ERROR
                error_msg = f"Parser returned no results for '{pattern.pattern_text}'"
                if is_unit:
                    if pattern.unit_status.can_transition_to(PatternStatus.ERROR):
                        pattern.transition_unit_to(PatternStatus.ERROR, error_msg=error_msg)
                    else:
                        logger.warning(
                            f"Cannot transition unit status from {pattern.unit_status.value} to ERROR, skipping state change"
                        )
                else:
                    if pattern.food_status.can_transition_to(PatternStatus.ERROR):
                        pattern.transition_food_to(PatternStatus.ERROR, error_msg=error_msg)
                    else:
                        logger.warning(
                            f"Cannot transition food status from {pattern.food_status.value} to ERROR, skipping state change"
                        )
                logger.warning(error_msg)

        except Exception as e:
            logger.error(f"Error parsing pattern '{pattern.pattern_text}': {e}", exc_info=True)
            error_msg = f"Parse error: {str(e)}"
            # Only transition to ERROR if not already in a terminal state (MATCHED)
            if is_unit:
                if pattern.unit_status.can_transition_to(PatternStatus.ERROR):
                    pattern.transition_unit_to(PatternStatus.ERROR, error_msg=error_msg)
                else:
                    logger.warning(
                        f"Cannot transition unit status from {pattern.unit_status.value} to ERROR, skipping state change"
                    )
            else:
                if pattern.food_status.can_transition_to(PatternStatus.ERROR):
                    pattern.transition_food_to(PatternStatus.ERROR, error_msg=error_msg)
                else:
                    logger.warning(
                        f"Cannot transition food status from {pattern.food_status.value} to ERROR, skipping state change"
                    )

        # Refresh both tables
        self.refresh_both_tables()

    async def _handle_create_checkbox_click(self, row_index: int, is_unit: bool) -> None:
        """Handle clicking the Create checkbox to toggle QUEUED status."""
        if row_index >= len(self.patterns):
            logger.warning(f"Invalid row index: {row_index}")
            return

        pattern = self.patterns[row_index]
        from mealie_parser.models import PatternStatus

        # Get current status for the appropriate type (unit or food)
        current_status = pattern.unit_status if is_unit else pattern.food_status

        # Only allow checkbox clicks for UNMATCHED or QUEUED patterns
        if current_status == PatternStatus.UNMATCHED:
            # Transition to QUEUED
            if is_unit:
                pattern.transition_unit_to(PatternStatus.QUEUED)
            else:
                pattern.transition_food_to(PatternStatus.QUEUED)
            logger.info(f"Pattern '{pattern.pattern_text}' marked as QUEUED")
            self.refresh_table_row(row_index, pattern, is_unit)
            # Update toggle button label to reflect new state
            button_id = "toggle-unit" if is_unit else "toggle-food"
            self._update_toggle_button_label(button_id)
            self.notify(
                f"Pattern '{pattern.pattern_text}' ready to create",
                severity="information",
                timeout=2,
            )

        elif current_status == PatternStatus.QUEUED:
            # Toggle back to UNMATCHED
            if is_unit:
                pattern.transition_unit_to(PatternStatus.UNMATCHED)
            else:
                pattern.transition_food_to(PatternStatus.UNMATCHED)
            logger.info(f"Pattern '{pattern.pattern_text}' unmarked from QUEUED")
            self.refresh_table_row(row_index, pattern, is_unit)
            # Update toggle button label to reflect new state
            button_id = "toggle-unit" if is_unit else "toggle-food"
            self._update_toggle_button_label(button_id)
            self.notify(
                f"Pattern '{pattern.pattern_text}' unmarked",
                severity="information",
                timeout=2,
            )

    def action_select_pattern(self) -> None:
        """Start pattern selection in a worker."""
        self.run_worker(self._select_pattern_worker(), exclusive=False)

    async def _select_pattern_worker(self) -> None:
        """Worker for handling pattern selection."""
        logger.debug("Pattern selection triggered")

        # Get currently active tab and table
        table, is_unit, _ = self.get_current_tab_info()

        # Get selected row
        if table.cursor_row is None:
            logger.debug("No pattern selected")
            return

        row_index = table.cursor_row
        if row_index >= len(self.patterns):
            logger.warning(f"Invalid row index: {row_index}")
            return

        pattern = self.patterns[row_index]

        # Skip if already processed or currently parsing
        from mealie_parser.models import PatternStatus

        # Check the specific status based on which tab we're on
        current_status = pattern.unit_status if is_unit else pattern.food_status
        if current_status in (PatternStatus.MATCHED, PatternStatus.PARSING):
            logger.debug(f"Pattern '{pattern.pattern_text}' already {current_status.value}")
            return

        await self.handle_pattern_selection(pattern, is_unit, row_index)

    def _handle_simple_action(self, action: str, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """Handle simple actions like skip or review_individual.

        Parameters
        ----------
        action : str
            Action to handle ("skip" or "review_individual")
        pattern : PatternGroup
            Pattern being processed
        is_unit : bool
            True for unit, False for food
        row_index : int
            Row index in table
        """
        from mealie_parser.models import PatternStatus

        if action == "review_individual":
            if is_unit:
                pattern.transition_unit_to(PatternStatus.PENDING)
            else:
                pattern.transition_food_to(PatternStatus.PENDING)
            self.refresh_table_row(row_index, pattern, is_unit)
            self.notify(
                "Individual review feature coming soon! "
                "This will allow you to process each ingredient in this pattern one-by-one.",
                severity="information",
                timeout=5,
            )
            logger.info(f"Review individual requested for pattern: {pattern.pattern_text} (feature pending)")

        elif action == "skip":
            if is_unit:
                pattern.transition_unit_to(PatternStatus.IGNORE)
            else:
                pattern.transition_food_to(PatternStatus.IGNORE)
            self.skipped_count += 1
            self.refresh_table_row(row_index, pattern, is_unit)
            logger.info(f"Skipped pattern: {pattern.pattern_text}")

    async def _show_action_modal(self, pattern: PatternGroup, is_unit: bool) -> str | None:
        """Show appropriate action modal for pattern.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to process
        is_unit : bool
            True for unit modal, False for food modal

        Returns
        -------
        str | None
            Action selected or None if cancelled
        """
        from mealie_parser.modals.batch_action_modal import BatchActionModal
        from mealie_parser.modals.food_modals import FoodActionModal

        if is_unit:
            return await self.app.push_screen_wait(
                BatchActionModal(
                    pattern_text=pattern.pattern_text,
                    ingredient_count=len(pattern.ingredient_ids),
                    recipe_count=len(pattern.recipe_ids),
                )
            )
        return await self.app.push_screen_wait(FoodActionModal(food_name=pattern.pattern_text))

    async def _handle_create_new_action(
        self, pattern: PatternGroup, is_unit: bool
    ) -> tuple[str | None, str | None, str | None]:
        """Handle create_new action to create unit or food.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to process
        is_unit : bool
            True for unit, False for food

        Returns
        -------
        tuple[str | None, str | None, str | None]
            (entity_id, entity_name, operation_type) or (None, None, None) if cancelled
        """
        from mealie_parser.api import create_food, create_unit
        from mealie_parser.modals.food_modals import CreateFoodModal
        from mealie_parser.modals.unit_modals import CreateUnitModal

        if is_unit:
            unit_details = await self.app.push_screen_wait(
                CreateUnitModal(unit_name=pattern.pattern_text, existing_units=self.known_units)
            )
            if unit_details is None:
                return None, None, None

            result = await create_unit(
                self.session,
                name=unit_details["name"],
                abbreviation=unit_details["abbreviation"],
                description=unit_details["description"],
            )
            logger.info(f"Created unit: {result['name']} (ID: {result['id']})")
            return result["id"], result["name"], "create_unit"

        food_details = await self.app.push_screen_wait(
            CreateFoodModal(food_name=pattern.pattern_text, existing_foods=self.known_foods)
        )
        if food_details is None:
            return None, None, None

        result = await create_food(self.session, name=food_details["name"], description=food_details["description"])
        logger.info(f"Created food: {result['name']} (ID: {result['id']})")
        return result["id"], result["name"], "create_food"

    async def _handle_add_alias_action(
        self, pattern: PatternGroup, is_unit: bool
    ) -> tuple[str | None, str | None, str | None]:
        """Handle add_alias action to add alias to existing food.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to process
        is_unit : bool
            True for unit (not implemented), False for food

        Returns
        -------
        tuple[str | None, str | None, str | None]
            (entity_id, entity_name, operation_type) or (None, None, None) if cancelled/not implemented
        """
        from mealie_parser.modals.food_modals import SelectFoodModal

        if is_unit:
            logger.warning("Add alias for units not yet implemented")
            return None, None, None

        food_selection = await self.app.push_screen_wait(
            SelectFoodModal(foods=self.known_foods, suggestion=pattern.pattern_text)
        )
        if food_selection is None:
            return None, None, None

        selected_food = food_selection["food"]
        logger.info(f"Will add alias '{pattern.pattern_text}' to food '{selected_food['name']}'")
        return selected_food["id"], selected_food["name"], "add_food_alias"

    async def _complete_batch_operation(
        self,
        pattern: PatternGroup,
        entity_id: str,
        entity_name: str,
        operation_type: str,
        is_unit: bool,
        row_index: int,
    ) -> None:
        """Complete batch operation with preview and execution.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to process
        entity_id : str
            ID of created/selected entity
        entity_name : str
            Name of entity
        operation_type : str
            Operation type string
        is_unit : bool
            True for unit, False for food
        row_index : int
            Row index in table
        """
        from mealie_parser.models import PatternStatus
        from mealie_parser.screens.batch_preview import BatchPreviewScreen

        # Fetch affected ingredients
        affected_ingredients = await self.fetch_affected_ingredients(pattern)

        if not affected_ingredients:
            logger.warning(f"No ingredients found for pattern '{pattern.pattern_text}'")
            if is_unit:
                pattern.transition_unit_to(PatternStatus.PENDING)
            else:
                pattern.transition_food_to(PatternStatus.PENDING)
            self.refresh_table_row(row_index, pattern, is_unit)
            return

        # Show batch preview
        batch_result = await self.app.push_screen_wait(
            BatchPreviewScreen(
                operation_type=operation_type,
                pattern=pattern,
                affected_ingredients=affected_ingredients,
                unit_or_food_id=entity_id,
                session=self.session,
                unit_or_food_name=entity_name,
            )
        )

        # Handle cancellation
        if batch_result.get("cancelled"):
            logger.info(f"User cancelled batch operation for pattern '{pattern.pattern_text}'")
            if is_unit:
                pattern.transition_unit_to(PatternStatus.PENDING)
            else:
                pattern.transition_food_to(PatternStatus.PENDING)
            self.refresh_table_row(row_index, pattern, is_unit)
            return

        # Process results
        succeeded = batch_result.get("succeeded", 0)
        failed = batch_result.get("failed", 0)
        errors = batch_result.get("errors", [])

        if failed > 0:
            logger.warning(f"Batch operation completed with errors: {succeeded} succeeded, {failed} failed")
            for error in errors:
                logger.warning(f"  - {error}")

        # Refresh cache if needed
        if not is_unit and succeeded > 0:
            await self.refresh_food_cache()

        # Mark as completed
        if is_unit:
            pattern.transition_unit_to(PatternStatus.MATCHED)
        else:
            pattern.transition_food_to(PatternStatus.MATCHED)
        self.processed_count += 1
        self.refresh_table_row(row_index, pattern, is_unit)

        # Save session state
        self.session_state.add_processed_pattern(pattern.pattern_text)
        self._save_session_state()

        logger.info(f"Completed pattern '{pattern.pattern_text}': {succeeded} succeeded, {failed} failed")

    async def _handle_entity_action(self, action: str, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """Handle entity creation or alias actions.

        Parameters
        ----------
        action : str
            Action to handle ("create_new" or "add_alias")
        pattern : PatternGroup
            Pattern being processed
        is_unit : bool
            True for unit, False for food
        row_index : int
            Row index in table
        """
        from mealie_parser.models import PatternStatus

        try:
            if action == "create_new":
                entity_id, entity_name, operation_type = await self._handle_create_new_action(pattern, is_unit)
            elif action == "add_alias":
                entity_id, entity_name, operation_type = await self._handle_add_alias_action(pattern, is_unit)
            else:
                return

            # Handle cancellation or not implemented
            if entity_id is None:
                if is_unit:
                    pattern.transition_unit_to(PatternStatus.PENDING)
                else:
                    pattern.transition_food_to(PatternStatus.PENDING)
                self.refresh_table_row(row_index, pattern, is_unit)
                return

            # Complete the batch operation
            await self._complete_batch_operation(pattern, entity_id, entity_name, operation_type, is_unit, row_index)

        except Exception as e:
            logger.error(f"Error processing pattern '{pattern.pattern_text}': {e}", exc_info=True)
            if is_unit:
                pattern.transition_unit_to(PatternStatus.PENDING)
            else:
                pattern.transition_food_to(PatternStatus.PENDING)
            self.refresh_table_row(row_index, pattern, is_unit)

    async def handle_pattern_selection(self, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """Handle the complete pattern selection workflow.

        Parameters
        ----------
        pattern : PatternGroup
            The selected pattern to process
        is_unit : bool
            True if processing unit pattern, False for food pattern
        row_index : int
            Index of the pattern in the table
        """
        from mealie_parser.models import PatternStatus

        current_status = pattern.unit_status if is_unit else pattern.food_status
        logger.info(f"Processing pattern: '{pattern.pattern_text}' (unit={is_unit}, status={current_status.value})")

        # Handle PENDING patterns
        if current_status == PatternStatus.PENDING:
            await self.handle_pending_pattern(pattern, is_unit, row_index)
            return

        # Handle UNMATCHED patterns
        if current_status == PatternStatus.UNMATCHED:
            await self.handle_unmatched_pattern(pattern, is_unit, row_index)
            return

        # Show action modal
        action = await self._show_action_modal(pattern, is_unit)

        if action is None:
            logger.debug(f"User cancelled action for pattern: {pattern.pattern_text}")
            return

        # Handle simple actions
        if action in ("review_individual", "skip"):
            self._handle_simple_action(action, pattern, is_unit, row_index)
            return

        # Handle create_new or add_alias actions
        await self._handle_entity_action(action, pattern, is_unit, row_index)

    async def refresh_food_cache(self) -> None:
        """
        Refresh food cache after food creation or alias addition.

        This ensures that newly created foods or aliases are immediately available
        for the next pattern processing, preventing duplicates.
        """
        try:
            logger.debug("Refreshing food cache...")
            self.known_foods = await get_foods_full(self.session)
            logger.info(f"Food cache refreshed: {len(self.known_foods)} foods loaded")
        except Exception as e:
            logger.warning(f"Failed to refresh food cache: {e}", exc_info=True)
            # Don't abort - continue with stale cache

    async def fetch_affected_ingredients(self, pattern: PatternGroup) -> list[dict[str, Any]]:
        """
        Fetch full ingredient objects for affected ingredients.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern containing ingredient IDs to fetch

        Returns
        -------
        list[dict]
            List of full ingredient objects with recipe names
        """
        ingredients = []

        # Group ingredient IDs by recipe ID
        recipe_ingredient_map: dict[str, list[str]] = {}
        for recipe_id in pattern.recipe_ids:
            recipe_ingredient_map[recipe_id] = []

        # Find matching unparsed recipes and extract ingredients
        for recipe in self.unparsed_recipes:
            recipe_id = recipe.get("id")
            if recipe_id not in pattern.recipe_ids:
                continue

            # Fetch full recipe details to get ingredients
            try:
                recipe_details = await get_recipe_details(self.session, recipe["slug"])
                recipe_ingredients = recipe_details.get("recipeIngredient", [])

                for ing in recipe_ingredients:
                    if ing.get("id") in pattern.ingredient_ids:
                        # Add recipe name to ingredient for display
                        ing["recipeName"] = recipe.get("name", "Unknown")
                        ing["recipeId"] = recipe_id
                        ingredients.append(ing)

            except Exception as e:
                logger.error(
                    f"Error fetching recipe details for '{recipe.get('name')}': {e}",
                    exc_info=True,
                )

        logger.debug(f"Fetched {len(ingredients)} ingredient objects for pattern '{pattern.pattern_text}'")
        return ingredients

    async def handle_pending_pattern(self, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """
        Handle PENDING pattern selection - show parse config modal for single item.

        Parameters
        ----------
        pattern : PatternGroup
            The PENDING pattern to parse
        is_unit : bool
            True if processing from unit table, False from food table
        row_index : int
            Index of the pattern in the table
        """
        from mealie_parser.api import parse_ingredients
        from mealie_parser.modals.parse_config_modal import ParseConfigModal

        logger.info(f"Opening ParseConfigModal for single pattern: '{pattern.pattern_text}'")

        # Show parse config modal in single-item mode
        parse_config = await self.app.push_screen_wait(
            ParseConfigModal(single_item=True, item_name=pattern.pattern_text)
        )

        if parse_config is None:
            # User cancelled
            logger.debug(f"User cancelled parse for pattern: {pattern.pattern_text}")
            return

        # Extract parse method
        from mealie_parser.models import PatternStatus

        method = parse_config.get("method", "nlp")
        logger.info(f"Parsing single pattern '{pattern.pattern_text}' with method: {method}")

        # Update pattern status to PARSING
        if is_unit:
            pattern.transition_unit_to(PatternStatus.PARSING)
        else:
            pattern.transition_food_to(PatternStatus.PARSING)
        self.refresh_table_row(row_index, pattern, is_unit)

        try:
            # Parse the single pattern
            parse_result = await parse_ingredients(self.session, [pattern.pattern_text], parser=method)

            if not parse_result or len(parse_result) == 0:
                # Parse failed
                from mealie_parser.models import PatternStatus

                if is_unit:
                    pattern.transition_unit_to(PatternStatus.ERROR, error_msg="Parser returned empty result")
                else:
                    pattern.transition_food_to(PatternStatus.ERROR, error_msg="Parser returned empty result")
                self.refresh_table_row(row_index, pattern, is_unit)
                self.notify(
                    f"Failed to parse '{pattern.pattern_text}': empty result",
                    severity="error",
                    timeout=5,
                )
                logger.error(f"Parse returned empty result for pattern: {pattern.pattern_text}")
                return

            # Extract parsed data and update pattern using utility function
            from mealie_parser.services.parse_result_processor import (
                update_pattern_from_parse_result,
            )

            parsed = parse_result[0]
            update_pattern_from_parse_result(pattern, parsed, self.known_units, self.known_foods)

            # Determine notification based on which tab is active
            from mealie_parser.services.parse_result_processor import (
                check_food_match,
                check_unit_match,
            )

            if is_unit:
                matched = check_unit_match(pattern.parsed_unit, self.known_units)
            else:
                matched = check_food_match(pattern.parsed_food, self.known_foods)

            if matched:
                logger.info(f"Pattern '{pattern.pattern_text}' matched successfully")
                self.notify(
                    f"Parsed '{pattern.pattern_text}' → matched!",
                    severity="information",
                    timeout=3,
                )
            else:
                logger.info(f"Pattern '{pattern.pattern_text}' parsed but unmatched")
                self.notify(
                    f"Parsed '{pattern.pattern_text}' but no match found",
                    severity="warning",
                    timeout=3,
                )

            # Refresh BOTH tables to show updated parse results
            logger.info(f"Calling refresh_both_tables for pattern '{pattern.pattern_text}'")
            logger.info(
                f"Before refresh - unit_status: {pattern.unit_status.value}, food_status: {pattern.food_status.value}, parsed_unit: '{pattern.parsed_unit}', parsed_food: '{pattern.parsed_food}'"
            )
            self.refresh_both_tables()

            # Force table refresh to ensure UI updates
            unit_table = self.query_one("#unit-table", DataTable)
            food_table = self.query_one("#food-table", DataTable)
            unit_table.refresh()
            food_table.refresh()

            logger.info("After refresh_both_tables completed")

        except Exception as e:
            from mealie_parser.models import PatternStatus

            logger.error(f"Error parsing pattern '{pattern.pattern_text}': {e}", exc_info=True)
            if is_unit:
                pattern.transition_unit_to(PatternStatus.ERROR, error_msg=str(e))
            else:
                pattern.transition_food_to(PatternStatus.ERROR, error_msg=str(e))
            self.refresh_table_row(row_index, pattern, is_unit)
            self.notify(
                f"Error parsing '{pattern.pattern_text}': {str(e)}",
                severity="error",
                timeout=5,
            )

    async def _show_unmatched_modal(self, pattern: PatternGroup, is_unit: bool) -> dict | None:
        """Show appropriate unmatched modal for unit or food.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to process
        is_unit : bool
            True for unit modal, False for food modal

        Returns
        -------
        dict | None
            Modal result or None if cancelled
        """
        from mealie_parser.modals.unmatched_food_modal import UnmatchedFoodModal
        from mealie_parser.modals.unmatched_unit_modal import UnmatchedUnitModal

        logger.info(f"Opening Unmatched{'Unit' if is_unit else 'Food'}Modal for pattern: '{pattern.pattern_text}'")

        if is_unit:
            return await self.app.push_screen_wait(
                UnmatchedUnitModal(
                    pattern=pattern,
                    units=self.known_units,
                    parse_method="nlp",
                )
            )
        return await self.app.push_screen_wait(
            UnmatchedFoodModal(
                pattern=pattern,
                foods=self.known_foods,
                parse_method="nlp",
            )
        )

    async def _handle_reparse_action(self, pattern: PatternGroup, result: dict, is_unit: bool, row_index: int) -> None:
        """Handle reparse action from unmatched modal.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to reparse
        result : dict
            Modal result containing parse method
        is_unit : bool
            True if from unit table, False if from food table
        row_index : int
            Row index in table
        """
        from mealie_parser.api import parse_ingredients
        from mealie_parser.services.parse_result_processor import (
            extract_confidence_scores,
            extract_parsed_food,
            extract_parsed_unit,
        )

        method = result.get("method", "nlp")
        logger.info(f"Re-parsing pattern '{pattern.pattern_text}' with method: {method}")

        parse_result = await parse_ingredients(self.session, [pattern.pattern_text], parser=method)

        if parse_result and len(parse_result) > 0:
            parsed = parse_result[0]
            ingredient = parsed.get("ingredient", {})

            # Extract parsed unit/food
            pattern.parsed_unit = extract_parsed_unit(ingredient)
            pattern.parsed_food = extract_parsed_food(ingredient)

            # Extract confidence scores
            unit_conf, food_conf = extract_confidence_scores(parsed)
            pattern.unit_confidence = unit_conf
            pattern.food_confidence = food_conf

            # Refresh both tables
            self.refresh_both_tables()
            logger.info(
                f"Re-parsed pattern: unit='{pattern.parsed_unit}' (conf: {pattern.unit_confidence:.2f}), food='{pattern.parsed_food}' (conf: {pattern.food_confidence:.2f})"
            )

            # Re-open modal with new parse results
            await self.handle_unmatched_pattern(pattern, is_unit, row_index)
        else:
            self.notify("Re-parse failed: empty result", severity="error", timeout=3)

    async def _handle_unit_operation(self, pattern: PatternGroup, operation: str, result: dict) -> None:
        """Handle unit-related operations from unmatched modal.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern being processed
        operation : str
            Operation type: "create_unit", "add_unit_alias", "create_unit_with_alias"
        result : dict
            Modal result with operation details
        """
        from mealie_parser.api import add_unit_alias, create_unit, get_units_full
        from mealie_parser.models import PatternStatus

        unit_name = result.get("unit_name")

        if operation == "create_unit":
            created_unit = await create_unit(
                self.session,
                name=unit_name,
                abbreviation=unit_name[:3],
                description=f"Created from pattern: {pattern.pattern_text}",
            )
            logger.info(f"Created unit: {created_unit['name']} (ID: {created_unit['id']})")
            self.notify(f"Created unit: {unit_name}", severity="information", timeout=3)

        elif operation == "add_unit_alias":
            unit_id = result.get("unit_id")
            alias = result.get("alias")
            await add_unit_alias(self.session, unit_id, alias)
            logger.info(f"Added alias '{alias}' to unit ID: {unit_id}")
            self.notify(f"Added alias: {alias}", severity="information", timeout=3)

        elif operation == "create_unit_with_alias":
            alias = result.get("alias")
            created_unit = await create_unit(
                self.session,
                name=unit_name,
                abbreviation=unit_name[:3],
                description=f"Created from pattern: {pattern.pattern_text}",
            )
            logger.info(f"Created unit: {created_unit['name']} (ID: {created_unit['id']})")

            if alias:
                await add_unit_alias(self.session, created_unit["id"], alias)
                logger.info(f"Added alias '{alias}' to new unit")

            self.notify(
                f"Created unit: {unit_name}" + (f" with alias: {alias}" if alias else ""),
                severity="information",
                timeout=3,
            )

        # Refresh units cache and mark pattern as matched
        self.known_units = await get_units_full(self.session)
        pattern.transition_unit_to(PatternStatus.MATCHED)
        self.refresh_both_tables()

    async def _handle_food_operation(self, pattern: PatternGroup, operation: str, result: dict) -> None:
        """Handle food-related operations from unmatched modal.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern being processed
        operation : str
            Operation type: "create_food", "add_food_alias", "create_food_with_alias"
        result : dict
            Modal result with operation details
        """
        from mealie_parser.api import add_food_alias, create_food
        from mealie_parser.models import PatternStatus

        food_name = result.get("food_name")

        if operation == "create_food":
            created_food = await create_food(
                self.session,
                name=food_name,
                description=f"Created from pattern: {pattern.pattern_text}",
            )
            logger.info(f"Created food: {created_food['name']} (ID: {created_food['id']})")
            self.notify(f"Created food: {food_name}", severity="information", timeout=3)

        elif operation == "add_food_alias":
            food_id = result.get("food_id")
            alias = result.get("alias")
            await add_food_alias(self.session, food_id, alias)
            logger.info(f"Added alias '{alias}' to food ID: {food_id}")
            self.notify(f"Added alias: {alias}", severity="information", timeout=3)

        elif operation == "create_food_with_alias":
            alias = result.get("alias")
            created_food = await create_food(
                self.session,
                name=food_name,
                description=f"Created from pattern: {pattern.pattern_text}",
            )
            logger.info(f"Created food: {created_food['name']} (ID: {created_food['id']})")

            if alias:
                await add_food_alias(self.session, created_food["id"], alias)
                logger.info(f"Added alias '{alias}' to new food")

            self.notify(
                f"Created food: {food_name}" + (f" with alias: {alias}" if alias else ""),
                severity="information",
                timeout=3,
            )

        # Refresh foods cache and mark pattern as matched
        await self.refresh_food_cache()
        pattern.transition_food_to(PatternStatus.MATCHED)
        self.refresh_both_tables()

    async def handle_unmatched_pattern(self, pattern: PatternGroup, is_unit: bool, row_index: int) -> None:
        """Handle UNMATCHED pattern selection with appropriate modal (unit or food).

        Parameters
        ----------
        pattern : PatternGroup
            The UNMATCHED pattern to process
        is_unit : bool
            True if processing from unit table, False from food table
        row_index : int
            Index of the pattern in the table
        """
        result = await self._show_unmatched_modal(pattern, is_unit)

        if result is None:
            logger.debug(f"User cancelled unmatched modal for pattern: {pattern.pattern_text}")
            return

        action = result.get("action")
        logger.info(f"Unmatched modal result: {result}")

        try:
            if action == "reparse":
                await self._handle_reparse_action(pattern, result, is_unit, row_index)
                return

            if action == "unit":
                operation = result.get("operation")
                await self._handle_unit_operation(pattern, operation, result)

            elif action == "food":
                operation = result.get("operation")
                await self._handle_food_operation(pattern, operation, result)

        except Exception as e:
            logger.error(
                f"Error handling unmatched pattern '{pattern.pattern_text}': {e}",
                exc_info=True,
            )
            self.notify(f"Error: {str(e)}", severity="error", timeout=5)

    def refresh_table_row(self, pattern_index: int, pattern: PatternGroup, is_unit: bool) -> None:
        """
        Refresh a specific DataTable row with updated pattern data.

        Uses unit_status for unit table and food_status for food table.

        Parameters
        ----------
        pattern_index : int
            Index of the pattern in self.patterns (NOT display row index)
        pattern : PatternGroup
            Updated pattern data
        is_unit : bool
            True if updating unit table, False for food table
        """
        # Delegate to table manager
        table_manager = self.unit_table_manager if is_unit else self.food_table_manager
        table_id = "#unit-table" if is_unit else "#food-table"
        table = self.query_one(table_id, DataTable)

        table_manager.update_pattern_row(table, pattern_index, pattern)

    def refresh_both_tables(self) -> None:
        """
        Refresh both Unit and Food tables with current pattern data.

        Uses unit_status for unit table and food_status for food table.
        This ensures both tables stay synchronized when patterns are updated
        (e.g., after parsing completes).
        """
        # Use the specialized refresh methods that respect hide toggles
        self.refresh_unit_table()
        self.refresh_food_table()
        logger.debug("Refreshed both Unit and Food tables with independent statuses")

    def action_skip_pattern(self) -> None:
        """
        Mark currently selected pattern as skipped.

        Keyboard shortcut: 's'
        """
        # Get currently active tab and table
        table, is_unit, _ = self.get_current_tab_info()

        # Get selected row
        if table.cursor_row is None:
            logger.debug("No pattern selected for skip")
            return

        row_index = table.cursor_row
        if row_index >= len(self.patterns):
            logger.warning(f"Invalid row index: {row_index}")
            return

        pattern = self.patterns[row_index]

        # Skip if already skipped or completed
        from mealie_parser.models import PatternStatus

        current_status = pattern.unit_status if is_unit else pattern.food_status
        if current_status in (PatternStatus.IGNORE, PatternStatus.MATCHED):
            logger.debug(f"Pattern '{pattern.pattern_text}' already {current_status.value}")
            return

        # Mark as skipped
        if is_unit:
            pattern.transition_unit_to(PatternStatus.IGNORE)
        else:
            pattern.transition_food_to(PatternStatus.IGNORE)
        self.skipped_count += 1
        self.refresh_table_row(row_index, pattern, is_unit)

        # Save session state
        self.session_state.add_skipped_pattern(pattern.pattern_text)
        self._save_session_state()

        logger.info(f"Skipped pattern: '{pattern.pattern_text}'")

        # Move to next pending pattern
        self.move_to_next_pending_pattern(table, self.patterns)

    def action_undo_skip(self) -> None:
        """
        Undo skip status for currently selected pattern.

        Keyboard shortcut: 'u'
        """
        # Get currently active tab and table
        table, is_unit, _ = self.get_current_tab_info()

        # Get selected row
        if table.cursor_row is None:
            logger.debug("No pattern selected for undo")
            return

        row_index = table.cursor_row
        if row_index >= len(self.patterns):
            logger.warning(f"Invalid row index: {row_index}")
            return

        pattern = self.patterns[row_index]

        # Only undo if currently skipped
        from mealie_parser.models import PatternStatus

        current_status = pattern.unit_status if is_unit else pattern.food_status
        if current_status != PatternStatus.IGNORE:
            logger.debug(f"Pattern '{pattern.pattern_text}' not skipped (status: {current_status.value})")
            self.notify("Pattern not skipped", severity="warning", timeout=2)
            return

        # Revert to pending
        if is_unit:
            pattern.transition_unit_to(PatternStatus.PENDING)
        else:
            pattern.transition_food_to(PatternStatus.PENDING)
        self.skipped_count -= 1
        self.refresh_table_row(row_index, pattern, is_unit)
        logger.info(f"Undo skip for pattern: '{pattern.pattern_text}'")

    def move_to_next_pending_pattern(self, table: DataTable, patterns: list[PatternGroup]) -> None:
        """
        Move table cursor to next pending pattern.

        Parameters
        ----------
        table : DataTable
            The data table to navigate
        patterns : list[PatternGroup]
            List of patterns to search
        """
        current_row = table.cursor_row
        if current_row is None:
            return

        # Search for next pending pattern
        from mealie_parser.models import PatternStatus

        # Determine which status to check based on which table we're in
        tabbed_content = self.query_one(TabbedContent)
        is_unit = tabbed_content.active == "units"

        for i in range(current_row + 1, len(patterns)):
            current_status = patterns[i].unit_status if is_unit else patterns[i].food_status
            if current_status == PatternStatus.PENDING:
                table.cursor_row = i
                logger.debug(f"Moved to next pending pattern at row {i}")
                return

        # No pending patterns after current, stay on current
        logger.debug("No more pending patterns after current")

    def action_start_parsing(self) -> None:
        """Open parse config modal and start parsing."""
        self.run_worker(self._start_parsing_worker(), exclusive=True)

    async def _start_parsing_worker(self) -> None:
        """Worker for starting parsing with modal."""
        # Show parse config modal with parsing_started flag
        config = await self.app.push_screen_wait(ParseConfigModal(parsing_started=self.parsing_started))

        if config is None:
            logger.info("Parse config cancelled")
            return

        # Start parsing with config
        quantity = config["quantity"]
        method = config["method"]
        parse_filter = config.get("filter", "all")  # Get filter from config

        logger.info(f"Starting batch parse: quantity={quantity}, method={method}, filter={parse_filter}")

        # Determine which table to work with based on active tab
        tabbed_content = self.query_one(TabbedContent)
        active_tab = tabbed_content.active

        if active_tab == "units":
            table_manager = self.unit_table_manager
            table_id = "#unit-table"
        else:
            table_manager = self.food_table_manager
            table_id = "#food-table"

        # Use the shared patterns list
        all_patterns = self.patterns

        # Determine which patterns to parse based on filter
        from mealie_parser.models import PatternStatus

        is_unit = active_tab == "units"

        if self.parsing_started:
            logger.info(f"Parsing with filter: {parse_filter}")
            # Count patterns by status for debugging
            status_counts = {}
            for p in all_patterns:
                status = (p.unit_status if is_unit else p.food_status).value
                status_counts[status] = status_counts.get(status, 0) + 1
            logger.info(f"Pattern status counts: {status_counts}")

            if parse_filter == "pending":
                # Only unparsed patterns (pending status)
                indices_to_parse = [
                    i
                    for i, p in enumerate(all_patterns)
                    if (p.unit_status if is_unit else p.food_status) == PatternStatus.PENDING
                ]
                logger.info(f"Filter 'pending': found {len(indices_to_parse)} patterns to parse")
            elif parse_filter == "pending_unmatched":
                # Pending + unmatched (parsed but no match found)
                indices_to_parse = [
                    i
                    for i, p in enumerate(all_patterns)
                    if (p.unit_status if is_unit else p.food_status) in (PatternStatus.PENDING, PatternStatus.UNMATCHED)
                ]
                logger.info(f"Filter 'pending_unmatched': found {len(indices_to_parse)} patterns to parse")
            else:  # "all"
                # Re-parse everything
                indices_to_parse = list(range(len(all_patterns)))
                logger.info(f"Filter 'all': will re-parse all {len(indices_to_parse)} patterns")
        else:
            # First run - parse from beginning
            indices_to_parse = list(range(len(all_patterns)))
            logger.info(f"First run: parsing first {len(indices_to_parse)} patterns")

        # Apply quantity limit
        if quantity != -1 and len(indices_to_parse) > quantity:
            indices_to_parse = indices_to_parse[:quantity]

        parse_count = len(indices_to_parse)

        if parse_count == 0:
            logger.warning("No patterns to parse with current filter")
            return

        # Extract concurrency setting
        concurrency = config.get("concurrency", 4)
        logger.info(f"Using concurrency level: {concurrency}")

        # Start parsing
        await self.parse_patterns_batch_filtered(
            all_patterns, indices_to_parse, table_manager, table_id, method, concurrency
        )

    def _should_skip_pattern(self, pattern: PatternGroup, is_unit_table: bool) -> bool:
        """Check if pattern should be skipped based on current status.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to check
        is_unit_table : bool
            True if checking unit status, False for food status

        Returns
        -------
        bool
            True if pattern should be skipped
        """
        from mealie_parser.models import PatternStatus

        current_status = pattern.unit_status if is_unit_table else pattern.food_status

        if current_status in (PatternStatus.MATCHED, PatternStatus.IGNORE):
            logger.debug(f"Skipping pattern '{pattern.pattern_text}' - already {current_status.value}")
            return True
        return False

    def _transition_to_parsing(self, pattern: PatternGroup, is_unit_table: bool) -> None:
        """Transition pattern to PARSING state if valid.

        Parameters
        ----------
        pattern : PatternGroup
            Pattern to transition
        is_unit_table : bool
            True for unit transition, False for food transition
        """
        from mealie_parser.models import PatternStatus

        current_status = pattern.unit_status if is_unit_table else pattern.food_status

        # Transition to PARSING state only if valid transition
        if current_status in (PatternStatus.PENDING, PatternStatus.UNMATCHED, PatternStatus.ERROR):
            if is_unit_table:
                if pattern.unit_status != PatternStatus.PARSING:
                    pattern.transition_unit_to(PatternStatus.PARSING)
            else:
                if pattern.food_status != PatternStatus.PARSING:
                    pattern.transition_food_to(PatternStatus.PARSING)

    def _update_current_table_cells(
        self,
        table: DataTable,
        row_key: Any,
        status_col: Any,
        parsed_col: Any,
        is_unit_table: bool,
        parsed_unit_name: str,
        parsed_food_name: str,
        unit_matched: bool,
        food_matched: bool,
    ) -> None:
        """Update cells in the currently visible table.

        Parameters
        ----------
        table : DataTable
            Table to update
        row_key : Any
            Row key for the pattern
        status_col : Any
            Status column key
        parsed_col : Any
            Parsed unit/food column key
        is_unit_table : bool
            True if unit table, False if food table
        parsed_unit_name : str
            Parsed unit name
        parsed_food_name : str
            Parsed food name
        unit_matched : bool
            Whether unit matched
        food_matched : bool
            Whether food matched
        """
        from textual.widgets._data_table import CellDoesNotExist

        try:
            if is_unit_table:
                table.update_cell(row_key, parsed_col, parsed_unit_name)
                status_text = "[green]✓ matched[/green]" if unit_matched else "[yellow]⚠ unmatched[/yellow]"
            else:
                table.update_cell(row_key, parsed_col, parsed_food_name)
                status_text = "[green]✓ matched[/green]" if food_matched else "[yellow]⚠ unmatched[/yellow]"

            table.update_cell(row_key, status_col, status_text)
        except CellDoesNotExist:
            # Table was refreshed, row no longer exists - silently ignore
            logger.debug(f"Cell no longer exists for row_key={row_key}, table was likely refreshed")
            pass

    def _update_background_table(
        self,
        pattern_index: int,
        is_unit_table: bool,
        parsed_unit_name: str,
        parsed_food_name: str,
        unit_matched: bool,
        food_matched: bool,
    ) -> None:
        """Update the non-visible table in background.

        Parameters
        ----------
        pattern_index : int
            Index of pattern
        is_unit_table : bool
            True if viewing unit table (so update food table), False otherwise
        parsed_unit_name : str
            Parsed unit name
        parsed_food_name : str
            Parsed food name
        unit_matched : bool
            Whether unit matched
        food_matched : bool
            Whether food matched
        """
        from textual.widgets._data_table import CellDoesNotExist

        try:
            if is_unit_table:
                # We're viewing unit table, update food table in background
                food_table = self.query_one("#food-table", DataTable)
                food_row_key = self.food_table_manager.row_keys[pattern_index]
                food_status_text = "[green]✓ matched[/green]" if food_matched else "[yellow]⚠ unmatched[/yellow]"
                food_table.update_cell(food_row_key, self.food_status_col, food_status_text)
                food_table.update_cell(food_row_key, self.food_parsed_food_col, parsed_food_name)
            else:
                # We're viewing food table, update unit table in background
                unit_table = self.query_one("#unit-table", DataTable)
                unit_row_key = self.unit_table_manager.row_keys[pattern_index]
                unit_status_text = "[green]✓ matched[/green]" if unit_matched else "[yellow]⚠ unmatched[/yellow]"
                unit_table.update_cell(unit_row_key, self.unit_status_col, unit_status_text)
                unit_table.update_cell(unit_row_key, self.unit_parsed_unit_col, parsed_unit_name)
        except CellDoesNotExist:
            # Table was refreshed, row no longer exists - silently ignore
            logger.debug(f"Background table cell no longer exists for pattern_index={pattern_index}")
            pass

    async def _parse_single_pattern_for_batch(
        self,
        pattern_index: int,
        patterns: list[PatternGroup],
        table: DataTable,
        table_manager: PatternTableManager,
        status_col: Any,
        parsed_col: Any,
        is_unit_table: bool,
        method: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Parse a single pattern as part of batch processing.

        Parameters
        ----------
        pattern_index : int
            Index of pattern in patterns list
        patterns : list[PatternGroup]
            All patterns
        table : DataTable
            Current table widget
        table_manager : PatternTableManager
            Manager for table state
        status_col : Any
            Status column key
        parsed_col : Any
            Parsed unit/food column key
        is_unit_table : bool
            True if processing unit table, False for food table
        method : str
            Parsing method ("nlp", "brute", or "openai")
        semaphore : asyncio.Semaphore
            Concurrency limiter
        """
        async with semaphore:
            pattern = patterns[pattern_index]

            # Skip if already in terminal state
            if self._should_skip_pattern(pattern, is_unit_table):
                return

            # Transition to PARSING state
            self._transition_to_parsing(pattern, is_unit_table)

            # Update status to show parsing
            row_key = table_manager.row_keys[pattern_index]
            from textual.widgets._data_table import CellDoesNotExist

            from mealie_parser.models import PatternStatus

            try:
                table.update_cell(row_key, status_col, self.get_status_display(PatternStatus.PARSING))
            except CellDoesNotExist:
                # Table was refreshed, row no longer exists - skip this pattern
                logger.debug(f"Cell no longer exists for pattern_index={pattern_index}, skipping")
                return

            try:
                # Parse pattern text
                result = await parse_ingredients(self.session, [pattern.pattern_text], parser=method)
                logger.debug(f"Parser response for '{pattern.pattern_text}': {result}")

                if result and len(result) > 0:
                    # Use utility to update pattern from parse result
                    from mealie_parser.services.parse_result_processor import (
                        check_food_match,
                        check_unit_match,
                        update_pattern_from_parse_result,
                    )

                    parsed = result[0]
                    update_pattern_from_parse_result(pattern, parsed, self.known_units, self.known_foods)

                    # Get parsed values and match status
                    parsed_unit_name = pattern.parsed_unit
                    parsed_food_name = pattern.parsed_food
                    unit_matched = check_unit_match(parsed_unit_name, self.known_units)
                    food_matched = check_food_match(parsed_food_name, self.known_foods)

                    # Debug logging for food matching
                    if parsed_food_name and not food_matched:
                        logger.debug(f"  Sample known foods: {[f.get('name') for f in self.known_foods[:5]]}")
                        similar_foods = [
                            f.get("name")
                            for f in self.known_foods
                            if f.get("name", "").lower().startswith(parsed_food_name.lower()[0])
                        ][:5]
                        logger.debug(f"  Foods starting with '{parsed_food_name[0]}': {similar_foods}")

                    # Update current table (visible to user)
                    self._update_current_table_cells(
                        table,
                        row_key,
                        status_col,
                        parsed_col,
                        is_unit_table,
                        parsed_unit_name,
                        parsed_food_name,
                        unit_matched,
                        food_matched,
                    )

                    # Update background table
                    self._update_background_table(
                        pattern_index, is_unit_table, parsed_unit_name, parsed_food_name, unit_matched, food_matched
                    )

                else:
                    # Parser returned empty result
                    logger.warning(f"Parser returned empty result for '{pattern.pattern_text}'")
                    try:
                        table.update_cell(row_key, status_col, "[red]✗ error[/red]")
                    except CellDoesNotExist:
                        logger.debug(f"Cell no longer exists for row_key={row_key}, table was likely refreshed")
                        pass

                    if is_unit_table:
                        pattern.transition_unit_to(PatternStatus.ERROR, error_msg="Parser returned empty result")
                    else:
                        pattern.transition_food_to(PatternStatus.ERROR, error_msg="Parser returned empty result")

            except Exception as e:
                logger.error(f"Error parsing pattern '{pattern.pattern_text}': {e}", exc_info=True)
                try:
                    table.update_cell(row_key, status_col, "[red]✗ error[/red]")
                except CellDoesNotExist:
                    logger.debug(f"Cell no longer exists for row_key={row_key}, table was likely refreshed")
                    pass

                if is_unit_table:
                    pattern.transition_unit_to(PatternStatus.ERROR, error_msg=str(e))
                else:
                    pattern.transition_food_to(PatternStatus.ERROR, error_msg=str(e))

            # Small delay to allow UI updates
            await asyncio.sleep(0.05)

    async def parse_patterns_batch_filtered(
        self,
        patterns: list[PatternGroup],
        indices: list[int],
        table_manager: PatternTableManager,
        table_id: str,
        method: str,
        concurrency: int = 4,
    ) -> None:
        """
        Parse patterns at specified indices with progress tracking and concurrent processing.

        Parameters
        ----------
        patterns : list[PatternGroup]
            All patterns in the table
        indices : list[int]
            Indices of patterns to parse
        table_manager : PatternTableManager
            Table manager for table updates
        table_id : str
            Table ID ("#unit-table" or "#food-table")
        method : str
            Parsing method: "nlp", "brute", or "openai"
        concurrency : int
            Number of concurrent parsing requests (default: 4)
        """
        table = self.query_one(table_id, DataTable)

        # Get correct column keys based on table
        if table_id == "#unit-table":
            status_col = self.unit_status_col
            parsed_col = self.unit_parsed_unit_col
            is_unit_table = True
        else:
            status_col = self.food_status_col
            parsed_col = self.food_parsed_food_col
            is_unit_table = False

        count = len(indices)

        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        # Process all patterns concurrently with semaphore limiting concurrency
        logger.info(f"Starting concurrent parsing of {count} patterns with concurrency={concurrency}")
        await asyncio.gather(
            *[
                self._parse_single_pattern_for_batch(
                    pattern_index=i,
                    patterns=patterns,
                    table=table,
                    table_manager=table_manager,
                    status_col=status_col,
                    parsed_col=parsed_col,
                    is_unit_table=is_unit_table,
                    method=method,
                    semaphore=semaphore,
                )
                for i in indices
            ],
            return_exceptions=False,
        )

        # Mark that parsing has started (after completing batch)
        if not self.parsing_started and count > 0:
            self.parsing_started = True
            logger.info("Batch parsing completed, setting parsing_started=True")

        # Refresh both tables to ensure synchronization
        self.refresh_both_tables()

        logger.info(f"Batch parsing complete: {count} patterns processed")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-parsing":
            self.action_start_parsing()
        elif event.button.id == "data-management":
            self.action_data_management()
        elif event.button.id == "back-button":
            self.action_back()
        elif event.button.id == "toggle-food":
            self.action_toggle_food()
        elif event.button.id == "toggle-unit":
            self.action_toggle_unit()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Handle switch toggle events."""
        if event.switch.id == "hide-matched-food":
            self.hide_matched_foods = event.value
            logger.info(f"Toggle hide matched foods: {self.hide_matched_foods}")
        elif event.switch.id == "hide-matched-unit":
            self.hide_matched_units = event.value
            logger.info(f"Toggle hide matched units: {self.hide_matched_units}")

    def action_data_management(self) -> None:
        """Open the Data Management modal to view all units and foods."""
        logger.info("Opening Data Management modal")
        self.app.push_screen(DataManagementModal(units=self.known_units, foods=self.known_foods))

    def action_switch_tab(self) -> None:
        """Switch between Food and Unit tabs."""
        tabbed_content = self.query_one(TabbedContent)
        # Toggle between the two tabs
        if tabbed_content.active == "foods":
            tabbed_content.active = "units"
        else:
            tabbed_content.active = "foods"
        logger.debug(f"Switched to tab: {tabbed_content.active}")

    def action_back(self) -> None:
        """Return to previous screen."""
        logger.info("Returning from PatternGroupScreen")
        self.dismiss()

    def refresh_food_table(self) -> None:
        """Refresh food table applying matched filter if enabled."""
        food_table = self.query_one("#food-table", DataTable)
        self.food_table_manager.refresh_table(food_table, hide_matched=self.hide_matched_foods)

    def refresh_unit_table(self) -> None:
        """Refresh unit table applying matched filter if enabled."""
        unit_table = self.query_one("#unit-table", DataTable)
        self.unit_table_manager.refresh_table(unit_table, hide_matched=self.hide_matched_units)

    def action_toggle_food(self) -> None:
        """Toggle food pattern checkboxes based on current state.

        If all unmatched patterns are queued → Clear all (QUEUED → UNMATCHED)
        If less than all are queued → Select all (UNMATCHED → QUEUED)
        """
        from mealie_parser.models import PatternStatus

        # Count unmatched and queued patterns
        unmatched_count = sum(1 for p in self.patterns if p.food_status == PatternStatus.UNMATCHED)
        queued_count = sum(1 for p in self.patterns if p.food_status == PatternStatus.QUEUED)

        # If all unmatched patterns are queued, clear all
        if unmatched_count == 0 and queued_count > 0:
            count = 0
            for pattern in self.patterns:
                if pattern.food_status == PatternStatus.QUEUED:
                    pattern.transition_food_to(PatternStatus.UNMATCHED)
                    count += 1

            self.refresh_food_table()
            self._update_toggle_button_label("toggle-food")
            logger.info(f"Cleared {count} food patterns")
            self.notify(f"Cleared {count} food patterns", severity="information", timeout=2)
        else:
            # Otherwise, select all unmatched patterns
            count = 0
            for pattern in self.patterns:
                if pattern.food_status == PatternStatus.UNMATCHED:
                    pattern.transition_food_to(PatternStatus.QUEUED)
                    count += 1

            self.refresh_food_table()
            self._update_toggle_button_label("toggle-food")
            logger.info(f"Selected {count} food patterns for creation")
            self.notify(
                f"Selected {count} food patterns for creation",
                severity="information",
                timeout=2,
            )

    def action_toggle_unit(self) -> None:
        """Toggle unit pattern checkboxes based on current state.

        If all unmatched patterns are queued → Clear all (QUEUED → UNMATCHED)
        If less than all are queued → Select all (UNMATCHED → QUEUED)
        """
        from mealie_parser.models import PatternStatus

        # Count unmatched and queued patterns
        unmatched_count = sum(1 for p in self.patterns if p.unit_status == PatternStatus.UNMATCHED)
        queued_count = sum(1 for p in self.patterns if p.unit_status == PatternStatus.QUEUED)

        # If all unmatched patterns are queued, clear all
        if unmatched_count == 0 and queued_count > 0:
            count = 0
            for pattern in self.patterns:
                if pattern.unit_status == PatternStatus.QUEUED:
                    pattern.transition_unit_to(PatternStatus.UNMATCHED)
                    count += 1

            self.refresh_unit_table()
            self._update_toggle_button_label("toggle-unit")
            logger.info(f"Cleared {count} unit patterns")
            self.notify(f"Cleared {count} unit patterns", severity="information", timeout=2)
        else:
            # Otherwise, select all unmatched patterns
            count = 0
            for pattern in self.patterns:
                if pattern.unit_status == PatternStatus.UNMATCHED:
                    pattern.transition_unit_to(PatternStatus.QUEUED)
                    count += 1

            self.refresh_unit_table()
            self._update_toggle_button_label("toggle-unit")
            logger.info(f"Selected {count} unit patterns for creation")
            self.notify(
                f"Selected {count} unit patterns for creation",
                severity="information",
                timeout=2,
            )

    def _update_toggle_button_label(self, button_id: str) -> None:
        """Update the toggle button label based on current pattern states.

        Args:
            button_id: ID of the button to update ('toggle-food' or 'toggle-unit')
        """
        from mealie_parser.models import PatternStatus

        # Determine which status to check based on button ID
        is_food = button_id == "toggle-food"

        # Count unmatched patterns
        unmatched_count = sum(
            1 for p in self.patterns if (p.food_status if is_food else p.unit_status) == PatternStatus.UNMATCHED
        )

        # Update button label
        button = self.query_one(f"#{button_id}", Button)
        if unmatched_count == 0:
            button.label = "Clear All Unmatched"
        else:
            button.label = "Select All Unmatched"
