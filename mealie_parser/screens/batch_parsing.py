"""Batch parsing screen for processing ingredients with different parsing methods."""

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp
from loguru import logger
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, ProgressBar, Static

from mealie_parser.api import (
    add_food_alias,
    add_unit_alias,
    create_food,
    create_unit,
    get_foods_full,
    get_units_full,
    parse_ingredients,
)
from mealie_parser.modals.parse_config_modal import ParseConfigModal
from mealie_parser.modals.unmatched_food_modal import UnmatchedFoodModal
from mealie_parser.modals.unmatched_unit_modal import UnmatchedUnitModal
from mealie_parser.models.pattern import PatternGroup
from mealie_parser.utils import find_food_by_name, find_unit_by_name


if TYPE_CHECKING:
    from textual.widgets._data_table import RowKey


class BatchParsingScreen(Screen):
    """
    Screen for batch parsing ingredients with method selection.

    Shows unparsed ingredients in a table with:
    - Original text
    - Recipe name
    - Parsed unit (populated after parsing)
    - Parsed food (populated after parsing)

    Allows user to configure parsing quantity and method, then processes
    ingredients one at a time, updating the table in real-time.
    """

    CSS = """
    BatchParsingScreen {
        background: $surface;
    }

    #header-container {
        dock: top;
        height: auto;
        padding: 1 2;
        background: $boost;
    }

    #title {
        text-style: bold;
        color: $primary;
    }

    #stats {
        color: $text-muted;
        margin-top: 1;
    }

    #controls {
        dock: top;
        height: auto;
        padding: 1 2;
        layout: horizontal;
        align: center middle;
        background: $panel;
    }

    #controls Button {
        margin: 0 1;
    }

    #table-container {
        height: 1fr;
        padding: 1 2;
    }

    #ingredients-table {
        height: 1fr;
    }

    .parsed-row {
        background: $success-darken-1 20%;
    }

    .unmatched-row {
        background: $warning-darken-1 30%;
    }

    #progress-container {
        dock: bottom;
        height: auto;
        padding: 1 2;
        background: $boost;
    }

    #progress-bar {
        height: 1;
        margin-bottom: 1;
    }

    #progress-status {
        text-align: center;
    }

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("escape", "back", "Back"),
        ("s", "start_parsing", "Start Parsing"),
    ]

    show_progress = reactive(False)
    parsing_active = reactive(False)
    parsing_started = reactive(False)  # Track if any parsing has occurred

    def __init__(
        self,
        unparsed_recipes: list[dict],
        session: aiohttp.ClientSession,
        known_units_full: list[dict],
        known_foods_full: list[dict],
    ):
        """
        Initialize batch parsing screen.

        Parameters
        ----------
        unparsed_recipes : list[dict]
            Recipes with unparsed ingredients
        session : aiohttp.ClientSession
            HTTP session for API calls
        known_units_full : list[dict]
            All known units from Mealie
        known_foods_full : list[dict]
            All known foods from Mealie
        """
        super().__init__()
        self.unparsed_recipes = unparsed_recipes
        self.session = session
        self.known_units_full = known_units_full
        self.known_foods_full = known_foods_full

        # Extract all ingredient lines from recipes
        self.ingredient_lines: list[dict[str, Any]] = []
        for recipe in unparsed_recipes:
            recipe_name = recipe.get("name", "Unknown")
            recipe_id = recipe.get("id")
            for ingredient in recipe.get("recipeIngredient", []):
                # Only include ingredients with note or originalText
                if ingredient.get("note") or ingredient.get("originalText"):
                    self.ingredient_lines.append(
                        {
                            "recipe_id": recipe_id,
                            "recipe_name": recipe_name,
                            "ingredient": ingredient,
                            "original_text": ingredient.get("note") or ingredient.get("originalText"),
                            "parsed_unit": None,
                            "parsed_food": None,
                            "parsed": False,
                            "has_match": False,
                        }
                    )

        # Row keys for table updates
        self.row_keys: dict[int, RowKey] = {}

        logger.info(f"BatchParsingScreen initialized with {len(self.ingredient_lines)} ingredient lines")

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield Header()

        with Container(id="header-container"):
            yield Static("Batch Parsing Mode", id="title")
            yield Static(
                f"Total ingredient lines: {len(self.ingredient_lines)} | Recipes: {len(self.unparsed_recipes)}",
                id="stats",
            )

        with Horizontal(id="controls"):
            yield Button("Start Parsing [s]", id="start-parsing", variant="primary")
            yield Button("Back [escape]", id="back", variant="default")

        with Container(id="table-container"):
            yield DataTable(id="ingredients-table")

        with Container(id="progress-container", classes="hidden"):
            yield ProgressBar(id="progress-bar", total=100)
            yield Static("", id="progress-status")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize table when screen mounts."""
        logger.debug("Mounting BatchParsingScreen")
        self.populate_ingredients_table()

        # Check if any ingredients have already been parsed
        if any(line.get("parsed", False) for line in self.ingredient_lines):
            self.parsing_started = True
            logger.info("Detected previously parsed ingredients, setting parsing_started=True")

    def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        """Handle cell selection - parse individual ingredient when clicking on pending items."""

        column_index = event.coordinate.column
        row_index = event.coordinate.row

        logger.info(f"Cell selected: row={row_index}, column={column_index}")

        # Get the ingredient line for this row
        if row_index >= len(self.ingredient_lines):
            logger.warning(f"Invalid row index: {row_index}")
            return

        line = self.ingredient_lines[row_index]
        logger.info(f"Ingredient line: parsed={line.get('parsed', False)}, text={line['original_text'][:50]}")

        # Only handle unparsed (pending) ingredients
        if line.get("parsed", False):
            logger.info(f"Ingredient already parsed, ignoring click: {line['original_text']}")
            return

        # For pending ingredients, clicking on any column opens the parse modal
        # Column 0: Original Text (pattern text)
        # Column 2-3: Parsed Unit/Food (empty for pending items - acts like status indicator)
        if column_index in [0, 2, 3]:
            # Open parse modal for this single ingredient
            logger.info(f"Opening parse modal for pending ingredient: {line['original_text']}")
            asyncio.create_task(self._handle_single_ingredient_parse(row_index))
        else:
            logger.info(f"Column {column_index} clicked - not triggering parse modal (only 0,2,3)")

    def get_styled_cell_text(self, text: str, has_match: bool, is_parsed: bool) -> Text:
        """
        Create consistently styled Text object for table cells.

        Parameters
        ----------
        text : str
            The text content to style
        has_match : bool
            Whether the parsed item matched a known unit/food
        is_parsed : bool
            Whether the item has been parsed yet

        Returns
        -------
        Text
            Rich Text object with appropriate styling
        """
        if not is_parsed or not text:
            return Text("")

        if has_match:
            return Text(text, style="bold green")
        return Text(text, style="bold yellow")

    def populate_ingredients_table(self) -> None:
        """Populate DataTable with ingredient lines."""
        table = self.query_one("#ingredients-table", DataTable)
        table.add_columns("Original Text", "Recipe", "Parsed Unit", "Parsed Food")

        for i, line in enumerate(self.ingredient_lines):
            # Use existing parsed data if available
            parsed_unit = line.get("parsed_unit", "")
            parsed_food = line.get("parsed_food", "")
            has_match = line.get("has_match", False)
            is_parsed = line.get("parsed", False)

            # Use helper method for consistent styling
            styled_unit = self.get_styled_cell_text(parsed_unit, has_match, is_parsed)
            styled_food = self.get_styled_cell_text(parsed_food, has_match, is_parsed)

            row_key = table.add_row(
                line["original_text"],
                line["recipe_name"],
                styled_unit,
                styled_food,
            )
            self.row_keys[i] = row_key

            # Apply row styling if already parsed
            if is_parsed:
                if has_match:
                    table.add_row_class(row_key, "parsed-row")
                else:
                    table.add_row_class(row_key, "unmatched-row")

        logger.debug(f"Populated table with {len(self.ingredient_lines)} rows")

    def watch_show_progress(self, old_value: bool, new_value: bool) -> None:
        """React to show_progress changes."""
        try:
            progress_container = self.query_one("#progress-container")
            if new_value:
                progress_container.remove_class("hidden")
            else:
                progress_container.add_class("hidden")
        except Exception:
            pass

    def watch_parsing_active(self, old_value: bool, new_value: bool) -> None:
        """React to parsing_active changes."""
        try:
            start_btn = self.query_one("#start-parsing", Button)
            start_btn.disabled = new_value
        except Exception:
            pass

    def watch_parsing_started(self, old_value: bool, new_value: bool) -> None:
        """React to parsing_started changes - update button label."""
        try:
            start_btn = self.query_one("#start-parsing", Button)

            if new_value:
                # Change button to "Continue Parsing"
                start_btn.label = "Continue Parsing [s]"
            else:
                # Reset to "Start Parsing"
                start_btn.label = "Start Parsing [s]"
        except Exception:
            pass

    async def _handle_single_ingredient_parse(self, row_index: int) -> None:
        """
        Handle parsing a single ingredient from cell click.

        Parameters
        ----------
        row_index : int
            Index of the ingredient to parse
        """
        if self.parsing_active:
            logger.warning("Parsing already in progress, cannot parse single ingredient")
            self.notify("Parsing in progress", severity="warning", timeout=2)
            return

        line = self.ingredient_lines[row_index]
        item_name = line["original_text"]

        # Show parse config modal but only ask for method (no quantity/filter needed)
        # Use single_item mode to show simplified modal
        config = await self.app.push_screen_wait(
            ParseConfigModal(
                parsing_started=self.parsing_started,
                single_item=True,
                item_name=item_name,
            )
        )

        if config is None:
            logger.info("Single ingredient parse cancelled")
            return

        method = config["method"]
        logger.info(f"Parsing single ingredient at index {row_index} with method {method}")

        # Parse just this one ingredient
        await self.parse_ingredients_batch_filtered([row_index], method)

        # After parsing, check for unmatched units/foods and handle them
        await self._handle_unmatched_items(row_index, method)

    async def _handle_unmatched_items(self, row_index: int, parse_method: str) -> None:
        """
        Handle unmatched units and foods for a single parsed ingredient.

        Opens modals for unmatched items and creates units/foods or adds aliases
        based on user input.

        Parameters
        ----------
        row_index : int
            Index of the ingredient to check
        parse_method : str
            The parsing method used ("nlp", "brute", or "openai")
        """
        line = self.ingredient_lines[row_index]

        # Only process if ingredient was successfully parsed
        if not line.get("parsed", False):
            return

        parsed_unit_name = line.get("parsed_unit", "")
        parsed_food_name = line.get("parsed_food", "")

        # Check for unmatched unit
        if parsed_unit_name:
            matching_unit = find_unit_by_name(parsed_unit_name, self.known_units_full)
            if not matching_unit:
                logger.info(f"Unmatched unit found: {parsed_unit_name}")
                await self._handle_unmatched_unit(row_index, parsed_unit_name, parse_method)

        # Refresh units list after potential unit creation
        self.known_units_full = await get_units_full(self.session)

        # Check for unmatched food
        if parsed_food_name:
            matching_food = find_food_by_name(parsed_food_name, self.known_foods_full)
            if not matching_food:
                logger.info(f"Unmatched food found: {parsed_food_name}")
                await self._handle_unmatched_food(row_index, parsed_food_name, parse_method)

        # Refresh foods list after potential food creation
        self.known_foods_full = await get_foods_full(self.session)

        # Update the table row to reflect any changes
        await self._update_table_row_after_match(row_index)

    async def _handle_unmatched_unit(self, row_index: int, parsed_unit_name: str, parse_method: str) -> None:
        """
        Handle an unmatched unit by showing the modal and processing user action.

        Parameters
        ----------
        row_index : int
            Index of the ingredient
        parsed_unit_name : str
            The parsed unit name that wasn't matched
        parse_method : str
            The parsing method used
        """
        line = self.ingredient_lines[row_index]

        # Create a temporary PatternGroup for the modal
        pattern = PatternGroup(
            pattern_text=line["original_text"],
            parsed_unit=parsed_unit_name,
            unit_confidence=0.8,  # Default confidence
        )

        # Show the unmatched unit modal
        result = await self.app.push_screen_wait(UnmatchedUnitModal(pattern, self.known_units_full, parse_method))

        if result is None:
            logger.info("User cancelled unit modal")
            return

        # Process the result
        await self._process_unit_action(result, row_index)

    async def _handle_unmatched_food(self, row_index: int, parsed_food_name: str, parse_method: str) -> None:
        """
        Handle an unmatched food by showing the modal and processing user action.

        Parameters
        ----------
        row_index : int
            Index of the ingredient
        parsed_food_name : str
            The parsed food name that wasn't matched
        parse_method : str
            The parsing method used
        """
        line = self.ingredient_lines[row_index]

        # Create a temporary PatternGroup for the modal
        pattern = PatternGroup(
            pattern_text=line["original_text"],
            parsed_food=parsed_food_name,
            food_confidence=0.8,  # Default confidence
        )

        # Show the unmatched food modal
        result = await self.app.push_screen_wait(UnmatchedFoodModal(pattern, self.known_foods_full, parse_method))

        if result is None:
            logger.info("User cancelled food modal")
            return

        # Process the result
        await self._process_food_action(result, row_index)

    async def _process_unit_action(self, result: dict, row_index: int) -> None:
        """
        Process the action from the unmatched unit modal.

        Parameters
        ----------
        result : dict
            The result from the modal containing operation details
        row_index : int
            Index of the ingredient
        """
        operation = result.get("operation")

        try:
            if operation == "create_unit":
                unit_name = result["unit_name"]
                logger.info(f"Creating new unit: {unit_name}")
                await create_unit(self.session, unit_name, abbreviation=unit_name[:3])
                self.notify(f"Created unit: {unit_name}", severity="information")

            elif operation == "add_unit_alias":
                unit_id = result["unit_id"]
                alias = result["alias"]
                unit_name = result["unit_name"]
                logger.info(f"Adding alias '{alias}' to unit '{unit_name}'")
                await add_unit_alias(self.session, unit_id, alias)
                self.notify(
                    f"Added alias '{alias}' to unit '{unit_name}'",
                    severity="information",
                )

            elif operation == "create_unit_with_alias":
                unit_name = result["unit_name"]
                alias = result.get("alias")
                logger.info(f"Creating unit '{unit_name}' with alias '{alias}'")
                # Create the unit first
                await create_unit(self.session, unit_name, abbreviation=unit_name[:3])
                # Add the alias if provided
                if alias:
                    # Refresh to get the new unit ID
                    self.known_units_full = await get_units_full(self.session)
                    new_unit = find_unit_by_name(unit_name, self.known_units_full)
                    if new_unit:
                        await add_unit_alias(self.session, new_unit["id"], alias)
                self.notify(
                    f"Created unit '{unit_name}'" + (f" with alias '{alias}'" if alias else ""),
                    severity="information",
                )

        except Exception as e:
            logger.error(f"Error processing unit action: {e}", exc_info=True)
            self.notify(f"Error: {e}", severity="error")

    async def _process_food_action(self, result: dict, row_index: int) -> None:
        """
        Process the action from the unmatched food modal.

        Parameters
        ----------
        result : dict
            The result from the modal containing operation details
        row_index : int
            Index of the ingredient
        """
        operation = result.get("operation")

        try:
            if operation == "create_food":
                food_name = result["food_name"]
                logger.info(f"Creating new food: {food_name}")
                await create_food(self.session, food_name)
                self.notify(f"Created food: {food_name}", severity="information")

            elif operation == "add_food_alias":
                food_id = result["food_id"]
                alias = result["alias"]
                food_name = result["food_name"]
                logger.info(f"Adding alias '{alias}' to food '{food_name}'")
                await add_food_alias(self.session, food_id, alias)
                self.notify(
                    f"Added alias '{alias}' to food '{food_name}'",
                    severity="information",
                )

            elif operation == "create_food_with_alias":
                food_name = result["food_name"]
                alias = result.get("alias")
                logger.info(f"Creating food '{food_name}' with alias '{alias}'")
                # Create the food first
                await create_food(self.session, food_name)
                # Add the alias if provided
                if alias:
                    # Refresh to get the new food ID
                    self.known_foods_full = await get_foods_full(self.session)
                    new_food = find_food_by_name(food_name, self.known_foods_full)
                    if new_food:
                        await add_food_alias(self.session, new_food["id"], alias)
                self.notify(
                    f"Created food '{food_name}'" + (f" with alias '{alias}'" if alias else ""),
                    severity="information",
                )

        except Exception as e:
            logger.error(f"Error processing food action: {e}", exc_info=True)
            self.notify(f"Error: {e}", severity="error")

    async def _update_table_row_after_match(self, row_index: int) -> None:
        """
        Update the table row styling after creating/matching units/foods.

        Parameters
        ----------
        row_index : int
            Index of the ingredient to update
        """
        line = self.ingredient_lines[row_index]
        parsed_unit_name = line.get("parsed_unit", "")
        parsed_food_name = line.get("parsed_food", "")

        # Check if items now match
        has_match = False
        if parsed_unit_name:
            matching_unit = find_unit_by_name(parsed_unit_name, self.known_units_full)
            if matching_unit:
                has_match = True

        if parsed_food_name and not has_match:
            matching_food = find_food_by_name(parsed_food_name, self.known_foods_full)
            if matching_food:
                has_match = True

        # Update the line data
        line["has_match"] = has_match

        # Update table styling
        table = self.query_one("#ingredients-table", DataTable)
        row_key = self.row_keys[row_index]

        # Clear previous styling
        table.remove_row_class(row_key, "parsed-row")
        table.remove_row_class(row_key, "unmatched-row")

        # Apply new styling
        if has_match:
            table.add_row_class(row_key, "parsed-row")
        else:
            table.add_row_class(row_key, "unmatched-row")

        # Update cell content with proper styling
        styled_unit = self.get_styled_cell_text(parsed_unit_name, has_match, True)
        styled_food = self.get_styled_cell_text(parsed_food_name, has_match, True)

        table.update_cell(row_key, "Parsed Unit", styled_unit)
        table.update_cell(row_key, "Parsed Food", styled_food)

        logger.info(
            f"Updated table row {row_index}: has_match={has_match}, unit='{parsed_unit_name}', food='{parsed_food_name}'"
        )

    async def action_start_parsing(self) -> None:
        """Open parse config modal and start parsing."""
        if self.parsing_active:
            logger.warning("Parsing already in progress")
            return

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

        # Determine which ingredients to parse based on filter
        if self.parsing_started:
            if parse_filter == "pending":
                # Only unparsed ingredients
                indices_to_parse = [i for i, line in enumerate(self.ingredient_lines) if not line["parsed"]]
            elif parse_filter == "pending_unmatched":
                # Unparsed + unmatched (parsed but no match)
                indices_to_parse = [
                    i
                    for i, line in enumerate(self.ingredient_lines)
                    if not line["parsed"] or (line["parsed"] and not line["has_match"])
                ]
            else:  # "all"
                # All ingredients (re-parse everything)
                indices_to_parse = list(range(len(self.ingredient_lines)))
        else:
            # First run - parse from beginning
            indices_to_parse = list(range(len(self.ingredient_lines)))

        # Apply quantity limit
        if quantity != -1 and len(indices_to_parse) > quantity:
            indices_to_parse = indices_to_parse[:quantity]

        parse_count = len(indices_to_parse)

        if parse_count == 0:
            logger.warning("No ingredients to parse with current filter")
            return

        # Start parsing task
        asyncio.create_task(self.parse_ingredients_batch_filtered(indices_to_parse, method))

    def _extract_parsed_names(self, ingredient: dict) -> tuple[str, str]:
        """Extract unit and food names from parsed ingredient.

        Parameters
        ----------
        ingredient : dict
            Parsed ingredient object from parser

        Returns
        -------
        tuple[str, str]
            Tuple of (parsed_unit_name, parsed_food_name)
        """
        parsed_unit_name = ""
        parsed_food_name = ""

        # Extract parsed unit
        if ingredient.get("unit"):
            if isinstance(ingredient["unit"], dict):
                parsed_unit_name = ingredient["unit"].get("name", "")
            elif isinstance(ingredient["unit"], str):
                parsed_unit_name = ingredient["unit"]
            logger.info(f"  Extracted unit name: '{parsed_unit_name}' (type: {type(ingredient['unit'])})")

        # Extract parsed food
        if ingredient.get("food"):
            if isinstance(ingredient["food"], dict):
                parsed_food_name = ingredient["food"].get("name", "")
            elif isinstance(ingredient["food"], str):
                parsed_food_name = ingredient["food"]
            logger.info(f"  Extracted food name: '{parsed_food_name}' (type: {type(ingredient['food'])})")

        return parsed_unit_name, parsed_food_name

    def _check_matches(self, parsed_unit_name: str, parsed_food_name: str) -> bool:
        """Check if parsed unit or food matches known items.

        Parameters
        ----------
        parsed_unit_name : str
            Name of parsed unit
        parsed_food_name : str
            Name of parsed food

        Returns
        -------
        bool
            True if match found, False otherwise
        """
        has_match = False

        if parsed_unit_name:
            has_match = any(u.get("name") == parsed_unit_name for u in self.known_units_full)
            logger.info(f"  Unit match check: '{parsed_unit_name}' -> {has_match}")

        if parsed_food_name and not has_match:
            has_match = any(f.get("name") == parsed_food_name for f in self.known_foods_full)
            logger.info(f"  Food match check: '{parsed_food_name}' -> {has_match}")

        return has_match

    def _update_table_row(
        self, table: DataTable, i: int, parsed_unit_name: str, parsed_food_name: str, has_match: bool
    ) -> None:
        """Update table row with parsed results and styling.

        Parameters
        ----------
        table : DataTable
            Table widget to update
        i : int
            Ingredient index
        parsed_unit_name : str
            Name of parsed unit
        parsed_food_name : str
            Name of parsed food
        has_match : bool
            Whether a match was found
        """
        row_key = self.row_keys[i]

        # Use helper method for consistent styling
        styled_unit = self.get_styled_cell_text(parsed_unit_name, has_match, True)
        styled_food = self.get_styled_cell_text(parsed_food_name, has_match, True)

        table.update_cell(row_key, "Parsed Unit", styled_unit)
        table.update_cell(row_key, "Parsed Food", styled_food)

        # Clear previous row styling
        table.remove_row_class(row_key, "parsed-row")
        table.remove_row_class(row_key, "unmatched-row")

        # Apply row styling
        if has_match:
            table.add_row_class(row_key, "parsed-row")
        else:
            table.add_row_class(row_key, "unmatched-row")

    async def _parse_single_ingredient(
        self, table: DataTable, i: int, line: dict, method: str
    ) -> tuple[str, str, bool]:
        """Parse a single ingredient and update data structures.

        Parameters
        ----------
        table : DataTable
            Table widget to update
        i : int
            Ingredient index
        line : dict
            Ingredient line data
        method : str
            Parsing method

        Returns
        -------
        tuple[str, str, bool]
            Tuple of (parsed_unit_name, parsed_food_name, has_match)
        """
        try:
            # Parse single ingredient
            result = await parse_ingredients(self.session, [line["original_text"]], parser=method)

            # Log full parser response for debugging
            logger.info(f"Parser response for '{line['original_text']}': {result}")

            if result and len(result) > 0:
                parsed = result[0]
                ingredient = parsed.get("ingredient", {})

                # Extract parsed names
                parsed_unit_name, parsed_food_name = self._extract_parsed_names(ingredient)

                # Check for matches
                has_match = self._check_matches(parsed_unit_name, parsed_food_name)

                # Update line data
                line["parsed_unit"] = parsed_unit_name
                line["parsed_food"] = parsed_food_name
                line["parsed"] = True
                line["has_match"] = has_match

                # Update table
                self._update_table_row(table, i, parsed_unit_name, parsed_food_name, has_match)

                # Log results
                if not has_match:
                    logger.warning(
                        f"No match found for '{line['original_text']}': "
                        f"unit='{parsed_unit_name}', food='{parsed_food_name}'"
                    )
                else:
                    logger.info(f"Match found for '{line['original_text']}'")

                return parsed_unit_name, parsed_food_name, has_match

            logger.warning(f"Parser returned empty result for '{line['original_text']}'")
            line["parsed"] = True
            line["has_match"] = False
            return "", "", False

        except Exception as e:
            logger.error(f"Error parsing ingredient {i}: {e}", exc_info=True)
            line["parsed"] = True
            line["has_match"] = False
            return "", "", False

    async def parse_ingredients_batch_filtered(self, indices: list[int], method: str) -> None:
        """Parse ingredients at specified indices with progress tracking.

        Parameters
        ----------
        indices : list[int]
            Indices of ingredients to parse
        method : str
            Parsing method: "nlp", "brute", or "openai"
        """
        self.parsing_active = True
        self.show_progress = True

        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_status = self.query_one("#progress-status", Static)
        table = self.query_one("#ingredients-table", DataTable)

        count = len(indices)
        progress_bar.update(total=count)

        for idx, i in enumerate(indices):
            line = self.ingredient_lines[i]

            # Update progress status
            progress_status.update(f"Parsing {idx + 1}/{count}: {line['original_text'][:50]}...")

            # Parse the ingredient
            await self._parse_single_ingredient(table, i, line, method)

            # Update progress bar
            progress_bar.update(progress=idx + 1)

            # Small delay to allow UI updates
            await asyncio.sleep(0.1)

        # Mark that parsing has started (after completing batch)
        if not self.parsing_started and count > 0:
            self.parsing_started = True
            logger.info("Batch parsing completed, setting parsing_started=True")

        # Parsing complete
        matched_count = sum(1 for i in indices if self.ingredient_lines[i]["has_match"])
        unmatched_count = count - matched_count

        progress_status.update(
            f"✓ Parsing complete: {matched_count} matched, {unmatched_count} unmatched (highlighted yellow)"
        )

        self.parsing_active = False

        # Force table to refresh and preserve Text formatting
        table.refresh()

        logger.info(f"Batch parsing complete: {matched_count}/{count} matched")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "start-parsing":
            asyncio.create_task(self.action_start_parsing())
        elif event.button.id == "back":
            self.action_back()

    def action_back(self) -> None:
        """Return to previous screen."""
        logger.info("Returning from batch parsing screen")
        self.app.pop_screen()
