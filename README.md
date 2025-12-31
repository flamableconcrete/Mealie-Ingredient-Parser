# Mealie Ingredient Parser

**IMPORTANT NOTE**: This is close to 100% vibe-coded by Claude Code.
It doesn't work. I don't know if I am proud of myself yet either.
You have been warned!

A Terminal User Interface (TUI) application for processing unparsed recipe ingredients in your Mealie instance. This tool identifies recipes with unparsed ingredients, uses Mealie's built-in NLP parser to process them, and provides an interactive interface for creating missing units/foods or adding aliases to existing ones.

## Features

- **Pattern-Based Processing**: Groups similar unparsed ingredients for efficient batch processing
- **Interactive TUI**: Built with Textual for a modern terminal interface
- **Batch & Sequential Modes**: Process ingredients in bulk or one-by-one
- **Session Persistence**: Resume interrupted processing sessions
- **Smart Retry Logic**: Handles transient API errors with exponential backoff
- **Comprehensive Logging**: Detailed logs for troubleshooting

## Setup

1. **Install uv** (if not already installed):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Configure environment**:
   Copy `.env.example` to `.env` and fill in your values:

   ```bash
   cp .env.example .env
   ```

   Then edit `.env` with your Mealie credentials:
   - `MEALIE_API_KEY`: Your API key from Mealie (Settings -> API Tokens)
   - `MEALIE_URL`: Your Mealie instance URL ending with `/api`
   - Optional settings for batch size and column widths (see `.env.example` for details)

3. **Install dependencies**:

   ```bash
   uv sync
   ```

## Usage

Run the application:

```bash
uv run python main.py
```

The app will:

1. Connect to your Mealie instance
2. Analyze recipes for unparsed ingredients
3. Group similar patterns together
4. Guide you through creating missing units/foods or adding aliases
5. Update ingredients in batch

## Development

See [CLAUDE.md](CLAUDE.md) for detailed architecture, development commands, and code style guidelines.

### Quick Commands

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format

# Lint code
uv run ruff check --fix
```

## Requirements

- Python 3.13+
- A running Mealie instance with API access
- Mealie API key with appropriate permissions

## License

MIT
