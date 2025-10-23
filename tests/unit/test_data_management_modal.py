"""Unit tests for DataManagementModal."""

import pytest
from textual.widgets import DataTable

from mealie_parser.modals.data_management_modal import DataManagementModal


@pytest.fixture
def sample_units():
    """Sample unit data for testing."""
    return [
        {
            "id": "unit-1",
            "name": "cup",
            "pluralName": "cups",
            "abbreviation": "c",
            "pluralAbbreviation": "c",
        },
        {
            "id": "unit-2",
            "name": "tablespoon",
            "pluralName": "tablespoons",
            "abbreviation": "tbsp",
            "pluralAbbreviation": "tbsp",
        },
        {
            "id": "unit-3",
            "name": "teaspoon",
            "pluralName": "teaspoons",
            "abbreviation": "tsp",
            "pluralAbbreviation": "tsp",
        },
    ]


@pytest.fixture
def sample_foods():
    """Sample food data for testing."""
    return [
        {
            "id": "food-1",
            "name": "sugar",
            "pluralName": "sugars",
            "description": "White granulated sugar",
        },
        {
            "id": "food-2",
            "name": "salt",
            "pluralName": "salts",
            "description": "Table salt",
        },
        {
            "id": "food-3",
            "name": "flour",
            "pluralName": "flours",
            "description": "All-purpose flour",
        },
    ]


@pytest.mark.asyncio
async def test_data_management_modal_initialization(sample_units, sample_foods):
    """Test that modal initializes with provided units and foods."""
    modal = DataManagementModal(units=sample_units, foods=sample_foods)

    assert modal.units == sample_units
    assert modal.foods == sample_foods


@pytest.mark.asyncio
async def test_data_management_modal_tables_populated(sample_units, sample_foods):
    """Test that unit and food tables are populated correctly."""
    from textual.app import App

    class TestApp(App):
        def on_mount(self):
            self.push_screen(DataManagementModal(units=sample_units, foods=sample_foods))

    app = TestApp()
    async with app.run_test() as pilot:
        # Wait for modal to mount
        await pilot.pause()

        # Check unit table
        unit_table = app.screen.query_one("#unit-table", DataTable)
        assert unit_table is not None
        assert len(unit_table.rows) == len(sample_units)

        # Check food table
        food_table = app.screen.query_one("#food-table", DataTable)
        assert food_table is not None
        assert len(food_table.rows) == len(sample_foods)


@pytest.mark.asyncio
async def test_data_management_modal_unit_columns(sample_units, sample_foods):
    """Test that unit table has correct columns."""
    from textual.app import App

    class TestApp(App):
        def on_mount(self):
            self.push_screen(DataManagementModal(units=sample_units, foods=sample_foods))

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        unit_table = app.screen.query_one("#unit-table", DataTable)
        columns = [col.label.plain for col in unit_table.columns.values()]

        assert "Name" in columns
        assert "Plural Name" in columns
        assert "Abbreviation" in columns
        assert "Plural Abbreviation" in columns


@pytest.mark.asyncio
async def test_data_management_modal_food_columns(sample_units, sample_foods):
    """Test that food table has correct columns."""
    from textual.app import App

    class TestApp(App):
        def on_mount(self):
            self.push_screen(DataManagementModal(units=sample_units, foods=sample_foods))

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        food_table = app.screen.query_one("#food-table", DataTable)
        columns = [col.label.plain for col in food_table.columns.values()]

        assert "Name" in columns
        assert "Plural Name" in columns
        assert "Description" in columns


@pytest.mark.asyncio
async def test_data_management_modal_close_button(sample_units, sample_foods):
    """Test that close button dismisses the modal."""
    from textual.app import App

    class TestApp(App):
        def on_mount(self):
            self.push_screen(DataManagementModal(units=sample_units, foods=sample_foods))

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Click close button
        await pilot.click("#close")
        await pilot.pause()

        # Modal should be dismissed (screen stack should be empty)
        assert len(app.screen_stack) == 1  # Only the base screen remains


@pytest.mark.asyncio
async def test_data_management_modal_escape_key(sample_units, sample_foods):
    """Test that escape key dismisses the modal."""
    from textual.app import App

    class TestApp(App):
        def on_mount(self):
            self.push_screen(DataManagementModal(units=sample_units, foods=sample_foods))

    app = TestApp()
    async with app.run_test() as pilot:
        await pilot.pause()

        # Press escape key
        await pilot.press("escape")
        await pilot.pause()

        # Modal should be dismissed
        assert len(app.screen_stack) == 1  # Only the base screen remains
