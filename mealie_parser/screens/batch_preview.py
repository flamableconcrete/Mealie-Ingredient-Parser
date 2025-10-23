"""Batch preview screen for confirming batch operations before execution."""

from typing import Any

import aiohttp
from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, ProgressBar, Static

from mealie_parser.models.pattern import PatternGroup


class BatchPreviewScreen(ModalScreen[dict[str, Any]]):
    """
    Modal screen for previewing and confirming batch operations.

    Shows affected ingredients, operation details, and executes batch API calls
    with progress tracking.

    Attributes
    ----------
    operation_type : str
        Type of operation: "create_unit", "create_food", "add_unit_alias", "add_food_alias"
    pattern : PatternGroup
        The pattern group being processed
    affected_ingredients : list[dict]
        Full ingredient objects that will be updated
    unit_or_food_id : str
        ID of the unit or food to assign/alias
    session : aiohttp.ClientSession
        Persistent HTTP session for API calls
    unit_or_food_name : str
        Name of the unit or food for display purposes
    show_progress : bool
        Reactive attribute controlling progress indicator visibility
    """

    CSS = """
    BatchPreviewScreen {
        align: center middle;
    }

    #dialog {
        width: 90%;
        max-width: 120;
        height: 90%;
        max-height: 40;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #header {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        height: auto;
    }

    #summary {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        height: auto;
    }

    #ingredients-table {
        height: 1fr;
        margin: 1 0;
    }

    #details {
        text-align: center;
        color: $text-muted;
        background: $boost;
        padding: 1;
        margin: 1 0;
        height: auto;
    }

    #progress-container {
        height: auto;
        margin: 1 0;
    }

    #progress-bar {
        height: 1;
        margin: 1 0;
    }

    #progress-status {
        text-align: center;
        height: auto;
    }

    #buttons {
        layout: horizontal;
        align: center middle;
        height: auto;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    show_progress = reactive(False)

    def __init__(
        self,
        operation_type: str,
        pattern: PatternGroup,
        affected_ingredients: list[dict],
        unit_or_food_id: str,
        session: aiohttp.ClientSession,
        unit_or_food_name: str = "",
    ):
        """
        Initialize batch preview screen.

        Parameters
        ----------
        operation_type : str
            Type of operation: "create_unit", "create_food", "add_unit_alias", "add_food_alias"
        pattern : PatternGroup
            The pattern group being processed
        affected_ingredients : list[dict]
            Full ingredient objects that will be updated
        unit_or_food_id : str
            ID of the unit or food to assign/alias
        session : aiohttp.ClientSession
            Persistent HTTP session for API calls
        unit_or_food_name : str, optional
            Name of the unit or food for display purposes
        """
        super().__init__()
        self.operation_type = operation_type
        self.pattern = pattern
        self.affected_ingredients = affected_ingredients
        self.unit_or_food_id = unit_or_food_id
        self.session = session
        self.unit_or_food_name = unit_or_food_name or pattern.pattern_text

        logger.info(
            f"Initialized BatchPreviewScreen: {operation_type} for pattern '{pattern.pattern_text}', "
            f"{len(affected_ingredients)} ingredients"
        )

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        with Container(id="dialog"):
            yield Static("Batch Operation Preview", id="header")
            yield Static(self.generate_summary_text(), id="summary")
            yield DataTable(id="ingredients-table")
            yield Static(self.generate_operation_details(), id="details")

            # Progress container (hidden by default)
            with Vertical(id="progress-container", classes="hidden"):
                yield ProgressBar(id="progress-bar", total=100)
                yield Static("", id="progress-status")

            # Buttons
            with Horizontal(id="buttons"):
                yield Button("Execute Batch Operation", id="execute", variant="primary")
                yield Button("Cancel", id="cancel", variant="default")

    def on_mount(self) -> None:
        """Initialize table when screen mounts."""
        logger.debug("Mounting BatchPreviewScreen, populating ingredients table")
        self.populate_ingredients_table()

    def generate_summary_text(self) -> str:
        """
        Generate operation summary text based on operation type.

        Returns
        -------
        str
            Summary text for display
        """
        count = len(self.affected_ingredients)
        name = self.unit_or_food_name

        summaries = {
            "create_unit": f"Create Unit: '{name}' → {count} ingredients",
            "create_food": f"Create Food: '{name}' → {count} ingredients",
            "add_unit_alias": f"Add Alias '{self.pattern.pattern_text}' to Unit '{name}' → {count} ingredients",
            "add_food_alias": f"Add Alias '{self.pattern.pattern_text}' to Food '{name}' → {count} ingredients",
        }

        return summaries.get(self.operation_type, f"Batch Operation → {count} ingredients")

    def generate_operation_details(self) -> str:
        """
        Generate detailed operation description.

        Returns
        -------
        str
            Operation details for display
        """
        count = len(self.affected_ingredients)
        # Count unique recipes
        recipe_ids = {ing.get("recipeId") for ing in self.affected_ingredients if ing.get("recipeId")}
        recipe_count = len(recipe_ids)

        field = "unit" if "unit" in self.operation_type else "food"

        return f"Will update {field} field for {count} ingredients across {recipe_count} recipes"

    def populate_ingredients_table(self) -> None:
        """Populate DataTable with affected ingredients."""
        table = self.query_one("#ingredients-table", DataTable)
        table.add_columns("Original Text", "Recipe Name", "Current Unit/Food")
        table.cursor_type = "row"

        # Limit to 100 rows for performance
        display_count = min(len(self.affected_ingredients), 100)

        for _i, ing in enumerate(self.affected_ingredients[:display_count]):
            original_text = ing.get("note") or ing.get("originalText") or "N/A"
            recipe_name = ing.get("recipeName", "N/A")

            # Get current unit or food name
            if "unit" in self.operation_type:
                current = ing.get("unit", {})
            else:
                current = ing.get("food", {})

            current_name = current.get("name", "(none)") if isinstance(current, dict) else "(none)"

            table.add_row(original_text, recipe_name, current_name)

        if len(self.affected_ingredients) > 100:
            logger.warning(f"Displaying first 100 of {len(self.affected_ingredients)} ingredients")

        logger.debug(f"Populated table with {display_count} ingredients")

    def watch_show_progress(self, old_value: bool, new_value: bool) -> None:
        """React to show_progress changes."""
        try:
            progress_container = self.query_one("#progress-container")

            if new_value:
                progress_container.remove_class("hidden")
            else:
                progress_container.add_class("hidden")
        except Exception:
            # Widget not mounted yet, skip update
            pass

    async def execute_batch_operation(self) -> None:
        """
        Execute the batch operation with progress tracking.

        Updates progress bar and status messages as ingredients are processed.
        Dismisses screen with result dictionary on completion.
        """
        from mealie_parser.api import (
            add_food_alias,
            add_unit_alias,
            update_ingredient_food_batch,
            update_ingredient_unit_batch,
        )

        logger.info(f"Executing batch operation: {self.operation_type}")

        # Disable execute button
        execute_btn = self.query_one("#execute", Button)
        execute_btn.disabled = True

        # Show progress UI
        self.show_progress = True
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_status = self.query_one("#progress-status", Static)

        total = len(self.affected_ingredients)
        progress_bar.update(total=total)

        # Extract ingredient IDs
        ingredient_ids = [ing.get("id") for ing in self.affected_ingredients if ing.get("id")]

        result = {
            "cancelled": False,
            "succeeded": 0,
            "failed": 0,
            "errors": [],
        }

        try:
            # Update progress: Starting
            progress_status.update("Starting batch operation...")
            logger.debug(f"Processing {len(ingredient_ids)} ingredient IDs")

            # Progress callback to update UI
            def update_progress(current: int, total_count: int):
                """Update progress bar and status during batch operation."""
                progress_bar.update(progress=current)
                progress_status.update(f"Processing ingredient {current}/{total_count}...")

            # Execute appropriate batch API function
            if self.operation_type == "create_unit":
                api_result = await update_ingredient_unit_batch(
                    self.session,
                    self.unit_or_food_id,
                    ingredient_ids,
                    progress_callback=update_progress,
                )
            elif self.operation_type == "create_food":
                api_result = await update_ingredient_food_batch(
                    self.session,
                    self.unit_or_food_id,
                    ingredient_ids,
                    progress_callback=update_progress,
                )
            elif self.operation_type == "add_unit_alias":
                # First add the alias, then update ingredients
                await add_unit_alias(self.session, self.unit_or_food_id, self.pattern.pattern_text)
                api_result = await update_ingredient_unit_batch(
                    self.session,
                    self.unit_or_food_id,
                    ingredient_ids,
                    progress_callback=update_progress,
                )
            elif self.operation_type == "add_food_alias":
                # First add the alias, then update ingredients
                await add_food_alias(self.session, self.unit_or_food_id, self.pattern.pattern_text)
                api_result = await update_ingredient_food_batch(
                    self.session,
                    self.unit_or_food_id,
                    ingredient_ids,
                    progress_callback=update_progress,
                )
            else:
                raise ValueError(f"Unknown operation type: {self.operation_type}")

            # Update progress: Complete
            progress_bar.update(progress=total)
            progress_status.update(
                f"✓ Completed: {len(api_result.successful)} succeeded, {len(api_result.failed)} failed ({api_result.success_rate:.1f}%)"
            )

            # Build result
            result["succeeded"] = len(api_result.successful)
            result["failed"] = len(api_result.failed)
            result["errors"] = [f"Ingredient {err['id']}: {err['error']}" for err in api_result.failed]

            logger.info(
                f"Batch operation complete: {result['succeeded']} succeeded, {result['failed']} failed ({api_result.success_rate:.1f}%)"
            )

        except Exception as e:
            logger.error(f"Error executing batch operation: {e}", exc_info=True)
            progress_status.update(f"✗ Error: {str(e)}")
            result["failed"] = total
            result["errors"] = [f"Batch operation failed: {str(e)}"]

        # Wait briefly to show completion message
        import asyncio

        await asyncio.sleep(2)

        # Return result
        self.dismiss(result)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "execute":
            logger.debug("Execute button pressed")
            import asyncio

            asyncio.create_task(self.execute_batch_operation())
        elif event.button.id == "cancel":
            logger.debug("Cancel button pressed")
            self.action_cancel()

    def action_cancel(self) -> None:
        """Handle cancel action."""
        logger.info("Batch operation cancelled by user")
        self.dismiss({"cancelled": True, "succeeded": 0, "failed": 0, "errors": []})
