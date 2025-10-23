"""Mode selection screen - choose between Recipe Mode and Batch Mode."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from .pattern_group import PatternGroupScreen
from .recipe_list import RecipeListScreen


class ModeSelectionScreen(Screen):
    """Screen for selecting processing mode"""

    CSS = """
    ModeSelectionScreen {
        align: center middle;
        background: $surface;
    }

    #mode-container {
        width: 80;
        height: auto;
        background: $panel;
        border: thick $primary;
        padding: 2 3;
    }

    #title {
        text-align: center;
        margin: 1 0;
        text-style: bold;
        color: $accent;
    }

    #description {
        text-align: center;
        margin: 1 0 2 0;
        color: $text-muted;
    }

    .mode-section {
        margin: 1 0;
        padding: 1 2;
        background: $boost;
        border: round $primary-lighten-1;
        height: auto;
    }

    .mode-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .mode-description {
        color: $text;
        margin-bottom: 1;
    }

    .mode-section Button {
        width: 100%;
    }

    #quit-container {
        margin-top: 2;
        align: center middle;
    }

    #quit-btn {
        width: auto;
        min-width: 20;
    }
    """

    BINDINGS = [
        Binding("1", "recipe_mode", "Recipe Mode", show=True),
        Binding("2", "batch_mode", "Batch Mode", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(
        self,
        unparsed_recipes,
        session,
        known_units_full,
        known_foods_full,
        all_patterns=None,
    ):
        super().__init__()
        self.unparsed_recipes = unparsed_recipes
        self.session = session
        self.known_units_full = known_units_full
        self.known_foods_full = known_foods_full
        self.all_patterns = all_patterns or []

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="mode-container"):
            yield Static("Mealie Ingredient Parser", id="title")
            yield Static(
                f"Found {len(self.unparsed_recipes)} recipes with unparsed ingredients",
                id="description",
            )

            with Vertical(classes="mode-section"):
                yield Static("Recipe Mode", classes="mode-title")
                yield Static(
                    "Process recipes one at a time with interactive ingredient review",
                    classes="mode-description",
                )
                yield Button("Start Recipe Mode [1]", variant="primary", id="recipe-mode-btn")

            with Vertical(classes="mode-section"):
                yield Static("Batch Mode", classes="mode-title")
                yield Static(
                    "Parse ingredients in bulk using NLP, Brute Force, or OpenAI methods",
                    classes="mode-description",
                )
                yield Button("Start Batch Mode [2]", variant="success", id="batch-mode-btn")

            with Horizontal(id="quit-container"):
                yield Button("Quit [q]", variant="error", id="quit-btn")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "recipe-mode-btn":
            self.action_recipe_mode()
        elif event.button.id == "batch-mode-btn":
            self.action_batch_mode()
        elif event.button.id == "quit-btn":
            self.action_quit()

    def action_recipe_mode(self) -> None:
        """Switch to recipe-by-recipe processing mode"""
        self.app.push_screen(
            RecipeListScreen(
                self.unparsed_recipes,
                self.session,
                self.known_units_full,
                self.known_foods_full,
            )
        )

    def action_batch_mode(self) -> None:
        """Switch to batch processing mode"""
        # Use PatternGroupScreen with parsing workflow
        self.app.push_screen(
            PatternGroupScreen(
                patterns=self.all_patterns,
                unparsed_recipes=self.unparsed_recipes,
                session=self.session,
                known_units=self.known_units_full,
                known_foods=self.known_foods_full,
            )
        )

    def action_quit(self) -> None:
        self.app.exit()
