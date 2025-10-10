"""Main application class for Mealie Ingredient Parser."""

import aiohttp
from textual.app import App

from .config import headers
from .screens import LoadingScreen


class MealieParserApp(App):
    """Main Textual app for Mealie ingredient parsing"""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    TITLE = "Mealie Ingredient Parser"

    def __init__(self):
        super().__init__()
        self.session = None

    async def on_mount(self):
        # Create persistent session
        connector = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(headers=headers, connector=connector)
        self.push_screen(LoadingScreen())

    async def on_unmount(self):
        # Clean up session when app exits
        if self.session:
            await self.session.close()
