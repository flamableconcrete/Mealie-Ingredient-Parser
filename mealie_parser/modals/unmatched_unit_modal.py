"""Modal for handling unmatched unit patterns."""

from typing import Any

from loguru import logger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from mealie_parser.utils import find_unit_by_name


class UnmatchedUnitModal(ModalScreen[dict[str, Any] | None]):
    """
    Modal for handling unmatched unit patterns.

    This modal provides a focused interface for resolving unmatched unit patterns by:
    1. Displaying parsed unit with confidence score
    2. Allowing unit input/selection with dynamic action buttons
    3. Supporting re-parse functionality
    4. Intelligently determining whether to create new units or add aliases

    Parameters
    ----------
    pattern : PatternGroup
        The pattern data to process
    units : list[dict]
        All available units from Mealie instance
    parse_method : str
        The parsing method used (for re-parse functionality)

    Returns
    -------
    dict or None
        Action result dictionary if user takes action, None if cancelled
    """

    CSS = """
    UnmatchedUnitModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #modal-container {
        width: 80%;
        max-width: 100;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        height: 1;
    }

    #pattern-text {
        text-align: center;
        text-style: bold;
        color: $accent;
        background: $boost;
        padding: 0 1;
        height: 1;
        margin-bottom: 1;
    }

    #parse-results {
        background: $panel;
        padding: 1;
        height: auto;
        border: solid $primary;
        margin-bottom: 1;
    }

    .parse-result-row {
        height: 1;
    }

    .parse-result-label {
        color: $text-muted;
        width: 18;
    }

    .parse-result-value {
        color: $success;
        text-style: bold;
    }

    #content-section {
        border: solid $primary;
        padding: 1;
        height: auto;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        height: 1;
    }

    .field-label {
        height: 1;
        padding: 0;
        margin-top: 1;
    }

    Input {
        height: 3;
        margin: 0;
    }

    Select {
        height: 3;
        margin: 0;
    }

    .action-button {
        width: 100%;
        height: 3;
        margin-top: 1;
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

    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    # Reactive attributes for dynamic button text
    unit_button_text = reactive("")

    def __init__(
        self,
        pattern: Any,  # PatternGroup
        units: list[dict],
        parse_method: str = "nlp",
    ) -> None:
        """Initialize the unmatched unit modal."""
        super().__init__()
        self.pattern = pattern
        self.units = units
        self.parse_method = parse_method

        # Current input values
        self.unit_input_value = pattern.parsed_unit or ""

        # Original parsed values (for comparison)
        self.original_parsed_unit = pattern.parsed_unit or ""
        self.unit_confidence = getattr(pattern, "unit_confidence", 0.0)

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Container(id="modal-container"):
            yield Static("Unmatched Pattern", id="title")
            yield Static(self.pattern.pattern_text, id="pattern-text")

            # Parse results section
            with Container(id="parse-results"):
                with Horizontal(classes="parse-result-row"):
                    yield Label("Parsed Unit:", classes="parse-result-label")
                    yield Static(
                        self.original_parsed_unit or "(none)",
                        classes="parse-result-value",
                        id="parsed-unit-display",
                    )
                with Horizontal(classes="parse-result-row"):
                    yield Label("Confidence:", classes="parse-result-label")
                    yield Static(
                        f"{self.unit_confidence:.2f}",
                        classes="parse-result-value",
                        id="confidence-display",
                    )

            # Unit section
            with Vertical(id="content-section"):
                yield Static("UNIT", classes="section-title")
                yield Static("Name:", classes="field-label")
                yield Input(
                    value=self.unit_input_value,
                    placeholder="Enter unit name",
                    id="unit-input",
                )
                yield Static("Or select:", classes="field-label")
                yield Select(
                    sorted(
                        [(u["name"], u["id"]) for u in self.units],
                        key=lambda x: x[0].lower(),
                    ),
                    id="unit-select",
                    prompt="Choose a unit...",
                )
                yield Button(
                    "Unit Action",
                    id="unit-action",
                    variant="primary",
                    classes="action-button hidden",
                )

            # Bottom buttons
            with Horizontal(id="bottom-buttons"):
                yield Button("Reset / Re-parse", id="reset", variant="default")
                yield Button("Cancel", id="cancel", variant="default")

    def on_mount(self) -> None:
        """Update button states on mount."""
        self.update_unit_button()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "unit-input":
            self.unit_input_value = event.value
            self.update_unit_button()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "unit-select" and event.value != Select.BLANK:
            # Find selected unit name and update input
            for unit in self.units:
                if unit["id"] == event.value:
                    unit_input = self.query_one("#unit-input", Input)
                    unit_input.value = unit["name"]
                    self.unit_input_value = unit["name"]
                    self.update_unit_button()
                    break

    def update_unit_button(self) -> None:
        """
        Update unit button based on current state.

        Logic:
        1. parsed_unit == input AND input matches DB → NO button
        2. parsed_unit == input AND input NOT in DB → "Create missing unit: <value>"
        3. parsed_unit != input AND input matches DB → "Add alias for <DB_unit>: <parsed_unit>"
        4. parsed_unit != input AND input NOT in DB → "Create missing unit: <input>\nWith Alias: <parsed_unit>"
        """
        try:
            button = self.query_one("#unit-action", Button)

            current_input = self.unit_input_value.strip()
            parsed_unit = self.original_parsed_unit.strip()

            if not current_input:
                button.add_class("hidden")
                return

            # Check if input matches DB unit
            matching_unit = find_unit_by_name(current_input, self.units)

            if parsed_unit == current_input:
                if matching_unit:
                    # Case 1: Match exists, no action needed
                    button.add_class("hidden")
                else:
                    # Case 2: Create new unit
                    button.label = f"Create missing unit: {current_input}"
                    button.remove_class("hidden")
            else:
                if matching_unit:
                    # Case 3: Add alias
                    if parsed_unit:
                        button.label = f"Add alias for {current_input}: {parsed_unit}"
                    else:
                        button.label = f"Use existing unit: {current_input}"
                    button.remove_class("hidden")
                else:
                    # Case 4: Create with alias
                    if parsed_unit:
                        button.label = f"Create missing unit: {current_input} (with alias: {parsed_unit})"
                    else:
                        button.label = f"Create missing unit: {current_input}"
                    button.remove_class("hidden")

        except Exception as e:
            logger.error(f"Error updating unit button: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "unit-action":
            self._handle_unit_action()
        elif button_id == "reset":
            self._handle_reset()
        elif button_id == "cancel":
            self.action_cancel()

    def _handle_unit_action(self) -> None:
        """Handle unit action button press."""
        current_input = self.unit_input_value.strip()
        parsed_unit = self.original_parsed_unit.strip()
        matching_unit = find_unit_by_name(current_input, self.units)

        result: dict[str, Any] = {
            "action": "unit",
            "pattern": self.pattern.pattern_text,
        }

        if parsed_unit == current_input:
            if not matching_unit:
                # Create new unit
                result["operation"] = "create_unit"
                result["unit_name"] = current_input
        else:
            if matching_unit:
                # Add alias
                result["operation"] = "add_unit_alias"
                result["unit_id"] = matching_unit["id"]
                result["unit_name"] = matching_unit["name"]
                result["alias"] = parsed_unit if parsed_unit else current_input
            else:
                # Create with alias
                result["operation"] = "create_unit_with_alias"
                result["unit_name"] = current_input
                result["alias"] = parsed_unit if parsed_unit else None

        logger.info(f"Unit action: {result}")
        self.dismiss(result)

    def _handle_reset(self) -> None:
        """Handle reset/re-parse button press."""
        # Signal that re-parse is needed
        result = {
            "action": "reparse",
            "pattern": self.pattern.pattern_text,
            "method": self.parse_method,
        }
        logger.info(f"Re-parse requested: {result}")
        self.dismiss(result)

    def action_cancel(self) -> None:
        """Handle cancel action."""
        logger.info("UnmatchedUnitModal cancelled")
        self.dismiss(None)
