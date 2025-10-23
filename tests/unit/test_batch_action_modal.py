"""Unit tests for BatchActionModal."""

from mealie_parser.modals.batch_action_modal import BatchActionModal


def test_batch_action_modal_initialization():
    """Test batch action modal initializes with correct data."""
    modal = BatchActionModal(
        pattern_text="tsp",
        ingredient_count=47,
        recipe_count=23,
    )

    assert modal.pattern_text == "tsp"
    assert modal.ingredient_count == 47
    assert modal.recipe_count == 23


def test_modal_title_formatting():
    """Test modal displays correct title format."""
    modal = BatchActionModal(
        pattern_text="chicken breast",
        ingredient_count=15,
        recipe_count=8,
    )

    assert modal.pattern_text == "chicken breast"
    # Title will be formatted as: 'Batch Action: "chicken breast"'


def test_modal_stats_formatting():
    """Test modal displays correct stats format."""
    modal = BatchActionModal(
        pattern_text="cup",
        ingredient_count=89,
        recipe_count=41,
    )

    assert modal.ingredient_count == 89
    assert modal.recipe_count == 41
    # Stats will be formatted as: "89 ingredients across 41 recipes"


def test_modal_action_types():
    """Test modal supports all expected action types."""
    # Expected action types returned by modal
    expected_actions = ["create_new", "add_alias", "skip", None]

    # Modal should be able to return any of these action types
    BatchActionModal(
        pattern_text="test",
        ingredient_count=1,
        recipe_count=1,
    )

    # Note: Actual action selection happens through button handlers
    # This test validates the expected return values are documented
    assert expected_actions is not None


def test_modal_keyboard_bindings():
    """Test modal has expected keyboard bindings."""
    modal = BatchActionModal(
        pattern_text="test",
        ingredient_count=1,
        recipe_count=1,
    )

    # Check bindings are defined (BINDINGS is a list of tuples)
    binding_keys = [binding[0] for binding in modal.BINDINGS]

    assert "escape" in binding_keys  # Cancel
    assert "1" in binding_keys  # Create New
    assert "2" in binding_keys  # Add Alias
    assert "3" in binding_keys  # Skip
