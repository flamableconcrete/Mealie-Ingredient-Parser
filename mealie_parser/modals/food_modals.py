"""Modal screens for food management."""

from loguru import logger
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from mealie_parser.validation import validate_food_name


class CreateFoodModal(ModalScreen):
    """Modal for creating a new food with validation"""

    CSS = """
    CreateFoodModal {
        align: center middle;
    }

    #modal-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    Input {
        margin: 1 0;
    }

    #validation-errors {
        color: $error;
        margin: 0 0 1 0;
        height: auto;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    validation_errors = reactive("")

    def __init__(self, food_name: str, existing_foods: list[dict], allow_custom: bool = False):
        super().__init__()
        self.food_name = food_name
        self.existing_foods = existing_foods
        self.allow_custom = allow_custom
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"Create New Food: {self.food_name}")
            if self.allow_custom:
                yield Label("Custom Name (leave blank to use suggestion):")
                yield Input(placeholder=self.food_name, id="custom_name")
            yield Label("Description (optional):")
            yield Input(id="description")
            yield Static("", id="validation-errors")
            with Horizontal(id="button-container"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        """Validate food name on mount."""
        self.validate_inputs()

    @on(Input.Changed, "#custom_name")
    def on_custom_name_changed(self, event: Input.Changed) -> None:
        """Validate on custom name change."""
        self.validate_inputs()

    def validate_inputs(self) -> bool:
        """
        Validate food name.

        Returns
        -------
        bool
            True if validation passes, False otherwise
        """
        # Determine which name to validate
        name = self.food_name
        if self.allow_custom:
            try:
                custom_input = self.query_one("#custom_name", Input)
                custom_name = custom_input.value.strip()
                if custom_name:
                    name = custom_name
            except Exception:
                # Widget not mounted yet
                pass

        # Validate food name
        result = validate_food_name(name, self.existing_foods)

        # Update validation errors
        self.validation_errors = "\n".join(result.errors)

        # Enable/disable create button
        try:
            create_btn = self.query_one("#create", Button)
            create_btn.disabled = not result.is_valid
        except Exception:
            # Widget not mounted yet
            pass

        if not result.is_valid:
            logger.debug(f"Validation failed for food '{name}': {result.errors}")

        return result.is_valid

    def watch_validation_errors(self, errors: str) -> None:
        """Update validation errors display."""
        error_widget = self.query_one("#validation-errors", Static)
        error_widget.update(errors)

    @on(Button.Pressed, "#create")
    def on_create(self):
        description = self.query_one("#description", Input).value
        name = self.food_name

        if self.allow_custom:
            custom_name = self.query_one("#custom_name", Input).value.strip()
            if custom_name:
                name = custom_name

        # Final validation check
        result = validate_food_name(name, self.existing_foods)
        if not result.is_valid:
            logger.warning(f"Attempted to create food with validation errors: {result.errors}")
            self.notify("Cannot create food: validation errors", severity="error")
            return

        self.result = {"name": name, "description": description}
        logger.info(f"Creating food: {name}")
        self.dismiss(self.result)

    @on(Button.Pressed, "#cancel")
    def on_cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)


class SelectFoodModal(ModalScreen):
    """Modal for selecting an existing food"""

    CSS = """
    SelectFoodModal {
        align: center middle;
    }

    #modal-container {
        width: 80;
        height: 30;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #search-input {
        margin: 1 0;
    }

    DataTable {
        height: 20;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, foods: list, suggestion: str):
        super().__init__()
        self.all_foods = foods
        self.suggestion = suggestion
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"Select Food for: '{self.suggestion}'")
            yield Input(placeholder="Search foods...", id="search-input")
            table = DataTable(id="food-table")
            table.add_columns("Food Name")
            yield table
            with Horizontal(id="button-container"):
                yield Button("Add as Alias", variant="primary", id="select")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self):
        self.update_table(self.all_foods[:50])

    def update_table(self, foods):
        table = self.query_one("#food-table", DataTable)
        table.clear()
        for food in foods:
            table.add_row(food["name"], key=food["id"])

    @on(Input.Changed, "#search-input")
    def on_search(self, event: Input.Changed):
        search_term = event.value.lower()
        if not search_term:
            self.update_table(self.all_foods[:50])
        else:
            matches = [f for f in self.all_foods if search_term in f["name"].lower()]
            self.update_table(matches[:50])

    @on(Button.Pressed, "#select")
    def on_select(self):
        table = self.query_one("#food-table", DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)[0]
            for food in self.all_foods:
                if food["id"] == row_key:
                    self.result = {"food": food, "add_alias": True}
                    self.dismiss(self.result)
                    return

    @on(Button.Pressed, "#cancel")
    def on_cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)


class FoodActionModal(ModalScreen):
    """Modal for handling missing foods"""

    CSS = """
    FoodActionModal {
        align: center middle;
    }

    #modal-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    Button {
        margin: 1 1;
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("1", "create", "Create"),
        Binding("2", "select", "Select"),
        Binding("3", "custom", "Custom"),
        Binding("4", "skip", "Skip"),
    ]

    def __init__(self, food_name: str):
        super().__init__()
        self.food_name = food_name
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"⚠ Food '{self.food_name}' not found")
            yield Button("1. Create New Food", variant="primary", id="create")
            yield Button("2. Select Existing & Add Alias", variant="success", id="select")
            yield Button("3. Create with Custom Name", variant="default", id="custom")
            yield Button("4. Skip", variant="default", id="skip")
            yield Button("Q. Quit", variant="error", id="quit")

    @on(Button.Pressed, "#create")
    def action_create(self):
        self.result = "create"
        self.dismiss(self.result)

    @on(Button.Pressed, "#select")
    def action_select(self):
        self.result = "select"
        self.dismiss(self.result)

    @on(Button.Pressed, "#custom")
    def action_custom(self):
        self.result = "custom"
        self.dismiss(self.result)

    @on(Button.Pressed, "#skip")
    def action_skip(self):
        self.result = "skip"
        self.dismiss(self.result)

    @on(Button.Pressed, "#quit")
    def on_quit(self):
        self.app.exit()

    def action_cancel(self):
        self.result = "skip"
        self.dismiss(self.result)
