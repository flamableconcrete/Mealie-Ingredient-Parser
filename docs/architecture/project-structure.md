# Project Structure

```plaintext
mealie-testing/
├── .env                              # Environment configuration (MEALIE_API_KEY, MEALIE_URL)
├── .python-version                   # Python version specification (3.13)
├── pyproject.toml                    # uv project dependencies and metadata
├── uv.lock                           # Locked dependency versions
├── main.py                           # Application entry point
│
├── mealie_parser/                    # Main application package
│   ├── __init__.py
│   ├── app.py                        # MealieParserApp - main Textual app class
│   ├── config.py                     # Configuration loading (.env → settings)
│   ├── api.py                        # Mealie API client functions
│   ├── utils.py                      # Shared utilities (is_recipe_unparsed, etc.)
│   │
│   ├── models/                       # Data models (NEW for Epic 1)
│   │   ├── __init__.py
│   │   ├── pattern.py                # PatternGroup data class
│   │   ├── batch_operation.py        # BatchOperation data class
│   │   └── state.py                  # Session state model for persistence
│   │
│   ├── screens/                      # Textual screen components
│   │   ├── __init__.py
│   │   ├── loading.py                # LoadingScreen - data fetch + pattern analysis
│   │   ├── recipe_list.py            # RecipeListScreen - unparsed recipe table
│   │   ├── ingredient_review.py      # IngredientReviewScreen - sequential mode
│   │   ├── pattern_group.py          # PatternGroupScreen - batch mode (NEW)
│   │   └── batch_preview.py          # BatchPreviewScreen - confirmation dialog (NEW)
│   │
│   ├── modals/                       # Modal dialog components
│   │   ├── __init__.py
│   │   ├── unit_action.py            # UnitActionModal - create/skip unit
│   │   ├── create_unit.py            # CreateUnitModal - unit creation form
│   │   ├── food_action.py            # FoodActionModal - create/alias/skip food
│   │   ├── create_food.py            # CreateFoodModal - food creation form
│   │   ├── select_food.py            # SelectFoodModal - searchable food table
│   │   ├── pattern_action.py         # PatternActionModal - batch action selector (NEW)
│   │   ├── progress_dashboard.py     # ProgressDashboardModal - stats display (NEW)
│   │   └── operation_summary.py      # OperationSummaryModal - batch result (NEW)
│   │
│   ├── widgets/                      # Reusable widget components (NEW)
│   │   ├── __init__.py
│   │   ├── status_badge.py           # StatusBadge - pattern status indicator
│   │   ├── progress_bar.py           # ProgressBar - completion percentage
│   │   └── help_footer.py            # HelpFooter - context-sensitive shortcuts
│   │
│   ├── services/                     # Business logic services (NEW for Epic 1)
│   │   ├── __init__.py
│   │   ├── pattern_analyzer.py       # Pattern extraction and grouping logic
│   │   ├── similarity_matcher.py     # Fuzzy matching for similar patterns
│   │   ├── batch_processor.py        # Batch operation execution and error handling
│   │   └── state_manager.py          # Session state persistence and recovery
│   │
│   └── styles/                       # Textual CSS stylesheets
│       ├── __init__.py
│       ├── app.tcss                  # Global app styles and theme variables
│       ├── screens.tcss              # Screen-specific styles
│       ├── modals.tcss               # Modal dialog styles
│       └── widgets.tcss              # Custom widget styles
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures (mock API, test data)
│   │
│   ├── unit/                         # Unit tests
│   │   ├── test_pattern_analyzer.py  # Pattern grouping logic tests
│   │   ├── test_similarity_matcher.py # Fuzzy matching tests
│   │   ├── test_batch_processor.py   # Batch operation logic tests
│   │   └── test_state_manager.py     # State persistence tests
│   │
│   ├── integration/                  # Integration tests
│   │   ├── test_api.py               # API layer with mocked responses
│   │   └── test_batch_workflows.py   # End-to-end batch operation flows
│   │
│   └── fixtures/                     # Test data
│       ├── recipes.json              # Sample recipe data
│       ├── unparsed_ingredients.json # Sample unparsed ingredients
│       └── state_examples.json       # Session state samples
│
├── docs/                             # Project documentation
│   ├── prd.md                        # Product Requirements Document
│   ├── front-end-spec.md             # UI/UX Specification
│   ├── architecture.md               # This document
│   ├── brief.md                      # User research and problem analysis
│   └── brainstorming-session-results.md
│
├── .mealie_parser_state.json         # Session state (gitignored, runtime-generated)
├── mealie_parser.log                 # Application logs (gitignored)
├── .gitignore
└── README.md
```

## Organizational Rationale

This structure follows **feature-based organization** within the `mealie_parser/` package while maintaining Textual's architectural patterns:

**Key Organizational Decisions:**

1. **`models/` package (NEW):** Centralizes Epic 1's data models (`PatternGroup`, `BatchOperation`, state schemas). Separates data structures from business logic for testability and reuse across screens/services.

2. **`services/` package (NEW):** Encapsulates batch processing business logic separate from UI. Enables unit testing without Textual UI dependencies.

3. **`screens/` vs `modals/`:** Follows existing codebase pattern. Screens are full-page views (push_screen), modals are overlay dialogs.

4. **`widgets/` package (NEW):** Reusable UI components that appear across multiple screens. Promotes DRY and consistent styling.

5. **`styles/` package:** Textual CSS files organized by scope for maintainability.

## File Naming Conventions

- **Python files:** `snake_case.py`
- **Classes:** `PascalCase` (e.g., `PatternGroupScreen`, `StatusBadge`)
- **CSS files:** `*.tcss` extension
- **Test files:** `test_<module_name>.py`

---
