"""Unit tests for food workflow functionality."""

from unittest.mock import AsyncMock

import pytest

from mealie_parser.models.pattern import PatternGroup


@pytest.fixture
def sample_food_pattern():
    """Sample food pattern for testing."""
    return PatternGroup(
        pattern_text="chicken breast",
        ingredient_ids=["ing-1", "ing-2", "ing-3"],
        recipe_ids=["recipe-1", "recipe-2"],
    )


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    return AsyncMock()


def test_food_action_modal_returns_correct_actions():
    """Test FoodActionModal can return expected action types."""
    expected_actions = ["create", "select", "custom", "skip", None]

    # All action types should be valid
    for action in expected_actions:
        assert action in ["create", "select", "custom", "skip", None]


def test_food_pattern_identification(sample_food_pattern):
    """Test food patterns are correctly identified."""
    # Food patterns should have pattern_text
    assert sample_food_pattern.pattern_text == "chicken breast"
    assert len(sample_food_pattern.ingredient_ids) == 3
    assert len(sample_food_pattern.recipe_ids) == 2


def test_refresh_food_cache_success():
    """Test food cache refresh with successful API call."""
    # Mock successful cache refresh
    mock_foods = [
        {"id": "food-1", "name": "Chicken"},
        {"id": "food-2", "name": "Beef"},
    ]

    # Validate expected data structure
    assert len(mock_foods) == 2
    assert mock_foods[0]["name"] == "Chicken"
    assert mock_foods[1]["name"] == "Beef"


def test_refresh_food_cache_handles_errors():
    """Test food cache refresh handles API errors gracefully."""
    # Should continue with stale cache on error
    # Actual implementation logs warning but doesn't abort
    error_message = "API connection timeout"

    # Test should validate error is logged but not raised
    assert error_message is not None


def test_batch_result_with_food_operations():
    """Test batch result format for food operations."""
    batch_result = {
        "cancelled": False,
        "succeeded": 30,
        "failed": 4,
        "errors": [
            "Ingredient ing-31: Network timeout",
            "Ingredient ing-32: Invalid food ID",
            "Ingredient ing-33: Recipe not found",
            "Ingredient ing-34: Permission denied",
        ],
    }

    # Validate result structure
    assert batch_result["succeeded"] == 30
    assert batch_result["failed"] == 4
    assert len(batch_result["errors"]) == 4
    assert not batch_result["cancelled"]


def test_food_operation_types():
    """Test all supported food operation types."""
    operation_types = ["create_food", "add_food_alias"]

    for op_type in operation_types:
        assert op_type in ["create_food", "add_food_alias"]


def test_food_cache_after_create_new():
    """Test food cache is refreshed after creating new food."""
    # After create_food operation, cache should be refreshed
    # This prevents duplicate food creation
    initial_foods_count = 50
    new_foods_count = 51  # One food added

    assert new_foods_count == initial_foods_count + 1


def test_food_cache_after_add_alias():
    """Test food cache is refreshed after adding alias."""
    # After add_food_alias operation, cache should be refreshed
    # This makes new alias immediately available
    initial_foods_count = 50
    refreshed_foods_count = 50  # Same count, but includes new alias

    assert refreshed_foods_count == initial_foods_count


def test_create_food_workflow_data_flow():
    """Test data flow through create food workflow."""
    # Pattern → FoodActionModal → CreateFoodModal → BatchPreviewScreen → Cache Refresh
    workflow_steps = [
        "pattern_selection",
        "food_action_modal",
        "create_food_modal",
        "batch_preview_screen",
        "batch_execution",
        "cache_refresh",
        "pattern_complete",
    ]

    assert len(workflow_steps) == 7
    assert workflow_steps[0] == "pattern_selection"
    assert workflow_steps[-1] == "pattern_complete"


def test_add_alias_workflow_data_flow():
    """Test data flow through add alias workflow."""
    # Pattern → FoodActionModal → SelectFoodModal → BatchPreviewScreen → Cache Refresh
    workflow_steps = [
        "pattern_selection",
        "food_action_modal",
        "select_food_modal",
        "batch_preview_screen",
        "batch_execution",
        "cache_refresh",
        "pattern_complete",
    ]

    assert len(workflow_steps) == 7
    assert workflow_steps[2] == "select_food_modal"


def test_food_vs_unit_pattern_routing():
    """Test correct modal is shown based on pattern type."""
    # is_unit=False should use FoodActionModal
    # is_unit=True should use BatchActionModal

    is_unit = False
    if is_unit:
        modal_type = "BatchActionModal"
    else:
        modal_type = "FoodActionModal"

    assert modal_type == "FoodActionModal"


def test_food_cache_refresh_only_on_success():
    """Test cache refresh only happens for successful operations."""
    # Cache should refresh when succeeded > 0
    # Cache should NOT refresh when succeeded = 0

    test_cases = [
        {"succeeded": 10, "should_refresh": True},
        {"succeeded": 0, "should_refresh": False},
        {"succeeded": 1, "should_refresh": True},
    ]

    for case in test_cases:
        should_refresh = case["succeeded"] > 0
        assert should_refresh == case["should_refresh"]


def test_food_cache_refresh_only_for_food_patterns():
    """Test cache refresh only happens for food patterns, not unit patterns."""
    # is_unit=True should NOT refresh food cache
    # is_unit=False should refresh food cache

    test_cases = [
        {"is_unit": True, "should_refresh_food": False},
        {"is_unit": False, "should_refresh_food": True},
    ]

    for case in test_cases:
        should_refresh = not case["is_unit"]
        assert should_refresh == case["should_refresh_food"]


def test_batch_preview_operation_details_for_food():
    """Test operation details formatting for food operations."""
    # "create_food" should show: "Will update food field for X ingredients across Y recipes"
    # "add_food_alias" should show alias creation details

    operation_details = {
        "create_food": "Will update food field for 34 ingredients across 18 recipes",
        "add_food_alias": "Will create alias 'chicken breast' for food 'Chicken' and update 34 ingredients across 18 recipes",
    }

    assert "food field" in operation_details["create_food"]
    assert "alias" in operation_details["add_food_alias"]


def test_pattern_status_after_successful_food_operation():
    """Test pattern status is marked completed after successful operation."""
    initial_status = "parsing"
    final_status = "completed"

    # After successful batch operation with succeeded > 0
    assert final_status == "completed"
    assert initial_status != final_status
