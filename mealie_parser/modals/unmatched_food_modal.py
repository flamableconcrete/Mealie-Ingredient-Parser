"""Modal for handling unmatched food patterns."""

from typing import Any

from loguru import logger
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from mealie_parser.utils import find_food_by_name


class UnmatchedFoodModal(ModalScreen[dict[str, Any] | None]):
    """
    Modal for handling unmatched food patterns.

    This modal provides a focused interface for resolving unmatched food patterns by:
    1. Displaying parsed food with confidence score
    2. Allowing food input/selection with dynamic action buttons
    3. Supporting re-parse functionality
    4. Intelligently determining whether to create new foods or add aliases

    Parameters
    ----------
    pattern : PatternGroup
        The pattern data to process
    foods : list[dict]
        All available foods from Mealie instance
    parse_method : str
        The parsing method used (for re-parse functionality)

    Returns
    -------
    dict or None
        Action result dictionary if user takes action, None if cancelled
    """

    CSS = """
    UnmatchedFoodModal {
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
    food_button_text = reactive("")

    def __init__(
        self,
        pattern: Any,  # PatternGroup
        foods: list[dict],
        parse_method: str = "nlp",
    ) -> None:
        """Initialize the unmatched food modal."""
        super().__init__()
        self.pattern = pattern
        self.foods = foods
        self.parse_method = parse_method

        # Current input values
        self.food_input_value = pattern.parsed_food or ""

        # Original parsed values (for comparison)
        self.original_parsed_food = pattern.parsed_food or ""
        self.food_confidence = getattr(pattern, "food_confidence", 0.0)

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Container(id="modal-container"):
            yield Static("Unmatched Pattern", id="title")
            yield Static(self.pattern.pattern_text, id="pattern-text")

            # Parse results section
            with Container(id="parse-results"):
                with Horizontal(classes="parse-result-row"):
                    yield Label("Parsed Food:", classes="parse-result-label")
                    yield Static(
                        self.original_parsed_food or "(none)",
                        classes="parse-result-value",
                        id="parsed-food-display",
                    )
                with Horizontal(classes="parse-result-row"):
                    yield Label("Confidence:", classes="parse-result-label")
                    yield Static(
                        f"{self.food_confidence:.2f}",
                        classes="parse-result-value",
                        id="confidence-display",
                    )

            # Food section
            with Vertical(id="content-section"):
                yield Static("FOOD", classes="section-title")
                yield Static("Name:", classes="field-label")
                yield Input(
                    value=self.food_input_value,
                    placeholder="Enter food name",
                    id="food-input",
                )
                yield Static("Or select:", classes="field-label")
                yield Select(
                    sorted(
                        [(f["name"], f["id"]) for f in self.foods],
                        key=lambda x: x[0].lower(),
                    ),
                    id="food-select",
                    prompt="Choose a food...",
                )
                yield Button(
                    "Food Action",
                    id="food-action",
                    variant="primary",
                    classes="action-button hidden",
                )

            # Bottom buttons
            with Horizontal(id="bottom-buttons"):
                yield Button("Reset / Re-parse", id="reset", variant="default")
                yield Button("Cancel", id="cancel", variant="default")

    def on_mount(self) -> None:
        """Update button states on mount."""
        self.update_food_button()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "food-input":
            self.food_input_value = event.value
            self.update_food_button()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "food-select" and event.value != Select.BLANK:
            # Find selected food name and update input
            for food in self.foods:
                if food["id"] == event.value:
                    food_input = self.query_one("#food-input", Input)
                    food_input.value = food["name"]
                    self.food_input_value = food["name"]
                    self.update_food_button()
                    break

    def update_food_button(self) -> None:
        """
        Update food button based on current state.

        Logic mirrors unit button logic.
        """
        try:
            button = self.query_one("#food-action", Button)

            current_input = self.food_input_value.strip()
            parsed_food = self.original_parsed_food.strip()

            # Debug logging
            logger.debug(f"update_food_button: current_input='{current_input}', parsed_food='{parsed_food}'")

            if not current_input:
                button.add_class("hidden")
                return

            # Check if input matches DB food
            matching_food = find_food_by_name(current_input, self.foods)
            logger.debug(f"update_food_button: matching_food={matching_food is not None}")

            if parsed_food == current_input:
                if matching_food:
                    # Case 1: Match exists, no action needed
                    button.add_class("hidden")
                else:
                    # Case 2: Create new food
                    button.label = f"Create missing food: {current_input}"
                    button.remove_class("hidden")
            else:
                if matching_food:
                    # Case 3: Add alias
                    if parsed_food:
                        button.label = f"Add alias for {current_input}: {parsed_food}"
                        logger.debug(f"Case 3: Add alias - button.label='{button.label}'")
                    else:
                        button.label = f"Use existing food: {current_input}"
                        logger.debug(f"Case 3: Use existing - button.label='{button.label}'")
                    button.remove_class("hidden")
                else:
                    # Case 4: Create with alias
                    if parsed_food:
                        button.label = f"Create missing food: {current_input} (with alias: {parsed_food})"
                        logger.debug(f"Case 4: Create with alias - button.label='{button.label}'")
                    else:
                        button.label = f"Create missing food: {current_input}"
                        logger.debug(f"Case 4: Create without alias - button.label='{button.label}'")
                    button.remove_class("hidden")

        except Exception as e:
            logger.error(f"Error updating food button: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "food-action":
            self._handle_food_action()
        elif button_id == "reset":
            self._handle_reset()
        elif button_id == "cancel":
            self.action_cancel()

    def _handle_food_action(self) -> None:
        """Handle food action button press."""
        current_input = self.food_input_value.strip()
        parsed_food = self.original_parsed_food.strip()
        matching_food = find_food_by_name(current_input, self.foods)

        result: dict[str, Any] = {
            "action": "food",
            "pattern": self.pattern.pattern_text,
        }

        if parsed_food == current_input:
            if not matching_food:
                # Create new food
                result["operation"] = "create_food"
                result["food_name"] = current_input
        else:
            if matching_food:
                # Add alias
                result["operation"] = "add_food_alias"
                result["food_id"] = matching_food["id"]
                result["food_name"] = matching_food["name"]
                result["alias"] = parsed_food if parsed_food else current_input
            else:
                # Create with alias
                result["operation"] = "create_food_with_alias"
                result["food_name"] = current_input
                result["alias"] = parsed_food if parsed_food else None

        logger.info(f"Food action: {result}")
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
        logger.info("UnmatchedFoodModal cancelled")
        self.dismiss(None)
