"""Unit tests for PatternGroup data model."""

from __future__ import annotations

import pytest

from mealie_parser.models.pattern import PatternGroup


class TestPatternGroupCreation:
    """Test PatternGroup creation and initialization."""

    def test_create_pattern_group_with_valid_data(self):
        """Test creating PatternGroup with all valid fields."""
        # Arrange & Act
        pattern = PatternGroup(
            pattern_text="tsp",
            ingredient_ids=["ing-1", "ing-2"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["teaspoon", "t"],
            operation_status="pending",
        )

        # Assert
        assert pattern.pattern_text == "tsp"
        assert pattern.ingredient_ids == ["ing-1", "ing-2"]
        assert pattern.recipe_ids == ["recipe-1"]
        assert pattern.suggested_similar_patterns == ["teaspoon", "t"]
        assert pattern.operation_status == "pending"

    def test_create_pattern_group_with_defaults(self):
        """Test creating PatternGroup with only required field."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="flour")

        # Assert
        assert pattern.pattern_text == "flour"
        assert pattern.ingredient_ids == []
        assert pattern.recipe_ids == []
        assert pattern.suggested_similar_patterns == []
        assert pattern.operation_status == "pending"

    def test_pattern_text_is_trimmed(self):
        """Test that pattern_text is automatically trimmed."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="  tsp  ")

        # Assert
        assert pattern.pattern_text == "tsp"

    def test_empty_pattern_text_raises_error(self):
        """Test that empty pattern_text raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="pattern_text must not be empty"):
            PatternGroup(pattern_text="")

    def test_whitespace_only_pattern_text_raises_error(self):
        """Test that whitespace-only pattern_text raises ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="pattern_text must not be empty"):
            PatternGroup(pattern_text="   ")


class TestPatternGroupSerialization:
    """Test PatternGroup serialization methods."""

    def test_to_dict(self):
        """Test serialization to dictionary."""
        # Arrange
        pattern = PatternGroup(
            pattern_text="cup",
            ingredient_ids=["ing-1"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["c"],
            operation_status="completed",
        )

        # Act
        result = pattern.to_dict()

        # Assert
        assert result == {
            "pattern_text": "cup",
            "ingredient_ids": ["ing-1"],
            "recipe_ids": ["recipe-1"],
            "suggested_similar_patterns": ["c"],
            "operation_status": "completed",
        }

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        # Arrange
        data = {
            "pattern_text": "tbsp",
            "ingredient_ids": ["ing-1", "ing-2"],
            "recipe_ids": ["recipe-1", "recipe-2"],
            "suggested_similar_patterns": ["tablespoon"],
            "operation_status": "processing",
        }

        # Act
        pattern = PatternGroup.from_dict(data)

        # Assert
        assert pattern.pattern_text == "tbsp"
        assert pattern.ingredient_ids == ["ing-1", "ing-2"]
        assert pattern.recipe_ids == ["recipe-1", "recipe-2"]
        assert pattern.suggested_similar_patterns == ["tablespoon"]
        assert pattern.operation_status == "processing"

    def test_from_dict_with_minimal_data(self):
        """Test deserialization with only required field."""
        # Arrange
        data = {"pattern_text": "salt"}

        # Act
        pattern = PatternGroup.from_dict(data)

        # Assert
        assert pattern.pattern_text == "salt"
        assert pattern.ingredient_ids == []
        assert pattern.recipe_ids == []
        assert pattern.suggested_similar_patterns == []
        assert pattern.operation_status == "pending"

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are reversible."""
        # Arrange
        original = PatternGroup(
            pattern_text="onion",
            ingredient_ids=["ing-1", "ing-2", "ing-3"],
            recipe_ids=["recipe-1"],
            suggested_similar_patterns=["yellow onion", "white onion"],
            operation_status="skipped",
        )

        # Act
        serialized = original.to_dict()
        deserialized = PatternGroup.from_dict(serialized)

        # Assert
        assert deserialized.pattern_text == original.pattern_text
        assert deserialized.ingredient_ids == original.ingredient_ids
        assert deserialized.recipe_ids == original.recipe_ids
        assert deserialized.suggested_similar_patterns == original.suggested_similar_patterns
        assert deserialized.operation_status == original.operation_status


class TestPatternGroupEdgeCases:
    """Test PatternGroup with edge case inputs."""

    def test_unicode_characters(self):
        """Test pattern_text with Unicode characters."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="jalapeño")

        # Assert
        assert pattern.pattern_text == "jalapeño"

    def test_special_characters(self):
        """Test pattern_text with special characters."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="café-style")

        # Assert
        assert pattern.pattern_text == "café-style"

    def test_very_long_pattern_text(self):
        """Test pattern_text with very long string."""
        # Arrange
        long_text = "a" * 1000

        # Act
        pattern = PatternGroup(pattern_text=long_text)

        # Assert
        assert pattern.pattern_text == long_text
        assert len(pattern.pattern_text) == 1000

    def test_pattern_with_numbers(self):
        """Test pattern_text containing numbers."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="1/2 cup")

        # Assert
        assert pattern.pattern_text == "1/2 cup"

    def test_pattern_with_mixed_whitespace(self):
        """Test pattern_text with tabs and newlines is trimmed."""
        # Arrange & Act
        pattern = PatternGroup(pattern_text="\t\ntsp\n\t")

        # Assert
        assert pattern.pattern_text == "tsp"
