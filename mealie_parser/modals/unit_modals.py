"""Modal screens for unit management."""

from loguru import logger
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from mealie_parser.validation import validate_abbreviation, validate_unit_name


class CreateUnitModal(ModalScreen):
    """Modal for creating a new unit with validation"""

    CSS = """
    CreateUnitModal {
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

    def __init__(self, unit_name: str, existing_units: list[dict]):
        super().__init__()
        self.unit_name = unit_name
        self.existing_units = existing_units
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"Create New Unit: {self.unit_name}")
            yield Label("Abbreviation:")
            yield Input(value=self.unit_name[:3], id="abbreviation")
            yield Label("Description (optional):")
            yield Input(id="description")
            yield Static("", id="validation-errors")
            with Horizontal(id="button-container"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", variant="default", id="cancel")

    def on_mount(self) -> None:
        """Validate unit name on mount."""
        self.validate_inputs()

    @on(Input.Changed, "#abbreviation")
    def on_abbreviation_changed(self, event: Input.Changed) -> None:
        """Validate on abbreviation change."""
        self.validate_inputs()

    def validate_inputs(self) -> bool:
        """
        Validate unit name and abbreviation.

        Returns
        -------
        bool
            True if validation passes, False otherwise
        """
        errors = []

        # Validate unit name
        name_result = validate_unit_name(self.unit_name, self.existing_units)
        if not name_result.is_valid:
            errors.extend(name_result.errors)

        # Validate abbreviation
        abbr_input = self.query_one("#abbreviation", Input)
        abbr_result = validate_abbreviation(abbr_input.value)
        if not abbr_result.is_valid:
            errors.extend(abbr_result.errors)

        # Update validation errors
        self.validation_errors = "\n".join(errors)

        # Enable/disable create button
        create_btn = self.query_one("#create", Button)
        create_btn.disabled = len(errors) > 0

        if errors:
            logger.debug(f"Validation failed for unit '{self.unit_name}': {errors}")

        return len(errors) == 0

    def watch_validation_errors(self, errors: str) -> None:
        """Update validation errors display."""
        error_widget = self.query_one("#validation-errors", Static)
        error_widget.update(errors)

    @on(Button.Pressed, "#create")
    def on_create(self):
        # Final validation check
        if not self.validate_inputs():
            logger.warning("Attempted to create unit with validation errors")
            self.notify("Cannot create unit: validation errors", severity="error")
            return

        abbreviation = self.query_one("#abbreviation", Input).value
        description = self.query_one("#description", Input).value
        self.result = {
            "name": self.unit_name,
            "abbreviation": abbreviation,
            "description": description,
        }
        logger.info(f"Creating unit: {self.unit_name}")
        self.dismiss(self.result)

    @on(Button.Pressed, "#cancel")
    def on_cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)


class UnitActionModal(ModalScreen):
    """Modal for handling missing units"""

    CSS = """
    UnitActionModal {
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
        Binding("2", "skip", "Skip"),
    ]

    def __init__(self, unit_name: str):
        super().__init__()
        self.unit_name = unit_name
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"⚠ Unit '{self.unit_name}' not found")
            yield Button("1. Create New Unit", variant="primary", id="create")
            yield Button("2. Skip", variant="default", id="skip")
            yield Button("Q. Quit", variant="error", id="quit")

    @on(Button.Pressed, "#create")
    def action_create(self):
        self.result = "create"
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
