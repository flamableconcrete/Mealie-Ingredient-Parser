"""Display constants for pattern group screens and tables."""

# Status display mapping with Rich markup for visual feedback
# Used throughout the UI to show pattern status consistently
STATUS_MAP = {
    "pending": "",
    "parsing": "[cyan]parsing[/cyan]",
    "matched": "[green]✓ matched[/green]",
    "unmatched": "[yellow]⚠ unmatched[/yellow]",
    "queued": "[blue]📤 queued[/blue]",
    "ignore": "[orange1]skipped[/orange1]",
    "error": "[red]✗ error[/red]",
}

# Table column configuration (name, width)
# Used for consistent column setup across unit and food tables
UNIT_TABLE_COLUMNS = [
    ("Pattern Text", 50),
    ("Status", 15),
    ("Parsed Unit", 20),
    ("Create", 8),
]

FOOD_TABLE_COLUMNS = [
    ("Pattern Text", 50),
    ("Status", 15),
    ("Parsed Food", 20),
    ("Create", 8),
]

# Checkbox display values
CHECKBOX_UNCHECKED = "☐"
CHECKBOX_CHECKED = "☑"
CHECKBOX_EMPTY = ""

# Default parsing configuration
DEFAULT_CONCURRENCY = 4
DEFAULT_PARSE_METHOD = "nlp"
