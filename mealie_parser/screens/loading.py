"""Loading screen while fetching initial data."""

import asyncio
import logging

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Label

from ..api import get_all_recipes, get_foods_full, get_recipe_details, get_units_full
from ..services.pattern_analyzer import PatternAnalyzer
from ..utils import is_recipe_unparsed
from .mode_selection import ModeSelectionScreen

logger = logging.getLogger(__name__)


class LoadingScreen(Screen):
    """Loading screen while fetching initial data"""

    CSS = """
    LoadingScreen {
        align: center middle;
        background: $surface;
    }

    #loading-container {
        width: 60;
        height: auto;
        background: $panel;
        border: thick $primary;
        padding: 2 4;
    }

    Label {
        text-align: center;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="loading-container"):
            yield Label("Loading Mealie Data...", id="loading-title")
            yield Label("Fetching recipes, units, and foods", id="loading-subtitle")

    async def on_mount(self):
        # Load data in background
        asyncio.create_task(self.load_data())

    async def load_data(self):
        try:
            logger.info("Starting data load process")
            # Use the app's persistent session
            session = self.app.session

            # Load all data
            logger.info("Fetching recipes, units, and foods")
            recipes = await get_all_recipes(session)
            known_units_full = await get_units_full(session)
            known_foods_full = await get_foods_full(session)

            # Find unparsed recipes
            logger.info(f"Checking {len(recipes)} recipes for unparsed ingredients")
            unparsed_recipes = []
            for recipe in recipes:
                try:
                    details = await get_recipe_details(session, recipe["slug"])
                    recipe_ingredients = details.get("recipeIngredient") or []

                    if recipe_ingredients and is_recipe_unparsed(recipe_ingredients):
                        unparsed_recipes.append(recipe)
                        logger.debug(f"Recipe '{recipe['name']}' has unparsed ingredients")
                except Exception as e:
                    logger.error(f"Error checking recipe '{recipe.get('name', 'unknown')}' (slug: {recipe.get('slug', 'unknown')}): {e}", exc_info=True)
                    # Continue processing other recipes

            logger.info(f"Found {len(unparsed_recipes)} recipes with unparsed ingredients")

            if not unparsed_recipes:
                self.notify("No unparsed recipes found!", severity="warning", timeout=3)
                logger.warning("No unparsed recipes found - exiting application")
                self.app.exit()
                return

            # Perform pattern analysis
            logger.info("Starting pattern analysis")
            analyzer = PatternAnalyzer()

            # Extract unparsed ingredients from all recipes
            unparsed_ingredients = analyzer.extract_unparsed_ingredients(recipes)
            logger.info(f"Extracted {len(unparsed_ingredients)} unparsed ingredients")

            # Group by unit and food patterns
            unit_patterns = analyzer.group_by_unit_pattern(unparsed_ingredients)
            food_patterns = analyzer.group_by_food_pattern(unparsed_ingredients)

            logger.info(f"Pattern analysis complete: {len(unit_patterns)} unit patterns, {len(food_patterns)} food patterns found")

            # Store pattern groups in screen state for later use
            self.unit_patterns = unit_patterns
            self.food_patterns = food_patterns

            # Switch to mode selection screen
            self.app.push_screen(
                ModeSelectionScreen(
                    unparsed_recipes, session, known_units_full, known_foods_full
                )
            )

        except Exception as e:
            logger.error(f"Critical error during data load: {e}", exc_info=True)
            self.notify(f"Error loading data: {e}", severity="error", timeout=3)
            self.app.exit()
