# Mealie Ingredient Parser

A Terminal User Interface (TUI) application for processing unparsed recipe ingredients in your Mealie instance.
This tool identifies recipes with unparsed ingredients, uses Mealie's built-in NLP parser to process them, and provides an interactive interface for creating missing units/foods or adding aliases to existing ones.

---

## ✨ Features

### Core Capabilities

- **Dual Processing Modes** — Recipe-by-recipe review or bulk batch processing
- **Pattern Recognition** — Intelligent grouping of similar unparsed ingredients for efficient batch operations
- **Session Persistence** — Save and resume work sessions automatically
- **Multiple Parsing Methods** — BRUTE (aggressive matching), NLPM (NLP-based), or combined approaches
- **Smart Unit Matching** — Configurable fuzzy matching for unit variations (e.g., "cups" → "cup")
- **Real-time Progress Tracking** — Live statistics for units, foods, and aliases created

### User Experience

- **Interactive Modals** — Guided workflows for creating units/foods or adding aliases
- **Data Management** — Built-in tools for reviewing and managing created units/foods
- **Async Performance** — Built with `aiohttp` for fast, concurrent API operations
- **Modern TUI** — Clean, intuitive interface powered by [Textual](https://textual.textualize.io)

### Technical Features

- **Automatic Detection** — Scans your Mealie instance to find all recipes with unparsed ingredients
- **NLP Parsing** — Leverages Mealie's NLP parser to extract structured ingredient data
- **Code Quality** — Strict linting with ruff, NumPy-style docstrings, comprehensive type hints
- **Structured Logging** — Detailed operation logging with loguru

---

## 🧩 Requirements

- Python ≥ 3.13
- A running Mealie instance with API access
- Mealie API key with appropriate permissions

---

## ⚙️ Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Install dependencies
uv sync

# Or install development dependencies
uv sync --group dev
```

**Production Dependencies:**
- aiohttp ≥ 3.13.0
- loguru ≥ 0.7.3
- python-dotenv ≥ 1.1.1
- rich ≥ 14.1.0
- textual ≥ 6.2.1

**Development Dependencies:**
- pytest ≥ 8.4.2
- pytest-asyncio ≥ 1.2.0
- ruff ≥ 0.9.0
- vulture ≥ 2.14

---

## 🔐 Configuration

Create a `.env` file in the project root with your Mealie credentials:

```env
MEALIE_API_KEY=your_api_key_here
MEALIE_URL=https://your-mealie-instance.com/api
```

**Environment Variables:**

- `MEALIE_API_KEY` — Your Mealie API bearer token
- `MEALIE_URL` — Base URL for the Mealie API (include `/api` path)

**Session Data:**

The application automatically saves session state to `.ai/session-state.json` for resuming work. This directory is git-ignored.

---

## 🚀 Usage

Run the application:

```bash
python main.py
# or
uv run main.py
```

### Application Workflow

#### 1. **Startup & Loading**
The app fetches all recipes, units, and foods from your Mealie instance and identifies recipes with unparsed ingredients.

#### 2. **Mode Selection**
Choose your processing approach:
- **Recipe Mode** — Review and process ingredients recipe-by-recipe with full control
- **Batch Mode** — Process groups of similar ingredients in bulk for efficiency

#### 3. **Recipe Mode Workflow**
1. View recipes with unparsed ingredients in a sortable table
2. Select a recipe to review its unparsed ingredients
3. For each ingredient, the app will:
   - Attempt to parse using Mealie's NLP parser
   - Prompt for missing units (create new or skip)
   - Prompt for missing foods (create new, add alias to existing, or skip)
4. Track progress with real-time statistics
5. Move to next recipe or return to list

#### 4. **Batch Mode Workflow**
1. **Pattern Analysis** — View groups of similar unparsed ingredients
2. **Select Pattern Group** — Choose a group to process (e.g., all "cup" units)
3. **Configure Parsing** — Select parsing method:
   - **BRUTE** — Aggressive matching with fuzzy logic
   - **NLPM** — NLP-based parsing (default)
   - **Both** — Try both methods for comprehensive results
4. **Batch Processing** — Process all ingredients in the group:
   - Preview parsed results in a table
   - Handle unmatched units/foods via modals
   - Bulk update all affected recipes
5. **Next Pattern** — Continue with other pattern groups

#### 5. **Session Management**
- Sessions are automatically saved to `.ai/session-state.json`
- Resume previous work session on startup
- Track cumulative statistics across sessions

#### 6. **Data Management**
Access the data management modal (varies by screen) to:
- Review all created units and foods
- Delete incorrect entries
- View summary statistics

---

## 🧠 How It Works

### Unparsed Detection

An ingredient is considered *unparsed* when it has a `note` or `originalText` but no associated `food.id` or `unit.id`.

### Parsing Process

**Recipe Mode:**
1. Identifies all unparsed recipes
2. Sends each unparsed ingredient to Mealie's NLP parser
3. Detects missing units/foods in the parsed result
4. Provides interactive prompts to resolve missing data
5. Updates the recipe with newly parsed ingredients

**Batch Mode:**
1. Analyzes all unparsed ingredients to identify common patterns
2. Groups similar ingredients (e.g., all ingredients with "cup" as unit)
3. Applies selected parsing method to entire group
4. Handles unmatched units/foods with batch actions
5. Updates all affected recipes simultaneously

### Pattern Analysis

The pattern analyzer (`mealie_parser/services/pattern_analyzer.py`) groups ingredients by:
- **Unit patterns** — Common unit strings (e.g., "cup", "tablespoon")
- **Food patterns** — Common food strings (e.g., "flour", "sugar")
- **Frequency** — Number of occurrences to prioritize high-impact patterns

### Parsing Methods

- **BRUTE** — Uses aggressive fuzzy matching and string manipulation to find matches
- **NLPM** — Uses Mealie's built-in NLP parser for intelligent extraction
- **Both** — Attempts BRUTE first, falls back to NLPM if no match found

---

## 🗂️ Project Structure

```
mealie-testing/
├── main.py                           # Application entry point
├── mealie_parser/
│   ├── app.py                        # Main Textual app with session management
│   ├── api.py                        # Mealie API client functions
│   ├── config.py                     # Environment configuration
│   ├── error_handling.py             # Error handling utilities
│   ├── logging_config.py             # Loguru configuration
│   ├── session_manager.py            # Session persistence manager
│   ├── utils.py                      # Helper utilities
│   ├── validation.py                 # Input validation
│   │
│   ├── constants/
│   │   └── pattern_display.py        # Pattern display constants
│   │
│   ├── models/
│   │   ├── pattern.py                # Pattern data models
│   │   ├── screen_state.py           # Screen state models
│   │   └── session_state.py          # Session state models
│   │
│   ├── screens/
│   │   ├── loading.py                # Initial data loading screen
│   │   ├── mode_selection.py         # Recipe/Batch mode selection
│   │   ├── recipe_list.py            # Recipe list view (Recipe Mode)
│   │   ├── ingredient_review.py      # Ingredient review screen (Recipe Mode)
│   │   ├── pattern_group.py          # Pattern group list (Batch Mode)
│   │   ├── batch_parsing.py          # Batch parsing with method selection
│   │   ├── batch_preview.py          # Preview parsed batch results
│   │   └── batch_units.py            # Batch unit assignment screen
│   │
│   ├── modals/
│   │   ├── batch_action_modal.py     # Batch processing actions
│   │   ├── data_management_modal.py  # Review/delete created data
│   │   ├── food_modals.py            # Food creation/selection modals
│   │   ├── parse_config_modal.py     # Parsing method configuration
│   │   ├── session_resume_modal.py   # Session resume prompt
│   │   ├── unit_modals.py            # Unit creation modals
│   │   ├── unmatched_food_modal.py   # Handle unmatched foods in batch
│   │   └── unmatched_unit_modal.py   # Handle unmatched units in batch
│   │
│   └── services/
│       ├── parse_result_processor.py # Parse result processing logic
│       ├── pattern_analyzer.py       # Pattern detection and grouping
│       └── table_manager.py          # DataTable management utilities
│
├── docs/
│   └── STYLE_GUIDE.md                # Python coding standards
├── pyproject.toml                    # Project metadata and ruff configuration
├── requirements.txt                  # Minimal pip requirements
├── CLAUDE.md                         # Claude Code instructions
└── README.md                         # This file
```

### Key Files

- **main.py** — Entry point that instantiates and runs `MealieParserApp`
- **mealie_parser/app.py** — Main Textual app with persistent aiohttp session
- **mealie_parser/api.py** — All Mealie REST API interactions (recipes, units, foods, parsing)
- **mealie_parser/session_manager.py** — Handles saving/loading session state to `.ai/session-state.json`
- **mealie_parser/services/pattern_analyzer.py** — Core pattern detection logic for batch mode
- **mealie_parser/services/parse_result_processor.py** — Processes parsing results and handles missing data

---

## 🛠️ Development

### Code Quality

This project follows strict Python coding standards:

```bash
# Format code
uv run ruff format .

# Check for issues
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .
```

See [STYLE_GUIDE.md](docs/STYLE_GUIDE.md) for complete coding standards.

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=mealie_parser
```

### Logging

Application logs are written to `mealie_parser.log` using loguru. Configure log level in `mealie_parser/logging_config.py`.

---

## 📋 Features Roadmap

- [x] Recipe-by-recipe ingredient review
- [x] Batch processing with pattern recognition
- [x] Multiple parsing methods (BRUTE, NLPM)
- [x] Session persistence and resume
- [x] Data management tools
- [x] Fuzzy unit matching
- [ ] Custom pattern definitions
- [ ] Export/import session data
- [ ] Undo/redo functionality
- [ ] Advanced filtering and search

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Follow the coding standards in [STYLE_GUIDE.md](docs/STYLE_GUIDE.md)
2. Run `uv run ruff format` and `uv run ruff check --fix` before committing
3. Add tests for new functionality
4. Update documentation as needed

---

## 📄 License

This project is provided as-is for use with Mealie instances.

---

## 🙏 Acknowledgments

- [Mealie](https://mealie.io/) — The recipe management platform this tool supports
- [Textual](https://textual.textualize.io/) — The amazing TUI framework
- [ruff](https://github.com/astral-sh/ruff) — Fast Python linter and formatter
