"""Screen showing list of unparsed recipes."""

from loguru import logger
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Static

from ..api import get_foods_full, get_recipe_details, get_units_full, parse_ingredients
from .ingredient_review import IngredientReviewScreen


class RecipeListScreen(Screen):
    """Main screen showing list of unparsed recipes"""

    CSS = """
    RecipeListScreen {
        layout: vertical;
        background: $surface;
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

    #main-container {
        height: 1fr;
        padding: 1 2;
    }

    #recipe-table {
        height: 1fr;
    }

    #status-bar {
        height: 3;
        background: $panel;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r", "review", "Review Selected", show=True),
    ]

    def __init__(self, unparsed_recipes, session, known_units_full, known_foods_full):
        super().__init__()
        self.unparsed_recipes = unparsed_recipes
        self.session = session
        self.known_units_full = known_units_full
        self.known_foods_full = known_foods_full
        self.total_stats = {
            "units_created": [],
            "foods_created": [],
            "aliases_created": [],
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="title-bar"):
            yield Static("Recipe Mode", id="title")
        with Horizontal(id="controls"):
            yield Button("← Back [escape]", id="back-button", variant="default")
            yield Button("Review Selected [r]", variant="primary", id="review-btn")
        with Container(id="main-container"):
            table = DataTable(id="recipe-table", cursor_type="row")
            table.add_columns("Recipe Name", "Slug")
            yield table
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#recipe-table", DataTable)
        for recipe in self.unparsed_recipes:
            table.add_row(recipe["name"], recipe["slug"])

        self.update_status()

    def update_status(self):
        status = self.query_one("#status-bar", Static)
        status.update(
            f"Total Unparsed: {len(self.unparsed_recipes)} | "
            f"Units Created: {len(self.total_stats['units_created'])} | "
            f"Foods Created: {len(self.total_stats['foods_created'])} | "
            f"Aliases: {len(self.total_stats['aliases_created'])}"
        )

    @on(Button.Pressed, "#review-btn")
    @work
    async def action_review(self):
        table = self.query_one("#recipe-table", DataTable)
        if table.cursor_row is not None:
            recipe = self.unparsed_recipes[table.cursor_row]
            await self.review_recipe(recipe)

    async def review_recipe(self, recipe):
        try:
            logger.info(f"Starting review of recipe: {recipe['name']} (slug: {recipe['slug']})")
            # Get recipe details
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

            if not raw_ingredients:
                logger.warning(f"No ingredients to parse for recipe: {recipe['name']}")
                self.notify("No ingredients to parse", severity="warning", timeout=3)
                return

            logger.debug(f"Parsing {len(raw_ingredients)} ingredients for recipe: {recipe['name']}")
            # Parse ingredients
            parsed = await parse_ingredients(self.session, raw_ingredients)

            # Open review screen
            review_screen = IngredientReviewScreen(
                recipe,
                parsed,
                self.session,
                self.known_units_full,
                self.known_foods_full,
            )
            await self.app.push_screen_wait(review_screen)

            # Update stats
            self.total_stats["units_created"].extend(review_screen.stats["units_created"])
            self.total_stats["foods_created"].extend(review_screen.stats["foods_created"])
            self.total_stats["aliases_created"].extend(review_screen.stats["aliases_created"])

            logger.info(
                f"Completed review of recipe: {recipe['name']} - "
                f"Units: +{len(review_screen.stats['units_created'])}, "
                f"Foods: +{len(review_screen.stats['foods_created'])}, "
                f"Aliases: +{len(review_screen.stats['aliases_created'])}"
            )

            # Refresh data
            self.known_units_full = await get_units_full(self.session)
            self.known_foods_full = await get_foods_full(self.session)

            self.update_status()

        except Exception as e:
            logger.error(
                f"Error reviewing recipe '{recipe.get('name', 'unknown')}' (slug: {recipe.get('slug', 'unknown')}): {e}",
                exc_info=True,
            )
            self.notify(f"Error reviewing recipe: {e}", severity="error", timeout=3)

    @on(Button.Pressed, "#back-button")
    def action_back(self):
        """Return to mode selection screen."""
        logger.info("Returning from Recipe List screen")
        self.app.pop_screen()
