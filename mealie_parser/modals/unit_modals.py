"""Modal screens for unit management."""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class CreateUnitModal(ModalScreen):
    """Modal for creating a new unit"""

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

    #button-container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, unit_name: str):
        super().__init__()
        self.unit_name = unit_name
        self.result = None

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label(f"Create New Unit: {self.unit_name}")
            yield Label("Abbreviation:")
            yield Input(value=self.unit_name[:3], id="abbreviation")
            yield Label("Description (optional):")
            yield Input(id="description")
            with Horizontal(id="button-container"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", variant="default", id="cancel")

    @on(Button.Pressed, "#create")
    def on_create(self):
        abbreviation = self.query_one("#abbreviation", Input).value
        description = self.query_one("#description", Input).value
        self.result = {
            "name": self.unit_name,
            "abbreviation": abbreviation,
            "description": description,
        }
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
