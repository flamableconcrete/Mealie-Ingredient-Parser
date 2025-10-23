"""Unit tests for PatternGroupScreen."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mealie_parser.models.pattern import PatternGroup, PatternStatus
from mealie_parser.screens.pattern_group import PatternGroupScreen


@pytest.fixture
def sample_unit_patterns():
    """Sample unit patterns for testing."""
    return [
        PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1", "ing-2", "ing-3"],
            recipe_ids=["recipe-1", "recipe-2"],
        ),
        PatternGroup(
            pattern_text="tbsp",
            ingredient_ids=["ing-4", "ing-5"],
            recipe_ids=["recipe-3"],
        ),
    ]


@pytest.fixture
def sample_food_patterns():
    """Sample food patterns for testing."""
    return [
        PatternGroup(
            pattern_text="chicken breast",
            ingredient_ids=["ing-6", "ing-7"],
            recipe_ids=["recipe-4"],
        ),
    ]


@pytest.fixture
def mock_session():
    """Mock aiohttp session."""
    return AsyncMock()


@pytest.fixture
def pattern_screen(sample_unit_patterns, sample_food_patterns, mock_session):
    """Pattern group screen instance for testing."""
    # PatternGroupScreen now handles missing app context gracefully
    # Combine patterns into single list as per new API
    all_patterns = sample_unit_patterns + sample_food_patterns
    return PatternGroupScreen(
        patterns=all_patterns,
        unparsed_recipes=[],
        session=mock_session,
        known_units=[],
        known_foods=[],
    )


def test_screen_initialization(pattern_screen, sample_unit_patterns, sample_food_patterns):
    """Test screen initializes with correct pattern data."""
    # Now patterns are unified, not separated
    assert len(pattern_screen.patterns) == 3  # 2 unit + 1 food
    assert pattern_screen.processed_count == 0
    assert pattern_screen.skipped_count == 0
    assert not pattern_screen.hide_matched_foods
    assert not pattern_screen.hide_matched_units


def test_pattern_group_creation():
    """Test PatternGroup creation and validation."""
    pattern = PatternGroup(
        pattern_text="cup",
        ingredient_ids=["ing-1"],
        recipe_ids=["recipe-1"],
    )

    assert pattern.pattern_text == "cup"
    assert pattern.unit_status == PatternStatus.PENDING
    assert pattern.food_status == PatternStatus.PENDING
    assert len(pattern.ingredient_ids) == 1
    assert len(pattern.recipe_ids) == 1


def test_pattern_group_empty_text_validation():
    """Test PatternGroup validates non-empty pattern text."""
    with pytest.raises(ValueError, match="pattern_text must not be empty"):
        PatternGroup(
            pattern_text="",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
        )


def test_pattern_group_whitespace_normalization():
    """Test PatternGroup normalizes whitespace in pattern text."""
    pattern = PatternGroup(
        pattern_text="  tsp  ",
        ingredient_ids=["ing-1"],
        recipe_ids=["recipe-1"],
    )

    assert pattern.pattern_text == "tsp"  # Whitespace trimmed


def test_reactive_processed_count(pattern_screen):
    """Test processed count reactive attribute."""
    initial_count = pattern_screen.processed_count

    # Simulate processing a pattern
    pattern_screen.processed_count += 1

    assert pattern_screen.processed_count == initial_count + 1


def test_reactive_skipped_count(pattern_screen):
    """Test skipped count reactive attribute."""
    initial_count = pattern_screen.skipped_count

    # Simulate skipping a pattern
    pattern_screen.skipped_count += 1

    assert pattern_screen.skipped_count == initial_count + 1


def test_pattern_status_values():
    """Test valid pattern status values using PatternStatus enum."""
    statuses = [
        PatternStatus.PENDING,
        PatternStatus.PARSING,
        PatternStatus.MATCHED,
        PatternStatus.UNMATCHED,
        PatternStatus.QUEUED,
        PatternStatus.IGNORE,
        PatternStatus.ERROR,
    ]

    for status in statuses:
        pattern = PatternGroup(
            pattern_text="test",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            unit_status=status,
        )
        assert pattern.unit_status == status


def test_pattern_serialization():
    """Test PatternGroup serialization to dict."""
    pattern = PatternGroup(
        pattern_text="tsp",
        ingredient_ids=["ing-1", "ing-2"],
        recipe_ids=["recipe-1"],
    )
    # Must transition through PARSING before MATCHED
    pattern.transition_unit_to(PatternStatus.PARSING)
    pattern.set_matched(unit_id="unit-123")

    data = pattern.to_dict()

    assert data["pattern_text"] == "tsp"
    assert data["ingredient_ids"] == ["ing-1", "ing-2"]
    assert data["recipe_ids"] == ["recipe-1"]
    assert data["unit_status"] == "matched"
    assert data["matched_unit_id"] == "unit-123"


def test_pattern_deserialization():
    """Test PatternGroup deserialization from dict."""
    data = {
        "pattern_text": "cup",
        "ingredient_ids": ["ing-3", "ing-4"],
        "recipe_ids": ["recipe-2"],
        "unit_status": "pending",
        "food_status": "matched",
        "matched_food_id": "food-456",
    }

    pattern = PatternGroup.from_dict(data)

    assert pattern.pattern_text == "cup"
    assert pattern.ingredient_ids == ["ing-3", "ing-4"]
    assert pattern.recipe_ids == ["recipe-2"]
    assert pattern.unit_status == PatternStatus.PENDING
    assert pattern.food_status == PatternStatus.MATCHED
    assert pattern.matched_food_id == "food-456"


def test_total_patterns_property(pattern_screen):
    """Test calculation of total patterns."""
    # Now patterns are unified
    total = len(pattern_screen.patterns)
    assert total == 3  # 2 unit patterns + 1 food pattern combined


def test_toggle_food_selects_all_when_some_unmatched():
    """Test toggle button selects all when some patterns are unmatched."""
    # Create patterns with mixed states
    patterns = [
        PatternGroup(
            pattern_text="chicken",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            food_status=PatternStatus.UNMATCHED,
        ),
        PatternGroup(
            pattern_text="beef",
            ingredient_ids=["ing-2"],
            recipe_ids=["recipe-2"],
            food_status=PatternStatus.UNMATCHED,
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Mock the refresh, button label update, and notify methods
    screen.refresh_food_table = MagicMock()
    screen._update_toggle_button_label = MagicMock()
    screen.notify = MagicMock()

    # Before toggle: both UNMATCHED
    assert patterns[0].food_status == PatternStatus.UNMATCHED
    assert patterns[1].food_status == PatternStatus.UNMATCHED

    # Simulate toggle action
    screen.action_toggle_food()

    # After toggle: both should be QUEUED
    assert patterns[0].food_status == PatternStatus.QUEUED
    assert patterns[1].food_status == PatternStatus.QUEUED


def test_toggle_food_clears_all_when_all_queued():
    """Test toggle button clears all when all patterns are queued."""
    # Create patterns all QUEUED
    patterns = [
        PatternGroup(
            pattern_text="chicken",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            food_status=PatternStatus.QUEUED,
        ),
        PatternGroup(
            pattern_text="beef",
            ingredient_ids=["ing-2"],
            recipe_ids=["recipe-2"],
            food_status=PatternStatus.QUEUED,
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Mock the refresh, button label update, and notify methods
    screen.refresh_food_table = MagicMock()
    screen._update_toggle_button_label = MagicMock()
    screen.notify = MagicMock()

    # Before toggle: both QUEUED
    assert patterns[0].food_status == PatternStatus.QUEUED
    assert patterns[1].food_status == PatternStatus.QUEUED

    # Simulate toggle action
    screen.action_toggle_food()

    # After toggle: both should be UNMATCHED
    assert patterns[0].food_status == PatternStatus.UNMATCHED
    assert patterns[1].food_status == PatternStatus.UNMATCHED


def test_toggle_unit_selects_all_when_some_unmatched():
    """Test toggle button selects all unit patterns when some are unmatched."""
    # Create patterns with mixed states
    patterns = [
        PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            unit_status=PatternStatus.UNMATCHED,
        ),
        PatternGroup(
            pattern_text="tbsp",
            ingredient_ids=["ing-2"],
            recipe_ids=["recipe-2"],
            unit_status=PatternStatus.UNMATCHED,
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Mock the refresh, button label update, and notify methods
    screen.refresh_unit_table = MagicMock()
    screen._update_toggle_button_label = MagicMock()
    screen.notify = MagicMock()

    # Before toggle: both UNMATCHED
    assert patterns[0].unit_status == PatternStatus.UNMATCHED
    assert patterns[1].unit_status == PatternStatus.UNMATCHED

    # Simulate toggle action
    screen.action_toggle_unit()

    # After toggle: both should be QUEUED
    assert patterns[0].unit_status == PatternStatus.QUEUED
    assert patterns[1].unit_status == PatternStatus.QUEUED


def test_toggle_unit_clears_all_when_all_queued():
    """Test toggle button clears all unit patterns when all are queued."""
    # Create patterns all QUEUED
    patterns = [
        PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            unit_status=PatternStatus.QUEUED,
        ),
        PatternGroup(
            pattern_text="tbsp",
            ingredient_ids=["ing-2"],
            recipe_ids=["recipe-2"],
            unit_status=PatternStatus.QUEUED,
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Mock the refresh, button label update, and notify methods
    screen.refresh_unit_table = MagicMock()
    screen._update_toggle_button_label = MagicMock()
    screen.notify = MagicMock()

    # Before toggle: both QUEUED
    assert patterns[0].unit_status == PatternStatus.QUEUED
    assert patterns[1].unit_status == PatternStatus.QUEUED

    # Simulate toggle action
    screen.action_toggle_unit()

    # After toggle: both should be UNMATCHED
    assert patterns[0].unit_status == PatternStatus.UNMATCHED
    assert patterns[1].unit_status == PatternStatus.UNMATCHED


def test_hide_matched_food_switch():
    """Test that hide matched food switch updates reactive attribute."""
    patterns = [
        PatternGroup(
            pattern_text="chicken",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Initially should be False
    assert screen.hide_matched_foods is False

    # Simulate switch change event
    from textual.widgets import Switch

    switch_event = Switch.Changed(switch=MagicMock(id="hide-matched-food"), value=True)
    screen.on_switch_changed(switch_event)

    # Should now be True
    assert screen.hide_matched_foods is True

    # Toggle back
    switch_event = Switch.Changed(switch=MagicMock(id="hide-matched-food"), value=False)
    screen.on_switch_changed(switch_event)

    # Should be False again
    assert screen.hide_matched_foods is False


def test_hide_matched_unit_switch():
    """Test that hide matched unit switch updates reactive attribute."""
    patterns = [
        PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
        ),
    ]

    session = AsyncMock()
    screen = PatternGroupScreen(
        patterns=patterns,
        unparsed_recipes=[],
        session=session,
        known_units=[],
        known_foods=[],
    )

    # Initially should be False
    assert screen.hide_matched_units is False

    # Simulate switch change event
    from textual.widgets import Switch

    switch_event = Switch.Changed(switch=MagicMock(id="hide-matched-unit"), value=True)
    screen.on_switch_changed(switch_event)

    # Should now be True
    assert screen.hide_matched_units is True

    # Toggle back
    switch_event = Switch.Changed(switch=MagicMock(id="hide-matched-unit"), value=False)
    screen.on_switch_changed(switch_event)

    # Should be False again
    assert screen.hide_matched_units is False
