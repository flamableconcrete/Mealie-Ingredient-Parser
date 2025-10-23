"""Table management for pattern group screens."""

from typing import TYPE_CHECKING

from loguru import logger
from textual.widgets import DataTable

from mealie_parser.models.pattern import PatternGroup, PatternStatus


if TYPE_CHECKING:
    from textual.widgets._data_table import RowKey


class PatternTableManager:
    """
    Manages DataTable state and synchronization for pattern display.

    Encapsulates all the complex row key and index mapping logic that was
    previously scattered throughout PatternGroupScreen.

    Attributes
    ----------
    patterns : list[PatternGroup]
        Reference to the shared pattern list
    table_id : str
        ID of the table being managed ("#unit-table" or "#food-table")
    is_unit_table : bool
        True if managing unit table, False for food table
    column_widths : list[tuple[str, int]]
        List of (column_name, width) tuples
    row_keys : dict[int, RowKey]
        Maps pattern index to table row key
    display_to_pattern : dict[int, int]
        Maps display row index to original pattern index
    pattern_to_display : dict[int, int]
        Maps pattern index to current display row index
    """

    def __init__(
        self,
        patterns: list[PatternGroup],
        table_id: str,
        is_unit_table: bool,
        column_widths: list[tuple[str, int]],
    ):
        """
        Initialize table manager.

        Parameters
        ----------
        patterns : list[PatternGroup]
            Reference to the shared pattern list
        table_id : str
            Table widget ID ("#unit-table" or "#food-table")
        is_unit_table : bool
            True for unit table, False for food table
        column_widths : list[tuple[str, int]]
            List of (column_name, width) tuples
        """
        self.patterns = patterns
        self.table_id = table_id
        self.is_unit_table = is_unit_table
        self.column_widths = column_widths

        # State tracking dictionaries
        self.row_keys: dict[int, RowKey] = {}
        self.display_to_pattern: dict[int, int] = {}
        self.pattern_to_display: dict[int, int] = {}

    def get_pattern_index(self, display_row: int) -> int | None:
        """
        Get the original pattern index from the displayed row index.

        Parameters
        ----------
        display_row : int
            The visible row index in the DataTable

        Returns
        -------
        int | None
            The original index in self.patterns, or None if not found
        """
        return self.display_to_pattern.get(display_row)

    def get_pattern_status(self, pattern: PatternGroup) -> PatternStatus:
        """
        Get the appropriate status for this table type.

        Parameters
        ----------
        pattern : PatternGroup
            The pattern to check

        Returns
        -------
        PatternStatus
            Unit status if unit table, food status if food table
        """
        return pattern.unit_status if self.is_unit_table else pattern.food_status

    def get_parsed_value(self, pattern: PatternGroup) -> str:
        """
        Get the parsed value to display for this table type.

        Parameters
        ----------
        pattern : PatternGroup
            The pattern to get value from

        Returns
        -------
        str
            Parsed unit if unit table, parsed food if food table
        """
        return pattern.parsed_unit if self.is_unit_table else pattern.parsed_food

    def get_status_display(self, status: PatternStatus) -> str:
        """
        Get Rich-formatted status display string.

        Parameters
        ----------
        status : PatternStatus
            The pattern status

        Returns
        -------
        str
            Rich-formatted status string
        """
        status_map = {
            "pending": "",
            "parsing": "[cyan]parsing[/cyan]",
            "matched": "[green]✓ matched[/green]",
            "unmatched": "[yellow]⚠ unmatched[/yellow]",
            "queued": "[blue]📤 queued[/blue]",
            "ignore": "[orange1]skipped[/orange1]",
            "error": "[red]✗ error[/red]",
        }
        return status_map.get(status.value, status.value)

    def get_checkbox_value(self, status: PatternStatus) -> str:
        """
        Get checkbox display value based on pattern status.

        Parameters
        ----------
        status : PatternStatus
            The current pattern status

        Returns
        -------
        str
            Checkbox character to display ("☐", "☑", or "")
        """
        if status == PatternStatus.UNMATCHED:
            return "☐"
        if status == PatternStatus.QUEUED:
            return "☑"
        return ""

    def initialize_table(
        self,
        table: DataTable,
        hide_matched: bool = False,
    ) -> None:
        """
        Populate table with initial pattern data.

        Parameters
        ----------
        table : DataTable
            The table widget to populate
        hide_matched : bool
            Whether to hide patterns with MATCHED status
        """
        logger.info(f"PatternTableManager.initialize_table: Starting for {self.table_id}")
        # Add columns
        for col_name, width in self.column_widths:
            table.add_column(col_name, width=width)

        # Set cursor type for cell selection
        table.cursor_type = "cell"

        # Populate rows
        rows = []
        display_row = 0
        for i, pattern in enumerate(self.patterns):
            # Skip matched patterns if hide toggle is on
            if hide_matched and self.get_pattern_status(pattern) == PatternStatus.MATCHED:
                continue

            status = self.get_pattern_status(pattern)
            status_display = self.get_status_display(status)
            parsed_value = self.get_parsed_value(pattern)
            create_cell = self.get_checkbox_value(status)

            rows.append(
                (
                    pattern.pattern_text,
                    status_display,
                    parsed_value,
                    create_cell,
                )
            )

            # Track mappings
            self.display_to_pattern[display_row] = i
            self.pattern_to_display[i] = display_row
            display_row += 1

        row_keys = table.add_rows(rows)
        for i, row_key in enumerate(row_keys):
            self.row_keys[self.display_to_pattern[i]] = row_key

        logger.info(
            f"PatternTableManager.initialize_table: Finished for {self.table_id}. Showing {display_row}/{len(self.patterns)} patterns"
        )

    def refresh_table(
        self,
        table: DataTable,
        hide_matched: bool = False,
    ) -> None:
        """
        Rebuild table with current pattern data.

        Parameters
        ----------
        table : DataTable
            The table widget to refresh
        hide_matched : bool
            Whether to hide patterns with MATCHED status
        """
        logger.info(f"PatternTableManager.refresh_table: Starting for {self.table_id}")
        # Clear and rebuild mappings
        table.clear()
        self.row_keys.clear()
        self.display_to_pattern.clear()
        self.pattern_to_display.clear()

        # Add columns if they don't exist
        if not table.columns:
            for col_name, width in self.column_widths:
                table.add_column(col_name, width=width)

        # Repopulate rows
        rows = []
        row_idx = 0
        for i, pattern in enumerate(self.patterns):
            # Skip matched patterns if hide toggle is on
            if hide_matched and self.get_pattern_status(pattern) == PatternStatus.MATCHED:
                continue

            status = self.get_pattern_status(pattern)
            status_display = self.get_status_display(status)
            parsed_value = self.get_parsed_value(pattern)
            create_cell = self.get_checkbox_value(status)

            rows.append(
                (
                    pattern.pattern_text,
                    status_display,
                    parsed_value,
                    create_cell,
                )
            )

            # Track mappings
            self.display_to_pattern[row_idx] = i
            self.pattern_to_display[i] = row_idx
            row_idx += 1

        row_keys = table.add_rows(rows)
        for i, row_key in enumerate(row_keys):
            self.row_keys[self.display_to_pattern[i]] = row_key

        logger.info(
            f"PatternTableManager.refresh_table: Finished for {self.table_id}. Showing {row_idx}/{len(self.patterns)} patterns"
        )
