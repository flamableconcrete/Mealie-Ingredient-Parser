"""Batch action selection modal for pattern groups."""

from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class BatchActionModal(ModalScreen[str]):
    """
    Modal for selecting batch action for a pattern group.

    Allows user to choose between creating new unit/food, adding alias to existing,
    reviewing individual ingredients, or skipping the pattern.

    Attributes
    ----------
    pattern_text : str
        The pattern text being processed
    ingredient_count : int
        Number of ingredients affected by this pattern
    recipe_count : int
        Number of recipes containing ingredients with this pattern

    Returns
    -------
    str or None
        Action type: "create_new", "add_alias", "review_individual", "skip", or None if cancelled
    """

    CSS = """
    BatchActionModal {
        align: center middle;
    }

    #dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    #stats {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    #prompt {
        text-align: center;
        margin-bottom: 1;
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
        ("1", "create_new", "Create New"),
        ("2", "add_alias", "Add Alias"),
        ("3", "review_individual", "Review Individual"),
        ("4", "skip", "Skip"),
    ]

    def __init__(
        self,
        pattern_text: str,
        ingredient_count: int,
        recipe_count: int,
    ):
        """
        Initialize batch action modal.

        Parameters
        ----------
        pattern_text : str
            The pattern text being processed
        ingredient_count : int
            Number of ingredients affected by this pattern
        recipe_count : int
            Number of recipes containing ingredients with this pattern
        """
        super().__init__()
        self.pattern_text = pattern_text
        self.ingredient_count = ingredient_count
        self.recipe_count = recipe_count

    def compose(self) -> ComposeResult:
        """Compose the modal layout."""
        with Container(id="dialog"):
            yield Static(
                f'Batch Action: "{self.pattern_text}"',
                id="title",
            )
            yield Static(
                f"{self.ingredient_count} ingredients across {self.recipe_count} recipes",
                id="stats",
            )
            yield Static("Choose an action:", id="prompt")
            yield Button("[1] Create New", id="create_new", variant="primary")
            yield Button("[2] Add Alias to Existing", id="add_alias")
            yield Button("[3] Review Individual", id="review_individual")
            yield Button("[4] Skip Pattern", id="skip")
            yield Static(
                "[Enter] Confirm  [Esc] Cancel",
                id="help",
            )

    def action_create_new(self) -> None:
        """Handle create new action."""
        logger.debug(f"User selected 'Create New' for pattern: {self.pattern_text}")
        self.dismiss("create_new")

    def action_add_alias(self) -> None:
        """Handle add alias action."""
        logger.debug(f"User selected 'Add Alias' for pattern: {self.pattern_text}")
        self.dismiss("add_alias")

    def action_review_individual(self) -> None:
        """Handle review individual action."""
        logger.debug(f"User selected 'Review Individual' for pattern: {self.pattern_text}")
        self.dismiss("review_individual")

    def action_skip(self) -> None:
        """Handle skip action."""
        logger.debug(f"User selected 'Skip' for pattern: {self.pattern_text}")
        self.dismiss("skip")

    def action_cancel(self) -> None:
        """Handle cancel action."""
        logger.debug(f"User cancelled batch action for pattern: {self.pattern_text}")
        self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        button_id = event.button.id
        if button_id == "create_new":
            self.action_create_new()
        elif button_id == "add_alias":
            self.action_add_alias()
        elif button_id == "review_individual":
            self.action_review_individual()
        elif button_id == "skip":
            self.action_skip()
