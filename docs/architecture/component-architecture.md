# Component Architecture

## Application Entry Point

**File:** `main.py`

```python
# Entry point
app = MealieParserApp()
app.run()
```

## Main Application Class

**File:** `mealie_parser/app.py`

```python
class MealieParserApp(App):
    """Main Textual application."""

    def __init__(self):
        super().__init__()
        self.session = None  # Will be set in on_mount

    async def on_mount(self):
        """Create persistent session and start app."""
        connector = aiohttp.TCPConnector(limit=10)
        self.session = aiohttp.ClientSession(
            headers=headers,  # From config.py
            connector=connector
        )
        self.push_screen(LoadingScreen())

    async def on_unmount(self):
        """Clean up session when app exits."""
        if self.session:
            await self.session.close()
```

**Key Responsibilities:**
- Session lifecycle management
- Initial screen navigation
- Global app state (session reference)

## Configuration Layer

**File:** `mealie_parser/config.py`

Loads environment variables from `.env` file:

```
MEALIE_URL=https://your-mealie-instance.com/api
MEALIE_API_KEY=your_api_key_here
```

**Exports:**
- `API_URL`: Base URL for Mealie API
- `headers`: HTTP headers with Bearer token authentication

---
