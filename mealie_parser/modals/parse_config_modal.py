"""Modal for configuring batch parsing parameters."""

from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Label, Select, Static


class ParseConfigModal(Screen[dict[str, str | int] | None]):
    """
    Modal for selecting parsing quantity and method.

    Returns
    -------
    dict or None
        {"quantity": int, "method": str} if user confirms, None if cancelled
    """

    CSS = """
    ParseConfigModal {
        layers: overlay;
        background: rgba(0, 0, 0, 0);
        align: center middle;
    }

    #dialog {
        width: 70;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
        layer: overlay;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        height: auto;
    }

    .field-row {
        height: auto;
        margin: 1 0;
    }

    .field-label {
        width: 20;
        height: auto;
        text-align: left;
        content-align: left middle;
    }

    Select {
        width: 1fr;
    }

    #openai-note {
        color: $warning;
        background: $boost;
        padding: 1;
        margin: 1 0;
        height: auto;
        text-align: center;
    }

    .hidden {
        display: none;
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
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        parsing_started: bool = False,
        single_item: bool = False,
        item_name: str = "",
    ) -> None:
        """Initialize the parse config modal.

        Parameters
        ----------
        parsing_started : bool
            Whether parsing has already started (shows filter dropdown)
        single_item : bool
            Whether this is for parsing a single item (hides quantity/filter dropdowns)
        item_name : str
            Name of the item being parsed (for single-item mode)
        """
        super().__init__()
        self.selected_method: str = "nlp"
        self.parsing_started = parsing_started
        self.single_item = single_item
        self.item_name = item_name

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Container(id="dialog"):
            # Title changes based on mode
            if self.single_item:
                yield Static(f"Parse Item: {self.item_name}", id="title")
            else:
                yield Static("Start Batch Parsing", id="title")

            # Quantity selection (only for batch mode)
            if not self.single_item:
                with Horizontal(classes="field-row"):
                    yield Label("Parse Quantity:", classes="field-label")
                    yield Select(
                        [
                            ("10 ingredients", "10"),
                            ("20 ingredients", "20"),
                            ("50 ingredients", "50"),
                            ("100 ingredients", "100"),
                            ("500 ingredients", "500"),
                            ("All ingredients", "all"),
                        ],
                        id="quantity-select",
                        value="10",
                    )

            # Method selection
            with Horizontal(classes="field-row"):
                yield Label("Parse Method:", classes="field-label")
                yield Select(
                    [
                        ("NLP (Natural Language Processing)", "nlp"),
                        ("Brute Force", "brute"),
                        ("OpenAI", "openai"),
                    ],
                    id="method-select",
                    value="nlp",
                )

            # Concurrency selection (only for batch mode)
            if not self.single_item:
                with Horizontal(classes="field-row"):
                    yield Label("Concurrent Parsing:", classes="field-label")
                    yield Select(
                        [
                            ("1", "1"),
                            ("2", "2"),
                            ("4 (recommended)", "4"),
                            ("8", "8"),
                            ("16", "16"),
                            ("32", "32"),
                        ],
                        id="concurrency-select",
                        value="4",
                    )

            # Filter selection (only for batch mode)
            if not self.single_item:
                with Horizontal(classes="field-row"):
                    yield Label("Filter:", classes="field-label")
                    yield Select(
                        [
                            ("Only parse pending", "pending"),
                            ("Parse pending and unmatched", "pending_unmatched"),
                            ("Parse all (will re-parse)", "all"),
                        ],
                        id="filter-select",
                        value="pending",
                    )

            # OpenAI note (hidden by default)
            yield Static(
                "⚠️ OpenAI method requires Mealie instance to be configured with OpenAI integration.\n"
                "See: https://docs.mealie.io/",
                id="openai-note",
                classes="hidden",
            )

            # Buttons
            with Horizontal(id="buttons"):
                yield Button("Cancel", id="cancel", variant="default")
                yield Button("Parse", id="parse", variant="primary")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select value changes."""
        if event.select.id == "method-select":
            self.selected_method = str(event.value)
            logger.debug(f"Method changed to: {self.selected_method}")

            # Show/hide OpenAI note
            try:
                note = self.query_one("#openai-note", Static)
                if self.selected_method == "openai":
                    note.remove_class("hidden")
                else:
                    note.add_class("hidden")
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "parse":
            logger.debug("Parse button pressed")
            method_select = self.query_one("#method-select", Select)
            method_value = str(method_select.value)

            result = {
                "method": method_value,
            }

            # For batch mode, include quantity and filter
            if not self.single_item:
                quantity_select = self.query_one("#quantity-select", Select)
                quantity_value = str(quantity_select.value)

                # Convert quantity to int or -1 for "all"
                if quantity_value == "all":
                    quantity_int = -1
                else:
                    quantity_int = int(quantity_value)

                result["quantity"] = quantity_int

                # Add filter from select widget
                try:
                    filter_select = self.query_one("#filter-select", Select)
                    result["filter"] = str(filter_select.value)
                except Exception:
                    result["filter"] = "all"  # Safe default

                # Add concurrency from select widget
                try:
                    concurrency_select = self.query_one("#concurrency-select", Select)
                    concurrency_value = str(concurrency_select.value)
                    result["concurrency"] = int(concurrency_value)
                except (ValueError, Exception):
                    result["concurrency"] = 4  # Safe default
            else:
                # For single-item mode, set quantity to 1
                result["quantity"] = 1
                result["filter"] = "single"

            logger.info(f"{'Single-item' if self.single_item else 'Batch'} parsing configured: {result}")
            self.dismiss(result)

        elif event.button.id == "cancel":
            logger.debug("Cancel button pressed")
            self.action_cancel()

    def action_cancel(self) -> None:
        """Handle cancel action."""
        logger.info("Parse config cancelled by user")
        self.dismiss(None)
