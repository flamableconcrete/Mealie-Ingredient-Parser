"""Modal for viewing all Unit and Food data from Mealie server."""

from loguru import logger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static, TabbedContent, TabPane

from mealie_parser.config import API_URL


class DataManagementModal(ModalScreen[None]):
    """
    Wide modal for viewing all Unit and Food data from the Mealie server.

    This modal provides a read-only view of all available units and foods:
    - Unit Data: name, plural name, abbreviation, plural abbreviation
    - Food Data: name, plural name, description

    Parameters
    ----------
    units : list[dict]
        All available units from Mealie instance
    foods : list[dict]
        All available foods from Mealie instance

    Returns
    -------
    None
        Modal is informational only, no return value
    """

    CSS = """
    DataManagementModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #modal-container {
        width: 95%;
        max-width: 140;
        height: 85%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        height: 1;
        margin-bottom: 1;
    }

    #info-text {
        text-align: center;
        color: $text-muted;
        height: 1;
        margin-bottom: 1;
    }

    #count-display {
        text-align: center;
        color: $accent;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }

    TabbedContent {
        height: 1fr;
        border: solid $primary;
    }

    DataTable {
        height: 1fr;
    }

    .tab-link {
        text-align: center;
        color: $accent;
        height: 1;
        margin-bottom: 1;
    }

    #bottom-buttons {
        layout: horizontal;
        align: center middle;
        height: 3;
        margin-top: 1;
    }

    #bottom-buttons Button {
        margin: 0 1;
        height: 3;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("ctrl+t", "switch_tab", "Switch Tab"),
    ]

    def __init__(
        self,
        units: list[dict],
        foods: list[dict],
    ) -> None:
        """Initialize the data management modal."""
        super().__init__()
        self.units = units
        self.foods = foods

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        # Get base URL without /api suffix for web UI links
        base_url = API_URL.removesuffix("/api") if API_URL else ""

        with Container(id="modal-container"):
            yield Static("Data Management", id="title")
            yield Static(
                "All available Unit and Food data from the Mealie server",
                id="info-text",
            )
            yield Static(
                f"Total Food Items: {len(self.foods)}",
                id="count-display",
            )

            with TabbedContent(initial="foods"):
                with TabPane("Food Data", id="foods"):
                    yield Static(f"Source: {base_url}/group/data/foods", classes="tab-link")
                    yield DataTable(id="food-table")
                with TabPane("Unit Data", id="units"):
                    yield Static(f"Source: {base_url}/group/data/units", classes="tab-link")
                    yield DataTable(id="unit-table")

            with Container(id="bottom-buttons"):
                yield Button("Close [escape]", id="close", variant="primary")

    def on_mount(self) -> None:
        """Initialize tables when modal mounts."""
        logger.debug("Mounting DataManagementModal, populating tables")

        # Setup unit table
        unit_table = self.query_one("#unit-table", DataTable)
        unit_table.add_column("Name", width=25)
        unit_table.add_column("Plural Name", width=25)
        unit_table.add_column("Abbreviation", width=15)
        unit_table.add_column("Plural Abbreviation", width=20)
        unit_table.cursor_type = "row"

        # Populate unit table
        for unit in sorted(self.units, key=lambda u: u.get("name", "").lower()):
            unit_table.add_row(
                unit.get("name", ""),
                unit.get("pluralName", ""),
                unit.get("abbreviation", ""),
                unit.get("pluralAbbreviation", ""),
            )

        # Setup food table
        food_table = self.query_one("#food-table", DataTable)
        food_table.add_column("Name", width=30)
        food_table.add_column("Plural Name", width=30)
        food_table.add_column("Description", width=50)
        food_table.cursor_type = "row"

        # Populate food table
        for food in sorted(self.foods, key=lambda f: f.get("name", "").lower()):
            food_table.add_row(
                food.get("name", ""),
                food.get("pluralName", ""),
                food.get("description", ""),
            )

        logger.info(f"Data Management Modal loaded: {len(self.units)} units, {len(self.foods)} foods")

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        """Update count display when switching tabs."""
        count_display = self.query_one("#count-display", Static)

        if event.pane.id == "foods":
            count_display.update(f"Total Food Items: {len(self.foods)}")
        elif event.pane.id == "units":
            count_display.update(f"Total Unit Items: {len(self.units)}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "close":
            self.action_close()

    def action_switch_tab(self) -> None:
        """Switch between Food and Unit tabs."""
        tabbed_content = self.query_one(TabbedContent)
        # Toggle between the two tabs
        if tabbed_content.active == "foods":
            tabbed_content.active = "units"
        else:
            tabbed_content.active = "foods"
        logger.debug(f"Switched to tab: {tabbed_content.active}")

    def action_close(self) -> None:
        """Handle close action."""
        logger.info("DataManagementModal closed")
        self.dismiss(None)
