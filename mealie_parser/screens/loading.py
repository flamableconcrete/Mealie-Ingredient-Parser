"""Loading screen while fetching initial data."""

import asyncio

from loguru import logger
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Label, LoadingIndicator, ProgressBar

from ..api import get_all_recipes, get_foods_full, get_recipe_details, get_units_full
from ..modals.session_resume_modal import SessionResumeModal
from ..services.pattern_analyzer import PatternAnalyzer
from ..session_manager import SessionManager
from ..utils import is_recipe_unparsed
from .mode_selection import ModeSelectionScreen


class LoadingScreen(Screen):
    """Loading screen while fetching initial data"""

    CSS = """
    LoadingScreen {
        background: $surface;
        align: center middle;
    }

    #loading-container {
        width: 80;
        height: auto;
        background: $panel;
        border: thick $primary;
        padding: 2 4;
        align-horizontal: center;
    }

    #loading-title {
        text-align: center;
        margin: 0 0 1 0;
        height: 1;
    }

    #loading-indicator {
        width: auto;
        height: 1;
        margin: 0 0 1 0;
        content-align: center middle;
    }

    #loading-subtitle {
        text-align: center;
        margin: 0 0 1 0;
    }

    Label {
        text-align: center;
        margin: 0;
    }

    ProgressBar {
        margin: 0 0 1 0;
    }

    .progress-label {
        text-align: center;
        color: $text-muted;
        height: 1;
        margin: 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="loading-container"):
            yield Label("[bold cyan]MEALIE INGREDIENT PARSER[/]", id="loading-title")
            yield LoadingIndicator(id="loading-indicator")
            yield Label(
                "[italic dim]Fetching recipes, units, and foods[/]",
                id="loading-subtitle",
            )
            yield Label("", id="recipes-label", classes="progress-label")
            yield ProgressBar(id="recipes-progress", show_eta=False)
            yield Label("", id="units-label", classes="progress-label")
            yield ProgressBar(id="units-progress", show_eta=False)
            yield Label("", id="foods-label", classes="progress-label")
            yield ProgressBar(id="foods-progress", show_eta=False)
            yield Label("Finding unparsed recipes...", id="unparsed-label", classes="progress-label")
            yield ProgressBar(id="unparsed-progress", show_eta=False)

    async def on_mount(self):
        # Initialize all progress bars to prevent animation before they're used
        self.query_one("#recipes-progress", ProgressBar).update(total=1, progress=0)
        self.query_one("#units-progress", ProgressBar).update(total=1, progress=0)
        self.query_one("#foods-progress", ProgressBar).update(total=1, progress=0)
        self.query_one("#unparsed-progress", ProgressBar).update(total=1, progress=0)

        # Load data in background
        asyncio.create_task(self.load_data())

    async def _handle_existing_session(self) -> None:
        """Check for and handle existing session state.

        Sets self.app.session_state based on user choice.
        """
        session_manager = SessionManager()
        if session_manager.session_exists():
            logger.info("Found existing session - prompting user to resume")
            try:
                previous_session = session_manager.load_session()
                logger.debug(f"Loaded previous session: {previous_session.summary}")

                # Show resume modal
                resume = await self.app.push_screen_wait(SessionResumeModal(previous_session))

                if resume:
                    logger.info("User chose to resume session")
                    # Store session state in app for later use
                    self.app.session_state = previous_session
                else:
                    logger.info("User chose to start fresh - clearing old session")
                    session_manager.clear_session()
                    self.app.session_state = None
            except Exception as e:
                logger.error(f"Error loading previous session: {e}", exc_info=True)
                self.notify(
                    "Error loading previous session - starting fresh",
                    severity="warning",
                )
                session_manager.clear_session()
                self.app.session_state = None
        else:
            logger.info("No existing session found")
            self.app.session_state = None

    async def _fetch_recipes(self, session) -> list:
        """Fetch all recipes with progress tracking.

        Parameters
        ----------
        session
            aiohttp session for API calls

        Returns
        -------
        list
            List of recipe objects
        """
        recipes_label = self.query_one("#recipes-label", Label)
        recipes_progress = self.query_one("#recipes-progress", ProgressBar)
        recipes_label.update("Fetching recipes...")
        recipes = await get_all_recipes(session)
        recipes_progress.update(total=100, progress=100)
        recipes_label.update(f"Fetched {len(recipes)} recipes")
        return recipes

    async def _fetch_units(self, session) -> list:
        """Fetch all units with progress tracking.

        Parameters
        ----------
        session
            aiohttp session for API calls

        Returns
        -------
        list
            List of unit objects
        """
        units_label = self.query_one("#units-label", Label)
        units_progress = self.query_one("#units-progress", ProgressBar)
        units_label.update("Fetching units...")

        def update_units_progress(current, total):
            units_progress.update(total=total, progress=current)
            units_label.update(f"Fetching units... {current}/{total}")

        known_units_full = await get_units_full(session, progress_callback=update_units_progress)
        units_label.update(f"Fetched {len(known_units_full)} units")
        return known_units_full

    async def _fetch_foods(self, session) -> list:
        """Fetch all foods with progress tracking.

        Parameters
        ----------
        session
            aiohttp session for API calls

        Returns
        -------
        list
            List of food objects
        """
        foods_label = self.query_one("#foods-label", Label)
        foods_progress = self.query_one("#foods-progress", ProgressBar)
        foods_label.update("Fetching foods...")

        def update_foods_progress(current, total):
            foods_progress.update(total=total, progress=current)
            foods_label.update(f"Fetching foods... {current}/{total}")

        known_foods_full = await get_foods_full(session, progress_callback=update_foods_progress)
        foods_label.update(f"Fetched {len(known_foods_full)} foods")
        return known_foods_full

    async def _find_unparsed_recipes(self, session, recipes: list) -> tuple[list, list]:
        """Find recipes with unparsed ingredients.

        Parameters
        ----------
        session
            aiohttp session for API calls
        recipes : list
            List of all recipes

        Returns
        -------
        tuple[list, list]
            Tuple of (unparsed_recipes, unparsed_recipe_details)
        """
        logger.info(f"Checking {len(recipes)} recipes for unparsed ingredients")
        unparsed_progress = self.query_one("#unparsed-progress", ProgressBar)

        unparsed_progress.update(total=len(recipes), progress=0)

        unparsed_recipes = []
        unparsed_recipe_details = []

        for idx, recipe in enumerate(recipes, 1):
            try:
                details = await get_recipe_details(session, recipe["slug"])
                recipe_ingredients = details.get("recipeIngredient") or []

                if recipe_ingredients and is_recipe_unparsed(recipe_ingredients):
                    unparsed_recipes.append(recipe)
                    unparsed_recipe_details.append(details)

                # Update progress
                unparsed_progress.update(progress=idx)
            except Exception as e:
                logger.error(
                    f"Error checking recipe '{recipe.get('name', 'unknown')}' (slug: {recipe.get('slug', 'unknown')}): {e}",
                    exc_info=True,
                )
                # Continue processing other recipes

        logger.info(f"Found {len(unparsed_recipes)} recipes with unparsed ingredients")
        return unparsed_recipes, unparsed_recipe_details

    async def load_data(self) -> None:
        """Load all data and initialize application."""
        try:
            logger.info("Starting data load process")
            # Use the app's persistent session
            session = self.app.session

            # Check for existing session
            await self._handle_existing_session()

            # Load all data with progress tracking
            logger.info("Fetching recipes, units, and foods")

            recipes = await self._fetch_recipes(session)
            known_units_full = await self._fetch_units(session)
            known_foods_full = await self._fetch_foods(session)

            # Find unparsed recipes
            unparsed_recipes, unparsed_recipe_details = await self._find_unparsed_recipes(session, recipes)

            if not unparsed_recipes:
                self.notify("No unparsed recipes found!", severity="warning", timeout=3)
                logger.warning("No unparsed recipes found - exiting application")
                self.app.exit()
                return

            # Perform pattern analysis
            logger.info("Starting pattern analysis")
            analyzer = PatternAnalyzer()

            # Extract unparsed ingredients from all recipes (use full details, not summaries)
            unparsed_ingredients = analyzer.extract_unparsed_ingredients(unparsed_recipe_details)
            logger.info(f"Extracted {len(unparsed_ingredients)} unparsed ingredients")

            # Group into unified pattern list (same patterns shown in both tabs)
            all_patterns = analyzer.group_all_patterns(unparsed_ingredients)

            logger.info(f"Pattern analysis complete: {len(all_patterns)} unique patterns found")

            # Store pattern groups in screen state for later use
            self.all_patterns = all_patterns

            # Switch to mode selection screen
            self.app.push_screen(
                ModeSelectionScreen(
                    unparsed_recipes,
                    session,
                    known_units_full,
                    known_foods_full,
                    all_patterns,
                )
            )

        except Exception as e:
            logger.error(f"Critical error during data load: {e}", exc_info=True)
            self.notify(f"Error loading data: {e}", severity="error", timeout=3)
            self.app.exit()
