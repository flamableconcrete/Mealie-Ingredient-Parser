"""Screen for reviewing parsed ingredients."""

import logging

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static

from ..api import (
    add_food_alias,
    create_food,
    create_unit,
    get_foods_full,
    get_units_full,
)
from ..modals import (
    CreateFoodModal,
    CreateUnitModal,
    FoodActionModal,
    SelectFoodModal,
    UnitActionModal,
)

logger = logging.getLogger(__name__)


class IngredientReviewScreen(Screen):
    """Screen for reviewing parsed ingredients"""

    CSS = """
    IngredientReviewScreen {
        background: $surface;
    }

    #ingredient-container {
        height: 1fr;
        padding: 1 2;
    }

    #ingredient-table {
        height: auto;
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

    #status-bar {
        height: 3;
        background: $panel;
        padding: 1;
    }
    """

    BINDINGS = [
        Binding("n", "next", "Next", show=True),
        Binding("escape", "back", "Back", show=True),
    ]

    def __init__(
        self, recipe, parsed_ingredients, session, known_units_full, known_foods_full
    ):
        super().__init__()
        self.recipe = recipe
        self.parsed_ingredients = parsed_ingredients
        self.session = session
        self.known_units_full = known_units_full
        self.known_foods_full = known_foods_full
        self.current_index = 0
        self.stats = {"units_created": [], "foods_created": [], "aliases_created": []}

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="ingredient-container"):
            yield Label(f"Recipe: {self.recipe['name']}", id="recipe-title")
            yield DataTable(id="ingredient-table")
            with Horizontal(id="button-container"):
                yield Button("Next Ingredient", variant="primary", id="next-btn")
                yield Button("Back to Recipes", variant="default", id="back-btn")
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self):
        self.display_current_ingredient()

    def display_current_ingredient(self):
        if self.current_index >= len(self.parsed_ingredients):
            self.app.pop_screen()
            return

        item = self.parsed_ingredients[self.current_index]
        parsed_ing = item.get("ingredient", {})
        original_text = item.get("input", "")

        table = self.query_one("#ingredient-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Field", "Value")

        table.add_row("Original", original_text)

        confidence = item.get("confidence", {})
        if isinstance(confidence, dict):
            conf_avg = confidence.get("average", 0)
            table.add_row("Confidence", f"{conf_avg:.2f}")
        else:
            table.add_row("Confidence", f"{confidence:.2f}")

        table.add_row("Quantity", str(parsed_ing.get("quantity", "")))

        unit = parsed_ing.get("unit", {})
        unit_name = unit.get("name") if isinstance(unit, dict) else (unit or "")
        table.add_row("Unit", unit_name)

        food = parsed_ing.get("food", {})
        food_name = food.get("name") if isinstance(food, dict) else (food or "")
        table.add_row("Food", food_name)

        table.add_row("Notes", parsed_ing.get("note", ""))

        status = self.query_one("#status-bar", Static)
        status.update(
            f"Ingredient {self.current_index + 1}/{len(self.parsed_ingredients)}"
        )

        # Check for missing unit/food and handle
        self.check_and_handle_missing()

    async def check_and_handle_missing(self):
        item = self.parsed_ingredients[self.current_index]
        ingredient = item.get("ingredient", {})

        # Check unit
        unit = ingredient.get("unit", {})
        if unit:
            unit_name = unit.get("name") if isinstance(unit, dict) else unit
            if unit_name:
                known_unit_names = {u["name"].lower() for u in self.known_units_full}
                if unit_name.lower() not in known_unit_names:
                    await self.handle_missing_unit(unit_name)

        # Check food
        food = ingredient.get("food", {})
        if food:
            food_name = food.get("name") if isinstance(food, dict) else food
            if food_name:
                known_food_names = {f["name"].lower() for f in self.known_foods_full}
                if food_name.lower() not in known_food_names:
                    await self.handle_missing_food(food_name)

    async def handle_missing_unit(self, unit_name):
        logger.info(f"Handling missing unit: {unit_name}")
        action = await self.app.push_screen_wait(UnitActionModal(unit_name))

        if action == "create":
            unit_data = await self.app.push_screen_wait(CreateUnitModal(unit_name))
            if unit_data:
                try:
                    new_unit = await create_unit(
                        self.session,
                        unit_data["name"],
                        unit_data["abbreviation"],
                        unit_data["description"],
                    )
                    self.stats["units_created"].append(new_unit["name"])
                    self.known_units_full = await get_units_full(self.session)
                    self.notify(f"✓ Created unit '{unit_name}'", severity="information", timeout=3)
                except Exception as e:
                    logger.error(f"Failed to create unit '{unit_name}': {e}", exc_info=True)
                    self.notify(f"✗ Error creating unit: {e}", severity="error", timeout=3)
        elif action == "skip":
            logger.info(f"Skipped creating unit: {unit_name}")

    async def handle_missing_food(self, food_name):
        logger.info(f"Handling missing food: {food_name}")
        action = await self.app.push_screen_wait(FoodActionModal(food_name))

        if action == "create":
            food_data = await self.app.push_screen_wait(CreateFoodModal(food_name))
            if food_data:
                try:
                    new_food = await create_food(
                        self.session, food_data["name"], food_data["description"]
                    )
                    self.stats["foods_created"].append(new_food["name"])
                    self.known_foods_full = await get_foods_full(self.session)
                    self.notify(f"✓ Created food '{food_name}'", severity="information", timeout=3)
                except Exception as e:
                    logger.error(f"Failed to create food '{food_name}': {e}", exc_info=True)
                    self.notify(f"✗ Error creating food: {e}", severity="error", timeout=3)

        elif action == "custom":
            food_data = await self.app.push_screen_wait(
                CreateFoodModal(food_name, allow_custom=True)
            )
            if food_data:
                try:
                    new_food = await create_food(
                        self.session, food_data["name"], food_data["description"]
                    )
                    self.stats["foods_created"].append(new_food["name"])
                    self.known_foods_full = await get_foods_full(self.session)
                    self.notify(
                        f"✓ Created food '{food_data['name']}'", severity="information", timeout=3
                    )
                except Exception as e:
                    logger.error(f"Failed to create food '{food_data['name']}': {e}", exc_info=True)
                    self.notify(f"✗ Error creating food: {e}", severity="error", timeout=3)

        elif action == "select":
            selection = await self.app.push_screen_wait(
                SelectFoodModal(self.known_foods_full, food_name)
            )
            if selection and selection.get("add_alias"):
                selected_food = selection["food"]
                try:
                    await add_food_alias(self.session, selected_food["id"], food_name)
                    self.stats["aliases_created"].append(
                        f"{food_name} → {selected_food['name']}"
                    )
                    self.known_foods_full = await get_foods_full(self.session)
                    self.notify(
                        f"✓ Added '{food_name}' as alias to '{selected_food['name']}'",
                        severity="information",
                        timeout=3
                    )
                except Exception as e:
                    logger.error(f"Failed to add alias '{food_name}' to '{selected_food.get('name', 'unknown')}': {e}", exc_info=True)
                    self.notify(f"✗ Error adding alias: {e}", severity="error", timeout=3)

        if action == "skip":
            logger.info(f"Skipped creating food: {food_name}")

    @on(Button.Pressed, "#next-btn")
    def action_next(self):
        self.current_index += 1
        self.display_current_ingredient()

    @on(Button.Pressed, "#back-btn")
    def action_back(self):
        self.app.pop_screen()
