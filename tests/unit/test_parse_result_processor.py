"""Tests for parse result processor utilities."""

from mealie_parser.models import PatternStatus
from mealie_parser.models.pattern import PatternGroup
from mealie_parser.services.parse_result_processor import (
    check_food_match,
    check_unit_match,
    extract_confidence_scores,
    extract_parsed_food,
    extract_parsed_unit,
    get_matched_food_id,
    get_matched_unit_id,
    update_pattern_from_parse_result,
)


class TestExtractParsedUnit:
    """Tests for extract_parsed_unit function."""

    def test_extract_unit_from_dict(self):
        """Test extracting unit name from dict format."""
        ingredient = {"unit": {"name": "cup", "id": "123"}}
        assert extract_parsed_unit(ingredient) == "cup"

    def test_extract_unit_from_string(self):
        """Test extracting unit name from string format."""
        ingredient = {"unit": "tablespoon"}
        assert extract_parsed_unit(ingredient) == "tablespoon"

    def test_extract_unit_missing(self):
        """Test extracting unit when not present."""
        ingredient = {"food": "salt"}
        assert extract_parsed_unit(ingredient) == ""

    def test_extract_unit_empty_dict(self):
        """Test extracting unit from empty dict."""
        ingredient = {"unit": {}}
        assert extract_parsed_unit(ingredient) == ""


class TestExtractParsedFood:
    """Tests for extract_parsed_food function."""

    def test_extract_food_from_dict(self):
        """Test extracting food name from dict format."""
        ingredient = {"food": {"name": "tomato", "id": "456"}}
        assert extract_parsed_food(ingredient) == "tomato"

    def test_extract_food_from_string(self):
        """Test extracting food name from string format."""
        ingredient = {"food": "onion"}
        assert extract_parsed_food(ingredient) == "onion"

    def test_extract_food_missing(self):
        """Test extracting food when not present."""
        ingredient = {"unit": "cup"}
        assert extract_parsed_food(ingredient) == ""

    def test_extract_food_empty_dict(self):
        """Test extracting food from empty dict."""
        ingredient = {"food": {}}
        assert extract_parsed_food(ingredient) == ""


class TestExtractConfidenceScores:
    """Tests for extract_confidence_scores function."""

    def test_extract_confidence_dict_format(self):
        """Test extracting confidence from dict with unit and food fields."""
        parse_result = {"confidence": {"unit": 0.95, "food": 0.85}}
        unit_conf, food_conf = extract_confidence_scores(parse_result)
        assert unit_conf == 0.95
        assert food_conf == 0.85

    def test_extract_confidence_with_average(self):
        """Test extracting confidence using average when specific fields missing."""
        parse_result = {"confidence": {"average": 0.9}}
        unit_conf, food_conf = extract_confidence_scores(parse_result)
        assert unit_conf == 0.9
        assert food_conf == 0.9

    def test_extract_confidence_single_value(self):
        """Test extracting confidence from single numeric value."""
        parse_result = {"confidence": 0.8}
        unit_conf, food_conf = extract_confidence_scores(parse_result)
        assert unit_conf == 0.8
        assert food_conf == 0.8

    def test_extract_confidence_missing(self):
        """Test extracting confidence when not present."""
        parse_result = {}
        unit_conf, food_conf = extract_confidence_scores(parse_result)
        assert unit_conf == 0.0
        assert food_conf == 0.0


class TestCheckUnitMatch:
    """Tests for check_unit_match function."""

    def test_match_found_exact(self):
        """Test finding exact unit match."""
        known_units = [{"name": "cup", "id": "1"}, {"name": "tablespoon", "id": "2"}]
        assert check_unit_match("cup", known_units) is True

    def test_match_found_case_insensitive(self):
        """Test finding unit match with different case."""
        known_units = [{"name": "Cup", "id": "1"}]
        assert check_unit_match("cup", known_units) is True

    def test_match_not_found(self):
        """Test when unit not in known units."""
        known_units = [{"name": "cup", "id": "1"}]
        assert check_unit_match("liter", known_units) is False

    def test_match_empty_string(self):
        """Test with empty unit name."""
        known_units = [{"name": "cup", "id": "1"}]
        assert check_unit_match("", known_units) is False


class TestCheckFoodMatch:
    """Tests for check_food_match function."""

    def test_match_found_exact(self):
        """Test finding exact food match."""
        known_foods = [{"name": "tomato", "id": "1"}, {"name": "onion", "id": "2"}]
        assert check_food_match("tomato", known_foods) is True

    def test_match_found_case_insensitive(self):
        """Test finding food match with different case."""
        known_foods = [{"name": "Tomato", "id": "1"}]
        assert check_food_match("tomato", known_foods) is True

    def test_match_not_found(self):
        """Test when food not in known foods."""
        known_foods = [{"name": "tomato", "id": "1"}]
        assert check_food_match("potato", known_foods) is False

    def test_match_empty_string(self):
        """Test with empty food name."""
        known_foods = [{"name": "tomato", "id": "1"}]
        assert check_food_match("", known_foods) is False


class TestGetMatchedIds:
    """Tests for get_matched_unit_id and get_matched_food_id functions."""

    def test_get_matched_unit_id(self):
        """Test getting unit ID for matched unit."""
        known_units = [{"name": "cup", "id": "unit-123"}]
        assert get_matched_unit_id("cup", known_units) == "unit-123"

    def test_get_matched_unit_id_not_found(self):
        """Test getting unit ID when not matched."""
        known_units = [{"name": "cup", "id": "unit-123"}]
        assert get_matched_unit_id("liter", known_units) is None

    def test_get_matched_food_id(self):
        """Test getting food ID for matched food."""
        known_foods = [{"name": "tomato", "id": "food-456"}]
        assert get_matched_food_id("tomato", known_foods) == "food-456"

    def test_get_matched_food_id_not_found(self):
        """Test getting food ID when not matched."""
        known_foods = [{"name": "tomato", "id": "food-456"}]
        assert get_matched_food_id("potato", known_foods) is None


class TestUpdatePatternFromParseResult:
    """Tests for update_pattern_from_parse_result function."""

    def test_update_pattern_with_matched_unit_and_food(self):
        """Test updating pattern when both unit and food match."""
        pattern = PatternGroup(
            pattern_text="1 cup tomato",
            ingredient_ids=["ing-1"],
            recipe_ids=["rec-1"],
        )
        parse_result = {
            "ingredient": {"unit": "cup", "food": "tomato"},
            "confidence": {"unit": 0.95, "food": 0.90},
        }
        known_units = [{"name": "cup", "id": "unit-1"}]
        known_foods = [{"name": "tomato", "id": "food-1"}]

        update_pattern_from_parse_result(pattern, parse_result, known_units, known_foods)

        assert pattern.parsed_unit == "cup"
        assert pattern.parsed_food == "tomato"
        assert pattern.unit_confidence == 0.95
        assert pattern.food_confidence == 0.90
        assert pattern.unit_status == PatternStatus.MATCHED
        assert pattern.food_status == PatternStatus.MATCHED
        assert pattern.matched_unit_id == "unit-1"
        assert pattern.matched_food_id == "food-1"

    def test_update_pattern_with_unmatched_unit_and_food(self):
        """Test updating pattern when neither unit nor food match."""
        pattern = PatternGroup(
            pattern_text="1 liter potato",
            ingredient_ids=["ing-1"],
            recipe_ids=["rec-1"],
        )
        parse_result = {
            "ingredient": {"unit": "liter", "food": "potato"},
            "confidence": 0.8,
        }
        known_units = [{"name": "cup", "id": "unit-1"}]
        known_foods = [{"name": "tomato", "id": "food-1"}]

        update_pattern_from_parse_result(pattern, parse_result, known_units, known_foods)

        assert pattern.parsed_unit == "liter"
        assert pattern.parsed_food == "potato"
        assert pattern.unit_status == PatternStatus.UNMATCHED
        assert pattern.food_status == PatternStatus.UNMATCHED

    def test_update_pattern_with_empty_parse_result(self):
        """Test updating pattern when parse result has no unit/food."""
        pattern = PatternGroup(
            pattern_text="some ingredient",
            ingredient_ids=["ing-1"],
            recipe_ids=["rec-1"],
        )
        parse_result = {"ingredient": {}, "confidence": {}}
        known_units = []
        known_foods = []

        update_pattern_from_parse_result(pattern, parse_result, known_units, known_foods)

        assert pattern.parsed_unit == ""
        assert pattern.parsed_food == ""
        assert pattern.unit_status == PatternStatus.UNMATCHED
        assert pattern.food_status == PatternStatus.UNMATCHED

    def test_update_pattern_transitions_through_parsing_state(self):
        """Test that pattern transitions through PARSING state."""
        pattern = PatternGroup(
            pattern_text="1 cup tomato",
            ingredient_ids=["ing-1"],
            recipe_ids=["rec-1"],
        )
        # Ensure starting status is PENDING
        assert pattern.unit_status == PatternStatus.PENDING
        assert pattern.food_status == PatternStatus.PENDING

        parse_result = {
            "ingredient": {"unit": "cup", "food": "tomato"},
            "confidence": 0.9,
        }
        known_units = [{"name": "cup", "id": "unit-1"}]
        known_foods = [{"name": "tomato", "id": "food-1"}]

        update_pattern_from_parse_result(pattern, parse_result, known_units, known_foods)

        # Should end in MATCHED (having transitioned through PARSING)
        assert pattern.unit_status == PatternStatus.MATCHED
        assert pattern.food_status == PatternStatus.MATCHED
