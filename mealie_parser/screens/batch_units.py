"""Batch mode screen for adding missing units across multiple recipes."""

import asyncio
import logging

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, ProgressBar, Static

from ..api import (
    add_unit_alias,
    create_unit,
    get_recipe_details,
    get_units_full,
    parse_ingredients,
    update_recipe,
)
from ..config import BATCH_SIZE
from ..utils import extract_missing_units

logger = logging.getLogger(__name__)


class BatchUnitsScreen(Screen):
    """Screen for batch processing missing units across multiple recipes"""

    CSS = """
    BatchUnitsScreen {
        background: $surface;
    }

    #main-container {
        height: 1fr;
        padding: 1 2;
    }

    #header-section {
        height: auto;
        padding: 1 0;
        margin-bottom: 1;
    }

    #title {
        text-style: bold;
        color: $accent;
        text-align: center;
    }

    #subtitle {
        color: $text-muted;
        margin-bottom: 1;
        text-align: center;
    }

    #info-text {
        color: $text;
        text-align: center;
        margin: 1 0;
    }

    #units-table {
        height: 1fr;
        margin: 1 0;
    }

    #button-container {
        height: auto;
        align: center middle;
        padding: 1;
    }

    Button {
        margin: 0 1;
    }

    #progress-bar {
        margin: 1 0;
    }

    #status-bar {
        height: 3;
        background: $panel;
        padding: 1;
        text-align: center;
    }
    """

    BINDINGS = [
        Binding("c", "create_units", "Create & Map Units", show=True),
        Binding("n", "next_batch", "Load Next Batch", show=True),
        Binding("b", "back", "Back", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, unparsed_recipes, session, known_units_full, known_foods_full):
        super().__init__()
        self.unparsed_recipes = unparsed_recipes
        self.session = session
        self.known_units_full = known_units_full
        self.known_foods_full = known_foods_full
        self.missing_units = {}
        self.batch_recipes = []
        self.all_parsed_ingredients = []
        self.current_batch_start = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main-container"):
            with Vertical(id="header-section"):
                yield Label("Batch Mode - Missing Units", id="title")
                yield Label(
                    f"Processing up to {BATCH_SIZE} recipes per batch",
                    id="subtitle",
                )
                yield Label(
                    "This will create all missing units suggested by the parser",
                    id="info-text",
                )
                yield ProgressBar(id="progress-bar", show_eta=False)

            table = DataTable(id="units-table", cursor_type="row", zebra_stripes=True)
            table.add_columns(
                "Missing Unit",
                "Times Used",
                "Action",
            )
            yield table

            with Horizontal(id="button-container"):
                yield Button("Create & Map Units [C]", variant="success", id="create-btn")
                yield Button("Load Next Batch [N]", variant="primary", id="next-btn")
                yield Button("Back [B]", variant="default", id="back-btn")

        yield Static(id="status-bar")
        yield Footer()

    async def on_mount(self):
        asyncio.create_task(self.load_batch_data())

    async def load_batch_data(self):
        """Load and parse ingredients from batch of recipes"""
        try:
            status = self.query_one("#status-bar", Static)
            progress_bar = self.query_one("#progress-bar", ProgressBar)

            # Determine batch range
            batch_end = min(self.current_batch_start + BATCH_SIZE, len(self.unparsed_recipes))
            self.batch_recipes = self.unparsed_recipes[self.current_batch_start:batch_end]

            total_recipes = len(self.batch_recipes)

            if total_recipes == 0:
                status.update("✅ No more recipes to process!")
                progress_bar.update(total=100, progress=100)
                create_btn = self.query_one("#create-btn", Button)
                next_btn = self.query_one("#next-btn", Button)
                create_btn.disabled = True
                next_btn.disabled = True

                table = self.query_one("#units-table", DataTable)
                table.clear()
                table.add_row("No more recipes", "N/A", "All batches processed")
                return

            status.update(f"⏳ Loading {total_recipes} recipes (batch {self.current_batch_start + 1}-{batch_end})...")
            progress_bar.update(total=total_recipes, progress=0)

            # Parse all ingredients from these recipes
            all_missing = {}
            recipe_count = 0

            for idx, recipe in enumerate(self.batch_recipes):
                try:
                    # Update progress
                    progress_bar.update(progress=idx + 1)
                    status.update(f"⏳ Processing recipe {idx + 1}/{total_recipes}: {recipe['name'][:40]}...")

                    details = await get_recipe_details(self.session, recipe["slug"])
                    recipe_ingredients = details.get("recipeIngredient") or []

                    # Extract raw ingredients
                    raw_ingredients = []
                    for ing in recipe_ingredients:
                        if isinstance(ing, dict):
                            text = ing.get("note") or ing.get("originalText") or ""
                            if text:
                                raw_ingredients.append(text)
                        elif isinstance(ing, str):
                            raw_ingredients.append(ing)

                    if raw_ingredients:
                        # Parse ingredients
                        parsed = await parse_ingredients(self.session, raw_ingredients)
                        self.all_parsed_ingredients.extend(parsed)

                        # Extract missing units
                        missing = extract_missing_units(parsed, self.known_units_full)

                        # Aggregate missing units
                        for unit_name, info in missing.items():
                            if unit_name not in all_missing:
                                all_missing[unit_name] = {
                                    "suggestion": info["suggestion"],
                                    "count": 0,
                                    "ingredients": [],
                                }
                            all_missing[unit_name]["count"] += info["count"]
                            all_missing[unit_name]["ingredients"].extend(info["ingredients"])

                        recipe_count += 1

                except Exception as e:
                    logger.error(f"Error processing recipe {recipe['name']}: {e}")
                    continue

            self.missing_units = all_missing

            # Populate table
            table = self.query_one("#units-table", DataTable)
            table.clear()

            if not self.missing_units:
                status.update("✅ No missing units found in this batch! Recipes are already well-parsed.")
                create_btn = self.query_one("#create-btn", Button)
                create_btn.disabled = True
                table.add_row("No missing units", "N/A", "Nothing to do in this batch")
            else:
                for unit_name, info in sorted(self.missing_units.items()):
                    table.add_row(
                        unit_name,
                        str(info["count"]),
                        f"Create '{info['suggestion']}'",
                    )

                create_btn = self.query_one("#create-btn", Button)
                create_btn.disabled = False

                status.update(
                    f"📊 Found {len(self.missing_units)} unique missing units across {recipe_count} recipes. Ready to create!"
                )

            # Update "Next Batch" button state
            next_btn = self.query_one("#next-btn", Button)
            remaining_recipes = len(self.unparsed_recipes) - batch_end
            if remaining_recipes > 0:
                next_btn.disabled = False
                next_btn.label = f"Load Next Batch ({remaining_recipes} left) [N]"
            else:
                next_btn.disabled = True
                next_btn.label = "No More Batches [N]"

        except Exception as e:
            logger.error(f"Error loading batch data: {e}", exc_info=True)
            self.notify(f"Error loading data: {e}", severity="error")
            status = self.query_one("#status-bar", Static)
            status.update(f"❌ Error: {e}")

    @on(Button.Pressed, "#create-btn")
    @work
    async def action_create_units(self):
        """Create missing units based on parser suggestions"""
        if not self.missing_units:
            self.notify("No units to create", severity="warning")
            return

        try:
            status = self.query_one("#status-bar", Static)
            status.update("⏳ Creating units...")

            created_count = 0
            skipped_count = 0

            for unit_name, info in self.missing_units.items():
                suggestion = info["suggestion"]

                # Check if this unit already exists
                existing_unit = next(
                    (u for u in self.known_units_full if u["name"].lower() == suggestion.lower()),
                    None,
                )

                if existing_unit:
                    logger.info(f"Unit '{suggestion}' already exists, skipping")
                    skipped_count += 1
                else:
                    # Create new unit
                    await create_unit(self.session, suggestion, abbreviation=suggestion[:3])
                    created_count += 1
                    logger.info(f"Created new unit: {suggestion}")

            # Refresh units
            self.known_units_full = await get_units_full(self.session)

            # Re-parse all recipes with new units
            status.update("⏳ Re-parsing recipes with new units...")
            reparsed_count = await self.reparse_recipes()

            self.notify(
                f"✅ Created {created_count} units (skipped {skipped_count} existing). Re-parsed {reparsed_count} recipes.",
                severity="information",
                timeout=10,
            )

            status.update(
                f"✅ Success! Created {created_count} units, re-parsed {reparsed_count} recipes"
            )

            # Wait a bit to show the message, then return
            await asyncio.sleep(2)
            self.app.pop_screen()

        except Exception as e:
            logger.error(f"Error creating units: {e}", exc_info=True)
            self.notify(f"Error creating units: {e}", severity="error")
            status = self.query_one("#status-bar", Static)
            status.update(f"❌ Error: {e}")

    async def reparse_recipes(self):
        """Re-parse all batch recipes after adding units"""
        reparsed_count = 0

        for recipe in self.batch_recipes:
            try:
                details = await get_recipe_details(self.session, recipe["slug"])
                recipe_ingredients = details.get("recipeIngredient") or []

                # Extract raw ingredients
                raw_ingredients = []
                for ing in recipe_ingredients:
                    if isinstance(ing, dict):
                        text = ing.get("note") or ing.get("originalText") or ""
                        if text:
                            raw_ingredients.append(text)
                    elif isinstance(ing, str):
                        raw_ingredients.append(ing)

                if raw_ingredients:
                    # Re-parse with new units
                    parsed = await parse_ingredients(self.session, raw_ingredients)

                    # Update the recipe with newly parsed ingredients
                    details["recipeIngredient"] = parsed
                    await update_recipe(self.session, recipe["slug"], details)

                    logger.info(f"Re-parsed recipe: {recipe['name']}")
                    reparsed_count += 1

            except Exception as e:
                logger.error(f"Error re-parsing recipe {recipe['name']}: {e}")
                continue

        return reparsed_count

    @on(Button.Pressed, "#next-btn")
    @work
    async def action_next_batch(self):
        """Load the next batch of recipes"""
        # Move to next batch
        self.current_batch_start += BATCH_SIZE

        # Clear current data
        self.missing_units = {}
        self.batch_recipes = []
        self.all_parsed_ingredients = []

        # Load new batch
        await self.load_batch_data()

    @on(Button.Pressed, "#back-btn")
    def action_back(self):
        """Go back to mode selection"""
        self.app.pop_screen()

    def action_quit(self):
        self.app.exit()
