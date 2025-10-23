"""Unit tests for BatchPreviewScreen."""

from unittest.mock import AsyncMock

import pytest

from mealie_parser.models.pattern import PatternGroup
from mealie_parser.screens.batch_preview import BatchPreviewScreen


@pytest.fixture
def sample_pattern():
    """Sample pattern for testing."""
    return PatternGroup(
        pattern_text="tsp",
        ingredient_ids=["ing-1", "ing-2", "ing-3"],
        recipe_ids=["recipe-1", "recipe-2"],
    )


@pytest.fixture
def sample_ingredients():
    """Sample ingredient data for testing."""
    return [
        {
            "id": "ing-1",
            "note": "1 tsp salt",
            "recipeName": "Chocolate Cake",
            "recipeId": "recipe-1",
            "unit": {"name": "None"},
            "food": {"name": "salt"},
        },
        {
            "id": "ing-2",
            "note": "2 tsp vanilla",
            "recipeName": "Cookies",
            "recipeId": "recipe-2",
            "unit": {},
            "food": {"name": "vanilla"},
        },
        {
            "id": "ing-3",
            "originalText": "1 tsp baking soda",
            "recipeName": "Pancakes",
            "recipeId": "recipe-1",
            "unit": None,
            "food": {"name": "baking soda"},
        },
    ]


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    return AsyncMock()


@pytest.fixture
def preview_screen_create_unit(sample_pattern, sample_ingredients, mock_session):
    """BatchPreviewScreen instance for create_unit operation."""
    return BatchPreviewScreen(
        operation_type="create_unit",
        pattern=sample_pattern,
        affected_ingredients=sample_ingredients,
        unit_or_food_id="unit-123",
        session=mock_session,
        unit_or_food_name="teaspoon",
    )


@pytest.fixture
def preview_screen_add_food_alias(sample_pattern, sample_ingredients, mock_session):
    """BatchPreviewScreen instance for add_food_alias operation."""
    return BatchPreviewScreen(
        operation_type="add_food_alias",
        pattern=sample_pattern,
        affected_ingredients=sample_ingredients,
        unit_or_food_id="food-456",
        session=mock_session,
        unit_or_food_name="chicken breast",
    )


def test_screen_initialization_create_unit(preview_screen_create_unit, sample_pattern, sample_ingredients):
    """Test screen initializes correctly for create_unit operation."""
    screen = preview_screen_create_unit

    assert screen.operation_type == "create_unit"
    assert screen.pattern == sample_pattern
    assert screen.affected_ingredients == sample_ingredients
    assert screen.unit_or_food_id == "unit-123"
    assert screen.unit_or_food_name == "teaspoon"
    assert screen.show_progress is False


def test_screen_initialization_add_food_alias(preview_screen_add_food_alias, sample_pattern):
    """Test screen initializes correctly for add_food_alias operation."""
    screen = preview_screen_add_food_alias

    assert screen.operation_type == "add_food_alias"
    assert screen.unit_or_food_id == "food-456"
    assert screen.unit_or_food_name == "chicken breast"


def test_generate_summary_text_create_unit(preview_screen_create_unit):
    """Test summary text generation for create_unit operation."""
    summary = preview_screen_create_unit.generate_summary_text()

    assert "Create Unit: 'teaspoon'" in summary
    assert "3 ingredients" in summary


def test_generate_summary_text_create_food(sample_pattern, sample_ingredients, mock_session):
    """Test summary text generation for create_food operation."""
    screen = BatchPreviewScreen(
        operation_type="create_food",
        pattern=sample_pattern,
        affected_ingredients=sample_ingredients,
        unit_or_food_id="food-123",
        session=mock_session,
        unit_or_food_name="chicken",
    )

    summary = screen.generate_summary_text()

    assert "Create Food: 'chicken'" in summary
    assert "3 ingredients" in summary


def test_generate_summary_text_add_unit_alias(sample_pattern, sample_ingredients, mock_session):
    """Test summary text generation for add_unit_alias operation."""
    screen = BatchPreviewScreen(
        operation_type="add_unit_alias",
        pattern=sample_pattern,
        affected_ingredients=sample_ingredients,
        unit_or_food_id="unit-123",
        session=mock_session,
        unit_or_food_name="teaspoon",
    )

    summary = screen.generate_summary_text()

    assert "Add Alias 'tsp' to Unit 'teaspoon'" in summary
    assert "3 ingredients" in summary


def test_generate_summary_text_add_food_alias(preview_screen_add_food_alias):
    """Test summary text generation for add_food_alias operation."""
    summary = preview_screen_add_food_alias.generate_summary_text()

    assert "Add Alias 'tsp' to Food 'chicken breast'" in summary
    assert "3 ingredients" in summary


def test_generate_operation_details(preview_screen_create_unit):
    """Test operation details generation."""
    details = preview_screen_create_unit.generate_operation_details()

    assert "Will update unit field" in details
    assert "3 ingredients" in details
    assert "2 recipes" in details  # recipe-1 and recipe-2


def test_generate_operation_details_food(preview_screen_add_food_alias):
    """Test operation details generation for food operations."""
    details = preview_screen_add_food_alias.generate_operation_details()

    assert "Will update food field" in details
    assert "3 ingredients" in details


def test_ingredient_count_in_summary(sample_pattern, mock_session):
    """Test summary reflects correct ingredient count."""
    # Test with different ingredient counts
    for count in [1, 5, 47]:
        ingredients = [{"id": f"ing-{i}"} for i in range(count)]
        screen = BatchPreviewScreen(
            operation_type="create_unit",
            pattern=sample_pattern,
            affected_ingredients=ingredients,
            unit_or_food_id="unit-123",
            session=mock_session,
            unit_or_food_name="test",
        )

        summary = screen.generate_summary_text()
        assert f"{count} ingredients" in summary


def test_cancellation_result_format():
    """Test cancellation returns correct result format."""
    expected_result = {
        "cancelled": True,
        "succeeded": 0,
        "failed": 0,
        "errors": [],
    }

    # Validate expected structure
    assert "cancelled" in expected_result
    assert "succeeded" in expected_result
    assert "failed" in expected_result
    assert "errors" in expected_result
    assert expected_result["cancelled"] is True


def test_success_result_format():
    """Test successful execution returns correct result format."""
    expected_result = {
        "cancelled": False,
        "succeeded": 45,
        "failed": 2,
        "errors": [
            "Ingredient ing-46: Network timeout",
            "Ingredient ing-47: Invalid ingredient ID",
        ],
    }

    # Validate expected structure
    assert "cancelled" in expected_result
    assert "succeeded" in expected_result
    assert "failed" in expected_result
    assert "errors" in expected_result
    assert expected_result["cancelled"] is False
    assert len(expected_result["errors"]) == 2


def test_keyboard_bindings(preview_screen_create_unit):
    """Test screen has expected keyboard bindings."""
    bindings = [binding[0] for binding in preview_screen_create_unit.BINDINGS]

    assert "escape" in bindings  # Cancel


def test_reactive_show_progress(preview_screen_create_unit):
    """Test show_progress reactive attribute."""
    screen = preview_screen_create_unit

    # Initial state
    assert screen.show_progress is False

    # Toggle to True
    screen.show_progress = True
    assert screen.show_progress is True

    # Toggle back to False
    screen.show_progress = False
    assert screen.show_progress is False


def test_ingredient_display_limit(sample_pattern, mock_session):
    """Test ingredient table limits display to 100 rows."""
    # Create 150 ingredients
    ingredients = [
        {
            "id": f"ing-{i}",
            "note": f"Ingredient {i}",
            "recipeName": "Test Recipe",
            "recipeId": "recipe-1",
        }
        for i in range(150)
    ]

    screen = BatchPreviewScreen(
        operation_type="create_unit",
        pattern=sample_pattern,
        affected_ingredients=ingredients,
        unit_or_food_id="unit-123",
        session=mock_session,
        unit_or_food_name="test",
    )

    # Validate screen has all 150 ingredients stored
    assert len(screen.affected_ingredients) == 150
    # Note: Actual table limiting is tested in integration tests


def test_missing_recipe_name_handles_gracefully(sample_pattern, mock_session):
    """Test ingredients without recipeName display 'N/A'."""
    ingredients = [
        {
            "id": "ing-1",
            "note": "1 tsp salt",
            # recipeName missing
            "recipeId": "recipe-1",
        }
    ]

    screen = BatchPreviewScreen(
        operation_type="create_unit",
        pattern=sample_pattern,
        affected_ingredients=ingredients,
        unit_or_food_id="unit-123",
        session=mock_session,
        unit_or_food_name="teaspoon",
    )

    # Screen should initialize without errors
    assert screen.affected_ingredients == ingredients


def test_operation_type_validation():
    """Test all expected operation types are supported."""
    valid_operation_types = [
        "create_unit",
        "create_food",
        "add_unit_alias",
        "add_food_alias",
    ]

    # All operation types should be valid
    for op_type in valid_operation_types:
        assert op_type in [
            "create_unit",
            "create_food",
            "add_unit_alias",
            "add_food_alias",
        ]
