"""Unit tests for validation utilities."""

from mealie_parser.validation import (
    MAX_ABBREVIATION_LENGTH,
    MAX_NAME_LENGTH,
    ValidationResult,
    check_disallowed_chars,
    check_duplicate_name,
    validate_abbreviation,
    validate_api_response,
    validate_food_name,
    validate_ingredient_ids,
    validate_pattern_text,
    validate_unit_name,
)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_create_valid_result(self):
        """Test creating valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error(self):
        """Test adding error sets is_valid to False."""
        result = ValidationResult(is_valid=True)
        result.add_error("Test error")
        assert result.is_valid is False
        assert "Test error" in result.errors

    def test_add_warning(self):
        """Test adding warning doesn't affect validity."""
        result = ValidationResult(is_valid=True)
        result.add_warning("Test warning")
        assert result.is_valid is True
        assert "Test warning" in result.warnings


class TestHelperFunctions:
    """Tests for validation helper functions."""

    def test_check_disallowed_chars_found(self):
        """Test detecting disallowed characters."""
        found = check_disallowed_chars("test<script>")
        assert "<" in found
        assert ">" in found

    def test_check_disallowed_chars_none(self):
        """Test no disallowed characters found."""
        found = check_disallowed_chars("clean name")
        assert found == []

    def test_check_duplicate_name_found(self):
        """Test detecting duplicate name (case-insensitive)."""
        existing = [{"name": "Teaspoon"}, {"name": "Tablespoon"}]
        assert check_duplicate_name("teaspoon", existing) is True
        assert check_duplicate_name("TEASPOON", existing) is True

    def test_check_duplicate_name_not_found(self):
        """Test no duplicate found."""
        existing = [{"name": "Teaspoon"}]
        assert check_duplicate_name("tablespoon", existing) is False


class TestValidateUnitName:
    """Tests for validate_unit_name function."""

    def test_valid_unit_name(self):
        """Test valid unit name passes."""
        result = validate_unit_name("teaspoon", [])
        assert result.is_valid is True
        assert result.errors == []

    def test_empty_name_fails(self):
        """Test empty name fails validation."""
        result = validate_unit_name("", [])
        assert result.is_valid is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_whitespace_only_fails(self):
        """Test whitespace-only name fails."""
        result = validate_unit_name("   ", [])
        assert result.is_valid is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_max_length_fails(self):
        """Test name exceeding max length fails."""
        long_name = "a" * (MAX_NAME_LENGTH + 1)
        result = validate_unit_name(long_name, [])
        assert result.is_valid is False
        assert any("exceed" in err.lower() for err in result.errors)

    def test_disallowed_chars_fail(self):
        """Test disallowed characters fail."""
        result = validate_unit_name("test<script>", [])
        assert result.is_valid is False
        assert any("cannot contain" in err.lower() for err in result.errors)

    def test_duplicate_name_fails(self):
        """Test duplicate name fails."""
        existing = [{"name": "teaspoon"}]
        result = validate_unit_name("Teaspoon", existing)
        assert result.is_valid is False
        assert any("already exists" in err.lower() for err in result.errors)

    def test_valid_characters_pass(self):
        """Test valid character patterns pass."""
        valid_names = ["tsp", "cup-metric", "fl_oz", "lb(s)", "piece"]
        for name in valid_names:
            result = validate_unit_name(name, [])
            assert result.is_valid is True, f"'{name}' should be valid"


class TestValidateFoodName:
    """Tests for validate_food_name function."""

    def test_valid_food_name(self):
        """Test valid food name passes."""
        result = validate_food_name("chicken breast", [])
        assert result.is_valid is True
        assert result.errors == []

    def test_empty_name_fails(self):
        """Test empty name fails validation."""
        result = validate_food_name("", [])
        assert result.is_valid is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_max_length_fails(self):
        """Test name exceeding max length fails."""
        long_name = "a" * (MAX_NAME_LENGTH + 1)
        result = validate_food_name(long_name, [])
        assert result.is_valid is False
        assert any("exceed" in err.lower() for err in result.errors)

    def test_disallowed_chars_fail(self):
        """Test disallowed characters fail."""
        result = validate_food_name("test&food", [])
        assert result.is_valid is False
        assert any("cannot contain" in err.lower() for err in result.errors)

    def test_duplicate_name_fails(self):
        """Test duplicate name fails."""
        existing = [{"name": "chicken"}]
        result = validate_food_name("Chicken", existing)
        assert result.is_valid is False
        assert any("already exists" in err.lower() for err in result.errors)

    def test_apostrophes_allowed(self):
        """Test apostrophes are allowed in food names."""
        result = validate_food_name("chef's choice", [])
        assert result.is_valid is True


class TestValidateAbbreviation:
    """Tests for validate_abbreviation function."""

    def test_empty_abbreviation_passes(self):
        """Test empty abbreviation is valid (optional field)."""
        result = validate_abbreviation("")
        assert result.is_valid is True

    def test_valid_abbreviation_passes(self):
        """Test valid abbreviations pass."""
        valid_abbrs = ["tsp", "tbsp", "lb", "oz", "ml"]
        for abbr in valid_abbrs:
            result = validate_abbreviation(abbr)
            assert result.is_valid is True, f"'{abbr}' should be valid"

    def test_max_length_fails(self):
        """Test abbreviation exceeding max length fails."""
        long_abbr = "a" * (MAX_ABBREVIATION_LENGTH + 1)
        result = validate_abbreviation(long_abbr)
        assert result.is_valid is False
        assert any("exceed" in err.lower() for err in result.errors)

    def test_spaces_not_allowed(self):
        """Test spaces not allowed in abbreviations."""
        result = validate_abbreviation("t sp")
        assert result.is_valid is False
        assert any("space" in err.lower() for err in result.errors)

    def test_disallowed_chars_fail(self):
        """Test disallowed characters fail."""
        result = validate_abbreviation("tsp<")
        assert result.is_valid is False
        assert any("cannot contain" in err.lower() for err in result.errors)


class TestValidatePatternText:
    """Tests for validate_pattern_text function."""

    def test_valid_pattern_passes(self):
        """Test valid pattern text passes."""
        result = validate_pattern_text("tsp")
        assert result.is_valid is True

    def test_empty_pattern_fails(self):
        """Test empty pattern fails."""
        result = validate_pattern_text("")
        assert result.is_valid is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_whitespace_only_fails(self):
        """Test whitespace-only pattern fails."""
        result = validate_pattern_text("   ")
        assert result.is_valid is False
        assert any("empty" in err.lower() for err in result.errors)

    def test_unnormalized_pattern_warning(self):
        """Test unnormalized pattern generates warning."""
        result = validate_pattern_text("TSP ")  # Not trimmed/lowercase
        assert len(result.warnings) > 0
        assert any("normalized" in warn.lower() for warn in result.warnings)


class TestValidateIngredientIds:
    """Tests for validate_ingredient_ids function."""

    def test_valid_ids_pass(self):
        """Test valid ingredient IDs pass."""
        recipes = [
            {"recipeIngredient": [{"id": "id1"}, {"id": "id2"}]},
            {"recipeIngredient": [{"id": "id3"}]},
        ]
        result = validate_ingredient_ids(["id1", "id2", "id3"], recipes)
        assert result.is_valid is True

    def test_invalid_ids_fail(self):
        """Test invalid ingredient IDs fail."""
        recipes = [{"recipeIngredient": [{"id": "id1"}]}]
        result = validate_ingredient_ids(["id1", "id2", "id3"], recipes)
        assert result.is_valid is False
        assert any("invalid" in err.lower() for err in result.errors)

    def test_empty_recipes_all_invalid(self):
        """Test empty recipes list makes all IDs invalid."""
        result = validate_ingredient_ids(["id1", "id2"], [])
        assert result.is_valid is False

    def test_many_invalid_ids_truncated(self):
        """Test many invalid IDs are truncated in error message."""
        recipes = []
        invalid_ids = [f"id{i}" for i in range(20)]
        result = validate_ingredient_ids(invalid_ids, recipes)
        assert result.is_valid is False
        # Should mention truncation
        assert any("more" in err.lower() for err in result.errors)


class TestValidateApiResponse:
    """Tests for validate_api_response function."""

    def test_valid_response_passes(self):
        """Test valid API response passes."""
        response = {"id": "123", "name": "test"}
        result = validate_api_response(response, ["id", "name"])
        assert result.is_valid is True

    def test_missing_fields_fail(self):
        """Test missing fields fail validation."""
        response = {"id": "123"}
        result = validate_api_response(response, ["id", "name", "description"])
        assert result.is_valid is False
        assert any("missing" in err.lower() for err in result.errors)
        assert any("name" in err.lower() for err in result.errors)

    def test_empty_response_fails(self):
        """Test empty response fails when fields expected."""
        response = {}
        result = validate_api_response(response, ["id", "name"])
        assert result.is_valid is False


class TestEdgeCases:
    """Tests for edge cases and special characters."""

    def test_unicode_characters_in_names(self):
        """Test Unicode characters in names."""
        # These should pass if they match the pattern
        result = validate_unit_name("café", [])
        # Pattern only allows ASCII, so this should fail
        assert result.is_valid is False

    def test_special_characters_in_names(self):
        """Test special characters in names."""
        result = validate_unit_name("test!@#", [])
        assert result.is_valid is False

    def test_very_long_pattern_text(self):
        """Test very long pattern text."""
        long_pattern = "a" * 1000
        result = validate_pattern_text(long_pattern)
        # Should pass (no max length on patterns)
        assert result.is_valid is True

    def test_numbers_in_names(self):
        """Test numbers in names."""
        result = validate_unit_name("piece123", [])
        assert result.is_valid is True

    def test_mixed_whitespace_in_names(self):
        """Test mixed whitespace in names."""
        result = validate_unit_name("  mixed   spaces  ", [])
        # Should pass after trimming check
        assert result.is_valid is True
