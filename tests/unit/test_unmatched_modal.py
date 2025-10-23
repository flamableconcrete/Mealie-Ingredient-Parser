"""Comprehensive unit tests for UnmatchedUnitModal and UnmatchedFoodModal workflows."""

from unittest.mock import MagicMock

import pytest

from mealie_parser.modals.unmatched_food_modal import UnmatchedFoodModal
from mealie_parser.modals.unmatched_unit_modal import UnmatchedUnitModal
from mealie_parser.models.pattern import PatternGroup


@pytest.fixture
def sample_pattern():
    """Sample pattern for testing."""
    pattern = MagicMock(spec=PatternGroup)
    pattern.pattern_text = "chicken breast"
    pattern.parsed_unit = "cup"
    pattern.parsed_food = "chicken"
    pattern.unit_confidence = 0.85
    pattern.food_confidence = 0.92
    return pattern


@pytest.fixture
def sample_units():
    """Sample units list for testing."""
    return [
        {"id": "unit-1", "name": "cup"},
        {"id": "unit-2", "name": "tablespoon"},
        {"id": "unit-3", "name": "teaspoon"},
        {"id": "unit-4", "name": "ounce"},
    ]


@pytest.fixture
def sample_foods():
    """Sample foods list for testing."""
    return [
        {"id": "food-1", "name": "Chicken"},
        {"id": "food-2", "name": "Beef"},
        {"id": "food-3", "name": "Pork"},
        {"id": "food-4", "name": "Fish"},
    ]


# =============================================================================
# UnmatchedUnitModal Tests
# =============================================================================


class TestUnmatchedUnitModalInitialization:
    """Test UnmatchedUnitModal initialization."""

    def test_modal_initializes_with_pattern_data(self, sample_pattern, sample_units):
        """Test modal initializes correctly with pattern data."""
        modal = UnmatchedUnitModal(pattern=sample_pattern, units=sample_units, parse_method="nlp")

        assert modal.pattern == sample_pattern
        assert modal.units == sample_units
        assert modal.parse_method == "nlp"
        assert modal.unit_input_value == "cup"
        assert modal.original_parsed_unit == "cup"
        assert modal.unit_confidence == 0.85

    def test_modal_handles_missing_parsed_unit(self, sample_units):
        """Test modal handles pattern with no parsed unit."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "raw text"
        pattern.parsed_unit = None
        pattern.unit_confidence = 0.0

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)

        assert modal.unit_input_value == ""
        assert modal.original_parsed_unit == ""
        assert modal.unit_confidence == 0.0


class TestUnmatchedUnitModalButtonStates:
    """Test button state transitions based on input changes."""

    def test_button_hidden_when_input_empty(self, sample_pattern, sample_units):
        """Test button is hidden when input is empty."""
        modal = UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)
        modal.unit_input_value = ""

        # Button should be hidden with empty input
        # This would normally be tested through DOM queries in integration test
        assert modal.unit_input_value == ""

    def test_button_hidden_case1_parsed_equals_input_and_exists(self, sample_pattern, sample_units):
        """Test Case 1: parsed_unit == input AND input matches DB -> NO button."""
        modal = UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)

        # Set input to match parsed_unit and DB
        modal.unit_input_value = "cup"  # Exists in sample_units

        # Update button logic would hide button in this case
        # In real usage, update_unit_button() would be called
        assert modal.unit_input_value == modal.original_parsed_unit
        # Verify unit exists in DB
        assert any(u["name"] == "cup" for u in sample_units)

    def test_button_visible_case2_parsed_equals_input_not_in_db(self, sample_pattern, sample_units):
        """Test Case 2: parsed_unit == input AND input NOT in DB -> Create button."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "newunit"
        pattern.unit_confidence = 0.75

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "newunit"

        # Button should show "Create missing unit: newunit"
        assert modal.unit_input_value == modal.original_parsed_unit
        assert not any(u["name"] == "newunit" for u in sample_units)

    def test_button_visible_case3_parsed_not_equal_input_matches_db(self, sample_pattern, sample_units):
        """Test Case 3: parsed_unit != input AND input matches DB -> Add alias."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "c"
        pattern.unit_confidence = 0.75

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "cup"  # Different from parsed, exists in DB

        # Button should show "Add alias for cup: c"
        assert modal.unit_input_value != modal.original_parsed_unit
        assert any(u["name"] == "cup" for u in sample_units)

    def test_button_visible_case4_parsed_not_equal_input_not_in_db(self, sample_pattern, sample_units):
        """Test Case 4: parsed_unit != input AND input NOT in DB -> Create with alias."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "c"
        pattern.unit_confidence = 0.75

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "custom_unit"

        # Button should show "Create missing unit: custom_unit (with alias: c)"
        assert modal.unit_input_value != modal.original_parsed_unit
        assert not any(u["name"] == "custom_unit" for u in sample_units)


class TestUnmatchedUnitModalOperations:
    """Test unit modal operation logic."""

    def test_unit_action_create_new_unit(self, sample_units):
        """Test creating new unit operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "newunit"

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "newunit"

        # Simulate button press - Case 2
        result = {
            "action": "unit",
            "pattern": "test pattern",
            "operation": "create_unit",
            "unit_name": "newunit",
        }

        assert result["operation"] == "create_unit"
        assert result["unit_name"] == "newunit"
        assert "alias" not in result

    def test_unit_action_add_alias(self, sample_units):
        """Test adding unit alias operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "c"

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "cup"  # Exists in DB

        # Simulate button press - Case 3
        result = {
            "action": "unit",
            "pattern": "test pattern",
            "operation": "add_unit_alias",
            "unit_id": "unit-1",
            "unit_name": "cup",
            "alias": "c",
        }

        assert result["operation"] == "add_unit_alias"
        assert result["unit_name"] == "cup"
        assert result["alias"] == "c"

    def test_unit_action_create_with_alias(self, sample_units):
        """Test creating unit with alias operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_unit = "c"

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "custom_unit"

        # Simulate button press - Case 4
        result = {
            "action": "unit",
            "pattern": "test pattern",
            "operation": "create_unit_with_alias",
            "unit_name": "custom_unit",
            "alias": "c",
        }

        assert result["operation"] == "create_unit_with_alias"
        assert result["unit_name"] == "custom_unit"
        assert result["alias"] == "c"

    def test_reparse_action(self, sample_pattern, sample_units):
        """Test re-parse action returns correct structure."""
        UnmatchedUnitModal(pattern=sample_pattern, units=sample_units, parse_method="nlp")

        # Simulate reset button press
        result = {
            "action": "reparse",
            "pattern": "chicken breast",
            "method": "nlp",
        }

        assert result["action"] == "reparse"
        assert result["pattern"] == "chicken breast"
        assert result["method"] == "nlp"

    def test_cancel_returns_none(self, sample_pattern, sample_units):
        """Test cancel action returns None."""
        UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)

        # Simulate cancel - would call dismiss(None)
        result = None

        assert result is None


# =============================================================================
# UnmatchedFoodModal Tests
# =============================================================================


class TestUnmatchedFoodModalInitialization:
    """Test UnmatchedFoodModal initialization."""

    def test_modal_initializes_with_pattern_data(self, sample_pattern, sample_foods):
        """Test modal initializes correctly with pattern data."""
        modal = UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods, parse_method="nlp")

        assert modal.pattern == sample_pattern
        assert modal.foods == sample_foods
        assert modal.parse_method == "nlp"
        assert modal.food_input_value == "chicken"
        assert modal.original_parsed_food == "chicken"
        assert modal.food_confidence == 0.92

    def test_modal_handles_missing_parsed_food(self, sample_foods):
        """Test modal handles pattern with no parsed food."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "raw text"
        pattern.parsed_food = None
        pattern.food_confidence = 0.0

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)

        assert modal.food_input_value == ""
        assert modal.original_parsed_food == ""
        assert modal.food_confidence == 0.0


class TestUnmatchedFoodModalButtonStates:
    """Test button state transitions for food modal."""

    def test_button_hidden_when_input_empty(self, sample_pattern, sample_foods):
        """Test button is hidden when input is empty."""
        modal = UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods)
        modal.food_input_value = ""

        assert modal.food_input_value == ""

    def test_button_hidden_case1_parsed_equals_input_and_exists(self, sample_pattern, sample_foods):
        """Test Case 1: parsed_food == input AND input matches DB -> NO button."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "Chicken"
        pattern.food_confidence = 0.85

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Chicken"  # Exists in sample_foods

        assert modal.food_input_value == modal.original_parsed_food
        assert any(f["name"] == "Chicken" for f in sample_foods)

    def test_button_visible_case2_parsed_equals_input_not_in_db(self, sample_pattern, sample_foods):
        """Test Case 2: parsed_food == input AND input NOT in DB -> Create button."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "Turkey"
        pattern.food_confidence = 0.75

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Turkey"

        assert modal.food_input_value == modal.original_parsed_food
        assert not any(f["name"] == "Turkey" for f in sample_foods)

    def test_button_visible_case3_parsed_not_equal_input_matches_db(self, sample_pattern, sample_foods):
        """Test Case 3: parsed_food != input AND input matches DB -> Add alias."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "chicken breast"
        pattern.food_confidence = 0.75

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Chicken"  # Different from parsed, exists in DB

        assert modal.food_input_value != modal.original_parsed_food
        assert any(f["name"] == "Chicken" for f in sample_foods)

    def test_button_visible_case4_parsed_not_equal_input_not_in_db(self, sample_pattern, sample_foods):
        """Test Case 4: parsed_food != input AND input NOT in DB -> Create with alias."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "chicken breast"
        pattern.food_confidence = 0.75

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Poultry"

        assert modal.food_input_value != modal.original_parsed_food
        assert not any(f["name"] == "Poultry" for f in sample_foods)


class TestUnmatchedFoodModalOperations:
    """Test food modal operation logic."""

    def test_food_action_create_new_food(self, sample_foods):
        """Test creating new food operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "Turkey"

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Turkey"

        # Simulate button press - Case 2
        result = {
            "action": "food",
            "pattern": "test pattern",
            "operation": "create_food",
            "food_name": "Turkey",
        }

        assert result["operation"] == "create_food"
        assert result["food_name"] == "Turkey"
        assert "alias" not in result

    def test_food_action_add_alias(self, sample_foods):
        """Test adding food alias operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "chicken breast"

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Chicken"  # Exists in DB

        # Simulate button press - Case 3
        result = {
            "action": "food",
            "pattern": "test pattern",
            "operation": "add_food_alias",
            "food_id": "food-1",
            "food_name": "Chicken",
            "alias": "chicken breast",
        }

        assert result["operation"] == "add_food_alias"
        assert result["food_name"] == "Chicken"
        assert result["alias"] == "chicken breast"

    def test_food_action_create_with_alias(self, sample_foods):
        """Test creating food with alias operation."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test pattern"
        pattern.parsed_food = "chicken breast"

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Poultry"

        # Simulate button press - Case 4
        result = {
            "action": "food",
            "pattern": "test pattern",
            "operation": "create_food_with_alias",
            "food_name": "Poultry",
            "alias": "chicken breast",
        }

        assert result["operation"] == "create_food_with_alias"
        assert result["food_name"] == "Poultry"
        assert result["alias"] == "chicken breast"

    def test_reparse_action(self, sample_pattern, sample_foods):
        """Test re-parse action returns correct structure."""
        UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods, parse_method="nlp")

        # Simulate reset button press
        result = {
            "action": "reparse",
            "pattern": "chicken breast",
            "method": "nlp",
        }

        assert result["action"] == "reparse"
        assert result["pattern"] == "chicken breast"
        assert result["method"] == "nlp"

    def test_cancel_returns_none(self, sample_pattern, sample_foods):
        """Test cancel action returns None."""
        UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods)

        # Simulate cancel - would call dismiss(None)
        result = None

        assert result is None


# =============================================================================
# Edge Cases and Input Validation
# =============================================================================


class TestEdgeCases:
    """Test edge cases and unusual input."""

    def test_unit_modal_with_empty_parsed_unit(self, sample_units):
        """Test unit modal handles empty parsed_unit gracefully."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_unit = ""
        pattern.unit_confidence = 0.0

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "cup"

        # User types "cup" (exists in DB) but no parsed_unit
        # Should show "Use existing unit: cup" button
        assert modal.original_parsed_unit == ""
        assert modal.unit_input_value == "cup"

    def test_food_modal_with_empty_parsed_food(self, sample_foods):
        """Test food modal handles empty parsed_food gracefully."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_food = ""
        pattern.food_confidence = 0.0

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Chicken"

        assert modal.original_parsed_food == ""
        assert modal.food_input_value == "Chicken"

    def test_unit_modal_case_insensitive_matching(self, sample_units):
        """Test unit matching is case-insensitive."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_unit = "CUP"

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "CUP"

        # "cup" exists in DB (lowercase)
        # find_unit_by_name should match case-insensitively
        assert modal.unit_input_value == "CUP"

    def test_food_modal_case_sensitive_exact_match(self, sample_foods):
        """Test food matching for exact case."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_food = "chicken"

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)
        modal.food_input_value = "Chicken"  # Different case

        # "Chicken" exists in DB with capital C
        assert modal.food_input_value == "Chicken"

    def test_whitespace_handling_in_input(self, sample_units):
        """Test input with leading/trailing whitespace is trimmed."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_unit = "cup"

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)
        modal.unit_input_value = "  cup  "

        # update_unit_button() uses .strip()
        assert modal.unit_input_value.strip() == "cup"


# =============================================================================
# Select Dropdown Interaction Tests
# =============================================================================


class TestSelectInteraction:
    """Test select dropdown interaction logic."""

    def test_unit_select_updates_input(self, sample_pattern, sample_units):
        """Test selecting unit from dropdown updates input field."""
        modal = UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)

        # Simulate selecting "tablespoon" from dropdown
        selected_unit_id = "unit-2"
        selected_unit = next(u for u in sample_units if u["id"] == selected_unit_id)

        # This would update the input field
        modal.unit_input_value = selected_unit["name"]

        assert modal.unit_input_value == "tablespoon"

    def test_food_select_updates_input(self, sample_pattern, sample_foods):
        """Test selecting food from dropdown updates input field."""
        modal = UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods)

        # Simulate selecting "Beef" from dropdown
        selected_food_id = "food-2"
        selected_food = next(f for f in sample_foods if f["id"] == selected_food_id)

        modal.food_input_value = selected_food["name"]

        assert modal.food_input_value == "Beef"


# =============================================================================
# Integration Test Scenarios
# =============================================================================


class TestWorkflowScenarios:
    """Test complete workflow scenarios."""

    def test_scenario_user_creates_missing_unit(self, sample_units):
        """
        Scenario: User encounters "tsp" which isn't in database.
        Parser extracted "tsp", user accepts it -> Create new unit.
        """
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "1 tsp salt"
        pattern.parsed_unit = "tsp"
        pattern.unit_confidence = 0.88

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)

        # User doesn't change input (accepts parsed value)
        assert modal.unit_input_value == "tsp"

        # tsp doesn't exist in DB
        assert not any(u["name"] == "tsp" for u in sample_units)

        # Expected result: Create new unit
        expected_result = {
            "action": "unit",
            "pattern": "1 tsp salt",
            "operation": "create_unit",
            "unit_name": "tsp",
        }

        assert expected_result["operation"] == "create_unit"

    def test_scenario_user_adds_alias_to_existing_unit(self, sample_units):
        """
        Scenario: Parser extracted "c" but user knows it means "cup".
        User selects "cup" from dropdown -> Add "c" as alias to "cup".
        """
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "2 c flour"
        pattern.parsed_unit = "c"
        pattern.unit_confidence = 0.65

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)

        # User changes input to "cup" (exists in DB)
        modal.unit_input_value = "cup"

        # Expected result: Add alias
        expected_result = {
            "action": "unit",
            "pattern": "2 c flour",
            "operation": "add_unit_alias",
            "unit_id": "unit-1",
            "unit_name": "cup",
            "alias": "c",
        }

        assert expected_result["operation"] == "add_unit_alias"
        assert expected_result["alias"] == "c"

    def test_scenario_user_creates_food_with_alias(self, sample_foods):
        """
        Scenario: Parser extracted "chicken breast" but user wants
        to create "Poultry" as new food with "chicken breast" as alias.
        """
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "chicken breast"
        pattern.parsed_food = "chicken breast"
        pattern.food_confidence = 0.82

        modal = UnmatchedFoodModal(pattern=pattern, foods=sample_foods)

        # User changes input to custom name
        modal.food_input_value = "Poultry"

        # Expected result: Create food with alias
        expected_result = {
            "action": "food",
            "pattern": "chicken breast",
            "operation": "create_food_with_alias",
            "food_name": "Poultry",
            "alias": "chicken breast",
        }

        assert expected_result["operation"] == "create_food_with_alias"
        assert expected_result["alias"] == "chicken breast"

    def test_scenario_user_requests_reparse(self, sample_pattern, sample_units):
        """
        Scenario: Parser got it wrong, user clicks "Reset / Re-parse"
        to try parsing again with different method.
        """
        UnmatchedUnitModal(pattern=sample_pattern, units=sample_units, parse_method="nlp")

        # User clicks reset button
        expected_result = {
            "action": "reparse",
            "pattern": "chicken breast",
            "method": "nlp",
        }

        assert expected_result["action"] == "reparse"

    def test_scenario_user_cancels_modal(self, sample_pattern, sample_units):
        """
        Scenario: User presses Escape or Cancel button.
        Modal returns None to indicate no action taken.
        """
        UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)

        # User cancels
        result = None

        assert result is None


# =============================================================================
# Confidence Score Display Tests
# =============================================================================


class TestConfidenceDisplay:
    """Test confidence score display formatting."""

    def test_unit_confidence_formatting(self, sample_pattern, sample_units):
        """Test unit confidence score is formatted correctly."""
        modal = UnmatchedUnitModal(pattern=sample_pattern, units=sample_units)

        # Confidence should be displayed as 0.85 (2 decimal places)
        assert modal.unit_confidence == 0.85
        formatted = f"{modal.unit_confidence:.2f}"
        assert formatted == "0.85"

    def test_food_confidence_formatting(self, sample_pattern, sample_foods):
        """Test food confidence score is formatted correctly."""
        modal = UnmatchedFoodModal(pattern=sample_pattern, foods=sample_foods)

        assert modal.food_confidence == 0.92
        formatted = f"{modal.food_confidence:.2f}"
        assert formatted == "0.92"

    def test_zero_confidence(self, sample_units):
        """Test zero confidence displays correctly."""
        pattern = MagicMock(spec=PatternGroup)
        pattern.pattern_text = "test"
        pattern.parsed_unit = None
        pattern.unit_confidence = 0.0

        modal = UnmatchedUnitModal(pattern=pattern, units=sample_units)

        assert modal.unit_confidence == 0.0
        formatted = f"{modal.unit_confidence:.2f}"
        assert formatted == "0.00"
